"""
Defend Engine: trains XGBoost + ensemble on synthetic fraud data,
exposes real-time prediction, and drives the adversarial feedback loop.
"""
import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb

logger = logging.getLogger(__name__)

DATA_PATH = Path("data/synthetic_transactions/transactions.csv")
MODEL_PATH = Path("backend/models/fraud_classifier_v1.pkl")
METRICS_PATH = Path("backend/models/metrics.json")

FEATURE_COLS = [
    "amount", "velocity_1h", "amount_deviation",
    "cross_border", "card_present", "txn_index",
    "mcc", "merchant_category_enc",
]


def _encode_df(df: pd.DataFrame) -> pd.DataFrame:
    """Encode categorical columns; returns new DataFrame."""
    out = df.copy()
    le = LabelEncoder()
    out["merchant_category_enc"] = le.fit_transform(out["merchant_category"].astype(str))
    return out


class DefendEngine:
    def __init__(self):
        self.model: Optional[VotingClassifier] = None
        self.metrics: Dict = {}
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Load persisted model if available
        if MODEL_PATH.exists():
            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
            if METRICS_PATH.exists():
                with open(METRICS_PATH) as f:
                    self.metrics = json.load(f)
            logger.info("Loaded persisted fraud classifier")

    # ------------------------------------------------------------------ #
    #  Training                                                            #
    # ------------------------------------------------------------------ #

    def train(self, data_path: Path = DATA_PATH) -> Dict:
        """Train ensemble classifier on synthetic dataset."""
        if not data_path.exists():
            raise FileNotFoundError(
                f"Training data not found at {data_path} — run GenerateEngine.run() first"
            )

        df = pd.read_csv(data_path)
        df = _encode_df(df)

        available = [c for c in FEATURE_COLS if c in df.columns]
        X = df[available].fillna(0)
        y = df["is_fraud"].astype(int)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )

        # Oversample minority fraud class
        smote = SMOTE(sampling_strategy=0.5, random_state=42)
        X_bal, y_bal = smote.fit_resample(X_train, y_train)

        neg, pos = (y_bal == 0).sum(), (y_bal == 1).sum()
        scale_pos = neg / pos if pos > 0 else 1.0

        xgb_clf = xgb.XGBClassifier(
            max_depth=6,
            learning_rate=0.1,
            n_estimators=200,
            scale_pos_weight=scale_pos,
            eval_metric="aucpr",
            use_label_encoder=False,
            random_state=42,
            n_jobs=-1,
        )
        rf_clf = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
        )
        lr_clf = LogisticRegression(max_iter=1000, random_state=42)

        ensemble = VotingClassifier(
            estimators=[("xgb", xgb_clf), ("rf", rf_clf), ("lr", lr_clf)],
            voting="soft",
            weights=[2, 1, 1],
        )

        ensemble.fit(X_bal, y_bal)

        y_pred = ensemble.predict(X_test)
        y_proba = ensemble.predict_proba(X_test)[:, 1]

        self.metrics = {
            "model_version": "v1.0",
            "precision": round(precision_score(y_test, y_pred), 4),
            "recall": round(recall_score(y_test, y_pred), 4),
            "f1_score": round(f1_score(y_test, y_pred), 4),
            "auc_roc": round(roc_auc_score(y_test, y_proba), 4),
            "auc_pr": round(average_precision_score(y_test, y_proba), 4),
            "train_samples": len(X_bal),
            "test_samples": len(X_test),
            "feature_cols": available,
        }

        self.model = ensemble
        self._persist()

        logger.info(
            f"Training complete — precision={self.metrics['precision']}, "
            f"recall={self.metrics['recall']}, F1={self.metrics['f1_score']}"
        )
        return self.metrics

    def _persist(self):
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.model, f)
        with open(METRICS_PATH, "w") as f:
            json.dump(self.metrics, f, indent=2)

    # ------------------------------------------------------------------ #
    #  Inference                                                           #
    # ------------------------------------------------------------------ #

    async def predict(self, transaction: Dict) -> Dict:
        """Predict fraud probability for a single transaction dict."""
        if self.model is None:
            # Return a meaningful mock until model is trained
            return self._mock_prediction()

        try:
            features = self._extract_features(transaction)
            proba = float(self.model.predict_proba([features])[0][1])
        except Exception as e:
            logger.warning(f"Prediction failed ({e}), falling back to mock")
            return self._mock_prediction()

        risk_score = int(proba * 100)
        return {
            "is_fraud": proba > 0.5,
            "fraud_probability": round(proba, 4),
            "risk_score": risk_score,
            "confidence": "high" if proba > 0.8 or proba < 0.2 else "medium",
            "top_features": {
                "amount_deviation": round(transaction.get("amount_deviation", 0.0), 3),
                "cross_border": int(transaction.get("cross_border", False)),
                "velocity_1h": transaction.get("velocity_1h", 0),
            },
        }

    def _extract_features(self, t: Dict) -> List:
        """Map a raw transaction dict to the model's feature vector."""
        cat_map = {k: i for i, k in enumerate(
            ["retail", "grocery", "gas_station", "restaurant",
             "electronics", "travel", "entertainment", "atm", "online", "pharmacy"]
        )}
        return [
            float(t.get("amount", 0)),
            float(t.get("velocity_1h", 0)),
            float(t.get("amount_deviation", 0)),
            int(t.get("cross_border", False) or t.get("country", "US") != "US"),
            int(t.get("card_present", True)),
            float(t.get("txn_index", 0)),
            float(t.get("mcc", 5999)),
            float(cat_map.get(t.get("merchant_category", "retail"), 0)),
        ]

    @staticmethod
    def _mock_prediction() -> Dict:
        import random
        p = random.uniform(0.01, 0.99)
        return {
            "is_fraud": p > 0.5,
            "fraud_probability": round(p, 4),
            "risk_score": int(p * 100),
            "confidence": "low",
            "top_features": {"note": "model not trained yet"},
        }

    async def get_metrics(self) -> Dict:
        return self.metrics if self.metrics else {"note": "model not trained yet — run train()"}

    # ------------------------------------------------------------------ #
    #  Adversarial feedback loop                                          #
    # ------------------------------------------------------------------ #

    async def adversarial_loop(
        self,
        iterations: int = 10,
        threshold: float = 0.70,
    ) -> List[Dict]:
        """
        For each iteration: probe the model with a new attack variant,
        retrain on failures if detection rate < threshold.
        Returns per-iteration metrics.
        """
        from engines.generate import GenerateEngine, _make_transaction
        from engines.llm_client import LLMClient

        gen = GenerateEngine()
        llm = LLMClient()
        history: List[Dict] = []

        with open(Path("data/attack_taxonomy.json")) as f:
            taxonomy = json.load(f)

        # Train baseline model if not already trained
        if self.model is None:
            gen.run()
            self.train()

        for i in range(iterations):
            # Ask LLM to generate a new evasive attack variant
            missed = [h for h in history if h.get("detection_rate", 1) < threshold]
            missed_desc = json.dumps(missed[-3:], indent=2) if missed else "none yet"

            prompt = f"""You are a fraud researcher designing attacks that evade ML classifiers.

Previously poorly-detected attacks: {missed_desc}

Generate ONE new GenAI-powered payment fraud attack variant designed to be subtle
and evade detection by mimicking legitimate transactions.

Return ONLY a JSON object with these exact keys:
{{
  "attack_id": "adversarial-iter-{i}",
  "name": "...",
  "category": "...",
  "genai_amplification": "...",
  "attack_steps": ["..."],
  "target_channel": "...",
  "detection_challenges": ["..."],
  "transaction_features": {{
    "amount_range": [min, max],
    "velocity_spike": false,
    "geographic_anomaly": false,
    "merchant_category": "retail",
    "time_pattern": "...",
    "card_present": true
  }}
}}"""

            try:
                raw = await llm.generate(prompt, temperature=0.9)
                raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
                new_attack = json.loads(raw)
            except Exception as e:
                logger.warning(f"Iteration {i}: LLM parse failed ({e}), using random attack")
                new_attack = taxonomy[i % len(taxonomy)]

            # Generate probe samples
            samples = [
                _make_transaction(is_fraud=True, attack=new_attack)
                for _ in range(100)
            ]

            if self.model:
                features = [self._extract_features(s) for s in samples]
                probas = self.model.predict_proba(features)[:, 1]
                detection_rate = float((probas > 0.5).mean())
            else:
                detection_rate = 1.0

            iteration_result = {
                "iteration": i,
                "attack_id": new_attack.get("attack_id", f"iter-{i}"),
                "attack_name": new_attack.get("name", "unknown"),
                "detection_rate": round(detection_rate, 3),
                "retrained": False,
            }

            # Retrain if detection rate is below threshold
            if detection_rate < threshold:
                logger.info(
                    f"Iteration {i}: detection rate {detection_rate:.0%} below "
                    f"threshold {threshold:.0%} — retraining..."
                )
                # Append new attack to taxonomy and regenerate dataset
                taxonomy.append(new_attack)
                with open(Path("data/attack_taxonomy.json"), "w") as f:
                    json.dump(taxonomy, f, indent=2)

                gen.run(force=True)
                self.train()
                iteration_result["retrained"] = True

            history.append(iteration_result)
            logger.info(f"Feedback loop iteration {i}: {iteration_result}")

            import asyncio
            await asyncio.sleep(1)

        # Persist loop history
        history_path = Path("data/feedback_loop_history.json")
        with open(history_path, "w") as f:
            json.dump(history, f, indent=2)

        return history
