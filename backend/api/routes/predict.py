"""
Fraud prediction API routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional

from engines.defend import DefendEngine

router = APIRouter()
defend_engine = DefendEngine()


class PredictRequest(BaseModel):
    """Request schema for fraud prediction."""
    card_number: str
    merchant_name: str
    merchant_category: str
    amount: float
    currency: str = "USD"
    city: str
    state: Optional[str] = None
    country: str
    timestamp: Optional[str] = None


class PredictResponse(BaseModel):
    """Response schema for fraud prediction."""
    is_fraud: bool
    fraud_probability: float
    risk_score: int
    confidence: str
    top_features: Dict[str, float]


@router.post("/", response_model=PredictResponse)
async def predict_fraud(request: PredictRequest):
    """Predict if a transaction is fraudulent."""
    try:
        prediction = await defend_engine.predict(request.model_dump())
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_model_metrics():
    """Get current model performance metrics."""
    try:
        metrics = await defend_engine.get_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
