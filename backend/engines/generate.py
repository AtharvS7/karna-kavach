"""
Generate Engine: produces synthetic fraud + legitimate transactions using
Faker for base data and LLM-derived attack features for fraud injection.
"""
import json
import csv
import uuid
import random
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from faker import Faker

logger = logging.getLogger(__name__)
fake = Faker()

# Realistic merchant distribution by category
MCC_MAP = {
    "retail":        ("Retail Store", 5411),
    "grocery":       ("Grocery", 5411),
    "gas_station":   ("Gas Station", 5541),
    "restaurant":    ("Restaurant", 5812),
    "electronics":   ("Electronics", 5732),
    "travel":        ("Airline/Hotel", 4511),
    "entertainment": ("Entertainment", 7922),
    "atm":           ("ATM Withdrawal", 6011),
    "online":        ("Online Retailer", 5999),
    "pharmacy":      ("Pharmacy", 5912),
}

# Amount distributions per merchant category (mean, std)
AMOUNT_DIST = {
    "retail":        (85,  60),
    "grocery":       (65,  40),
    "gas_station":   (55,  20),
    "restaurant":    (35,  25),
    "electronics":   (350, 250),
    "travel":        (420, 300),
    "entertainment": (70,  50),
    "atm":           (200, 100),
    "online":        (120, 90),
    "pharmacy":      (45,  30),
}


def _realistic_amount(category: str, override_range: Optional[List] = None) -> float:
    if override_range:
        return round(random.uniform(override_range[0], override_range[1]), 2)
    mean, std = AMOUNT_DIST.get(category, (100, 80))
    amount = max(1.0, random.gauss(mean, std))
    return round(amount, 2)


def _make_transaction(
    is_fraud: bool,
    attack: Optional[Dict] = None,
    card_id: Optional[str] = None,
    base_time: Optional[datetime] = None,
    velocity_index: int = 0,
) -> Dict:
    """Build one synthetic transaction record."""
    cat_key = random.choice(list(MCC_MAP.keys()))
    merchant_name, mcc = MCC_MAP[cat_key]

    features = attack.get("transaction_features", {}) if attack else {}

    # Override category from attack features when present
    if features.get("merchant_category"):
        cat_key = features["merchant_category"] if features["merchant_category"] in MCC_MAP else cat_key
        merchant_name, mcc = MCC_MAP[cat_key]

    amount = _realistic_amount(cat_key, features.get("amount_range"))

    # Timestamp: velocity spike = many txns close together
    base = base_time or datetime.now() - timedelta(days=random.randint(0, 30))
    if features.get("velocity_spike") and velocity_index > 0:
        ts = base + timedelta(minutes=velocity_index * random.randint(1, 5))
    else:
        ts = base - timedelta(
            hours=random.randint(0, 72),
            minutes=random.randint(0, 59)
        )

    # Geography
    if features.get("geographic_anomaly") and is_fraud:
        country = random.choice(["NG", "RO", "UA", "PH", "BR", "VN"])
        city = fake.city()
        state = ""
    else:
        country = "US"
        city = fake.city()
        state = fake.state_abbr()

    return {
        "transaction_id": f"TXN-{uuid.uuid4().hex[:12].upper()}",
        "card_id": card_id or f"CARD-{uuid.uuid4().hex[:8].upper()}",
        "merchant_name": f"{merchant_name} #{random.randint(100, 9999)}",
        "merchant_category": cat_key,
        "mcc": mcc,
        "amount": amount,
        "currency": "USD",
        "timestamp": ts.isoformat(),
        "city": city,
        "state": state,
        "country": country,
        "card_present": features.get("card_present", not is_fraud),
        "is_fraud": int(is_fraud),
        "attack_id": attack["attack_id"] if attack else None,
    }


