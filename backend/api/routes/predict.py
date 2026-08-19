"""
Fraud prediction routes — wired to real DefendEngine.
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, List

from engines.defend import DefendEngine

router = APIRouter()
defend = DefendEngine()


class PredictRequest(BaseModel):
    card_id: Optional[str] = None
    merchant_name: str
    merchant_category: str
    amount: float
    currency: str = "USD"
    city: str
    country: str = "US"
    card_present: bool = True
    velocity_1h: int = 1
    amount_deviation: float = 0.0
    cross_border: bool = False
    mcc: int = 5999
    txn_index: int = 0


class PredictResponse(BaseModel):
    is_fraud: bool
    fraud_probability: float
    risk_score: int
    confidence: str
    top_features: Dict


@router.post("/", response_model=PredictResponse)
async def predict_fraud(request: PredictRequest):
    try:
        result = await defend.predict(request.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics():
    return await defend.get_metrics()


@router.post("/train")
async def train_model(background_tasks: BackgroundTasks):
    """Kick off model training in the background."""
    def _train():
        defend.train()
    background_tasks.add_task(_train)
    return {"status": "training started"}


@router.post("/feedback-loop")
async def run_feedback_loop(iterations: int = 10):
    """Run the adversarial feedback loop (blocking — use for demos)."""
    if iterations > 20:
        raise HTTPException(status_code=400, detail="Max 20 iterations")
    try:
        history = await defend.adversarial_loop(iterations=iterations)
        return {"iterations": len(history), "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
