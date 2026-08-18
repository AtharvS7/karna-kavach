"""
Identify Engine: generates the GenAI-powered fraud attack taxonomy using LLM.
Outputs 30+ attacks across 6 categories into data/attack_taxonomy.json.
"""
import json
import asyncio
import logging
from pathlib import Path
from typing import List
from engines.llm_client import LLMClient

logger = logging.getLogger(__name__)

CATEGORIES = [
    ("Card-Not-Present Fraud", "e-commerce, online payments", 6),
    ("Social Engineering", "phone, email, SMS, deepfake voice/video", 8),
    ("Account Takeover", "mobile banking, web portals", 5),
    ("Synthetic Identity Fraud", "new account opening, credit applications", 4),
    ("Authorization Bypass", "contactless, QR, API exploits", 4),
    ("Merchant & Refund Fraud", "returns, chargebacks, fake merchants", 4),
]

PROMPT_TEMPLATE = """You are a senior payment security researcher documenting GenAI-powered fraud attacks.

Generate exactly {count} distinct, realistic fraud attack variants for the category: **{category}**
Target channels/surfaces: {channel}

Rules:
- Ground each attack in real payment system mechanics
- Explain specifically HOW GenAI (LLMs, deepfakes, voice cloning, image generation, etc.) lowers the barrier or amplifies the attack
- Keep transaction_features grounded in real observable signals
- detection_challenges must explain WHY rule-based systems fail against this

Return a JSON array (no markdown, no explanation outside JSON):
[
  {{
    "attack_id": "kebab-case-unique-id",
    "name": "Short descriptive name",
    "category": "{category}",
    "genai_amplification": "How GenAI specifically enables or scales this attack",
    "attack_steps": ["step 1", "step 2", "step 3"],
    "target_channel": "specific payment channel",
    "detection_challenges": ["challenge 1", "challenge 2"],
    "transaction_features": {{
      "amount_range": [min, max],
      "velocity_spike": true/false,
      "geographic_anomaly": true/false,
      "merchant_category": "mcc_name",
      "time_pattern": "description",
      "card_present": true/false
    }}
  }}
]"""


class IdentifyEngine:
    def __init__(self):
        self.llm = LLMClient()
        # Use absolute path from project root
        project_root = Path(__file__).parent.parent.parent
        self.output_path = project_root / "data" / "attack_taxonomy.json"
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def _extract_json_array(self, raw: str) -> List[dict]:
        """Robustly extract a JSON array from LLM output, handling markdown fences and trailing text."""
        import re
        text = raw.strip()

        # Strategy 1: Strip markdown code fences (```json ... ```)
        fence_match = re.search(r'```(?:json)?\s*\n?(.*?)```', text, re.DOTALL)
        if fence_match:
            text = fence_match.group(1).strip()

        # Strategy 2: Find the outermost JSON array brackets
        start = text.find('[')
        if start == -1:
            raise ValueError("No JSON array found in LLM response")

        # Find matching closing bracket by counting depth
        depth = 0
        end = -1
        for i in range(start, len(text)):
            if text[i] == '[':
                depth += 1
            elif text[i] == ']':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break

        if end == -1:
            raise ValueError("Unmatched JSON array brackets")

        return json.loads(text[start:end])

    async def _generate_category(self, category: str, channel: str, count: int) -> List[dict]:
        prompt = PROMPT_TEMPLATE.format(category=category, channel=channel, count=count)
        for attempt in range(2):  # retry once on failure
            try:
                raw = await self.llm.generate(prompt, temperature=0.8)
                attacks = self._extract_json_array(raw)
                logger.info(f"Generated {len(attacks)} attacks for '{category}'")
                return attacks
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed for '{category}': {e}")
                if attempt == 0:
                    await asyncio.sleep(2)  # brief pause before retry
        logger.error(f"Failed to generate attacks for '{category}' after 2 attempts")
        return []

    async def run(self) -> List[dict]:
        """Generate full attack taxonomy across all categories."""
        # Check if taxonomy already exists (with actual data) to avoid wasting LLM quota
        if self.output_path.exists():
            with open(self.output_path) as f:
                existing = json.load(f)
            if len(existing) > 0:
                logger.info(f"attack_taxonomy.json already has {len(existing)} attacks — loading from disk")
                return existing
            logger.info("attack_taxonomy.json exists but is empty — regenerating")

        logger.info("Generating attack taxonomy via LLM...")
        all_attacks: List[dict] = []

        # Generate categories sequentially to respect rate limits
        for category, channel, count in CATEGORIES:
            attacks = await self._generate_category(category, channel, count)
            all_attacks.extend(attacks)
            await asyncio.sleep(1)  # polite pause between requests

        with open(self.output_path, "w") as f:
            json.dump(all_attacks, f, indent=2)

        logger.info(f"Saved {len(all_attacks)} attacks to {self.output_path}")
        return all_attacks

    async def seed_db(self, db) -> int:
        """Seed attack taxonomy into the database."""
        from sqlalchemy import select
        from db.models import Attack

        attacks = await self.run()
        inserted = 0

        for a in attacks:
            result = await db.execute(select(Attack).where(Attack.attack_id == a["attack_id"]))
            if result.scalar_one_or_none():
                continue
            db.add(Attack(
                attack_id=a["attack_id"],
                name=a["name"],
                category=a["category"],
                genai_amplification=a["genai_amplification"],
                attack_steps=a["attack_steps"],
                target_channel=a["target_channel"],
                detection_challenges=a["detection_challenges"],
                transaction_features=a["transaction_features"],
            ))
            inserted += 1

        await db.commit()
        logger.info(f"Seeded {inserted} new attacks into DB")
        return inserted
