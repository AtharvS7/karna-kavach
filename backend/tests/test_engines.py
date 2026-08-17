"""
Smoke tests for the three engines — no fixtures, no framework, runnable via pytest.
"""
import asyncio
import json
import sys
from pathlib import Path

# Allow imports from backend root
sys.path.insert(0, str(Path(__file__).parent.parent))


# ── Generate Engine ──────────────────────────────────────────────────────────

def test_generate_single_legitimate():
    from engines.generate import _make_transaction
    txn = _make_transaction(is_fraud=False)
    assert txn["is_fraud"] == 0
    assert txn["attack_id"] is None
    assert txn["amount"] > 0
    assert txn["country"] == "US"


def test_generate_single_fraud_geographic():
    from engines.generate import _make_transaction
    attack = {
        "attack_id": "test-geo-01",
        "transaction_features": {
            "amount_range": [1000, 2000],
            "velocity_spike": False,
            "geographic_anomaly": True,
            "merchant_category": "electronics",
            "card_present": False,
        }
    }
    txn = _make_transaction(is_fraud=True, attack=attack)
    assert txn["is_fraud"] == 1
    assert txn["country"] != "US"
    assert txn["amount"] >= 1000


def test_generate_velocity_spike():
    from engines.generate import _make_transaction
    from datetime import datetime
    attack = {
        "attack_id": "test-vel-01",
        "transaction_features": {
            "velocity_spike": True,
            "geographic_anomaly": False,
            "card_present": False,
        }
    }
    base = datetime(2026, 8, 17, 10, 0, 0)
    txns = [_make_transaction(is_fraud=True, attack=attack, base_time=base, velocity_index=i) for i in range(5)]
    assert len(txns) == 5
    assert all(t["is_fraud"] == 1 for t in txns)


# ── Identify Engine ───────────────────────────────────────────────────────────

def test_taxonomy_loads_if_exists(tmp_path):
    """IdentifyEngine.run() returns cached taxonomy without LLM call."""
    from engines.identify import IdentifyEngine
    engine = IdentifyEngine()
    # Temporarily override output path
    sample = [{"attack_id": "test-01", "name": "Test Attack", "category": "Test"}]
    tmp_file = tmp_path / "attack_taxonomy.json"
    tmp_file.write_text(json.dumps(sample))
    engine.output_path = tmp_file

    result = asyncio.get_event_loop().run_until_complete(engine.run())
    assert result == sample


# ── Defend Engine ─────────────────────────────────────────────────────────────

def test_mock_prediction_shape():
    from engines.defend import DefendEngine
    engine = DefendEngine()
    engine.model = None  # force mock path
    result = asyncio.get_event_loop().run_until_complete(
        engine.predict({"amount": 500, "merchant_category": "retail"})
    )
    assert "is_fraud" in result
    assert "fraud_probability" in result
    assert 0.0 <= result["fraud_probability"] <= 1.0
    assert 0 <= result["risk_score"] <= 100


def test_feature_extraction():
    from engines.defend import DefendEngine
    engine = DefendEngine()
    txn = {
        "amount": 250.0,
        "velocity_1h": 3,
        "amount_deviation": 1.2,
        "cross_border": True,
        "card_present": False,
        "txn_index": 5,
        "mcc": 5732,
        "merchant_category": "electronics",
    }
    features = engine._extract_features(txn)
    assert len(features) == 8
    assert features[0] == 250.0
    assert features[3] == 1  # cross_border=True


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
