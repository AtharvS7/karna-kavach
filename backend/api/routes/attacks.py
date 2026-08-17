"""
Attack taxonomy API routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from db.database import get_db
from db.models import Attack

router = APIRouter()


class AttackResponse(BaseModel):
    """Attack response schema."""
    id: int
    attack_id: str
    name: str
    category: str
    genai_amplification: str
    attack_steps: list
    target_channel: str
    detection_challenges: list
    transaction_features: dict

    class Config:
        from_attributes = True


@router.get("/", response_model=List[AttackResponse])
async def list_attacks(
    category: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List all attacks, optionally filtered by category."""
    query = select(Attack)
    if category:
        query = query.where(Attack.category == category)

    result = await db.execute(query)
    attacks = result.scalars().all()
    return attacks


@router.get("/{attack_id}", response_model=AttackResponse)
async def get_attack(
    attack_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific attack by ID."""
    query = select(Attack).where(Attack.attack_id == attack_id)
    result = await db.execute(query)
    attack = result.scalar_one_or_none()

    if not attack:
        raise HTTPException(status_code=404, detail="Attack not found")

    return attack


@router.get("/categories/list")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """Get all unique attack categories."""
    query = select(Attack.category).distinct()
    result = await db.execute(query)
    categories = [row[0] for row in result.all()]
    return {"categories": categories}
