"""
Transaction generation API routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from db.database import get_db
from engines.generate import GenerateEngine

router = APIRouter()
generate_engine = GenerateEngine()


class GenerateRequest(BaseModel):
    """Request schema for transaction generation."""
    attack_id: Optional[str] = None
    count: int = 1


class TransactionResponse(BaseModel):
    """Transaction response schema."""
    transaction_id: str
    card_id: str
    merchant_name: str
    merchant_category: str
    amount: float
    currency: str
    timestamp: str
    city: str
    state: Optional[str]
    country: str
    is_fraud: bool
    attack_id: Optional[str]


@router.post("/transaction", response_model=TransactionResponse)
async def generate_transaction(
    request: GenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate a single synthetic transaction."""
    try:
        transaction = await generate_engine.generate_single(
            attack_id=request.attack_id,
            db=db
        )
        return transaction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def generate_batch(
    request: GenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate a batch of synthetic transactions."""
    if request.count > 1000:
        raise HTTPException(status_code=400, detail="Maximum batch size is 1000")

    try:
        transactions = await generate_engine.generate_batch(
            count=request.count,
            attack_id=request.attack_id,
            db=db
        )
        return {
            "count": len(transactions),
            "transactions": transactions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