class GenerateEngine:
    """
    Generates:
      - 10 000 legitimate transactions across 500 synthetic cardholders
      - ~5 000 fraud transactions spread across all taxonomy attacks
    """

    def __init__(self):
        project_root = Path(__file__).parent.parent.parent
        self.taxonomy_path = project_root / "data" / "attack_taxonomy.json"
        self.output_dir = project_root / "data" / "synthetic_transactions"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.output_path = self.output_dir / "transactions.csv"

    def _load_taxonomy(self) -> List[Dict]:
        if not self.taxonomy_path.exists():
            raise FileNotFoundError(
                "attack_taxonomy.json not found — run IdentifyEngine.run() first"
            )
        with open(self.taxonomy_path) as f:
            return json.load(f)

    def _generate_legitimate(self, n: int = 10_000) -> List[Dict]:
        logger.info(f"Generating {n} legitimate transactions...")
        # 500 cardholders, each with ~20 transactions
        card_ids = [f"CARD-{uuid.uuid4().hex[:8].upper()}" for _ in range(500)]
        rows = []
        for _ in range(n):
            card_id = random.choice(card_ids)
            rows.append(_make_transaction(is_fraud=False, card_id=card_id))
        return rows

    def _generate_fraud(self, attacks: List[Dict]) -> List[Dict]:
        """~150 fraud transactions per attack."""
        rows = []
        for attack in attacks:
            card_id = f"CARD-{uuid.uuid4().hex[:8].upper()}"
            base_time = datetime.now() - timedelta(days=random.randint(1, 30))
            n = random.randint(130, 170)
            for i in range(n):
                rows.append(_make_transaction(
                    is_fraud=True,
                    attack=attack,
                    card_id=card_id,
                    base_time=base_time,
                    velocity_index=i,
                ))
        return rows

    def _add_engineered_features(self, rows: List[Dict]) -> List[Dict]:
        """
        Add velocity and deviation features that the ML model will learn from.
        ponytail: simple look-back over sorted list; replace with pandas groupby
        when dataset grows beyond 100k rows.
        """
        by_card: Dict[str, List[Dict]] = {}
        for r in rows:
            by_card.setdefault(r["card_id"], []).append(r)

        for card_rows in by_card.values():
            card_rows.sort(key=lambda x: x["timestamp"])
            amounts = [r["amount"] for r in card_rows]
            avg_amount = sum(amounts) / len(amounts)

            for idx, r in enumerate(card_rows):
                # transactions in last 1h window (approximated by index proximity)
                window = max(0, idx - 10)
                r["velocity_1h"] = idx - window
                r["amount_deviation"] = abs(r["amount"] - avg_amount) / max(avg_amount, 1)
                r["cross_border"] = int(r["country"] != "US")
                r["txn_index"] = idx

        return rows

    def run(self, force: bool = False) -> Path:
        """Generate full synthetic dataset, saving to CSV."""
        if self.output_path.exists() and not force:
            logger.info(f"Dataset already exists at {self.output_path} — skipping generation")
            return self.output_path

        attacks = self._load_taxonomy()
        legit = self._generate_legitimate(10_000)
        fraud = self._generate_fraud(attacks)
        all_rows = self._add_engineered_features(legit + fraud)
        random.shuffle(all_rows)

        fieldnames = list(all_rows[0].keys())
        with open(self.output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)

        fraud_count = sum(1 for r in all_rows if r["is_fraud"])
        logger.info(
            f"Saved {len(all_rows)} transactions "
            f"({fraud_count} fraud / {len(all_rows) - fraud_count} legit) "
            f"to {self.output_path}"
        )
        return self.output_path

    async def generate_single(
        self,
        attack_id: Optional[str] = None,
        db=None,
    ) -> Dict:
        """API helper: generate one transaction on demand."""
        attack = None
        if attack_id:
            attacks = self._load_taxonomy()
            attack = next((a for a in attacks if a["attack_id"] == attack_id), None)

        return _make_transaction(is_fraud=attack is not None, attack=attack)

    async def generate_batch(
        self,
        count: int,
        attack_id: Optional[str] = None,
        db=None,
    ) -> List[Dict]:
        return [await self.generate_single(attack_id) for _ in range(count)]
