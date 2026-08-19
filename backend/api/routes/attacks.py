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


import json
from pathlib import Path

_TAXONOMY_PATH = Path(__file__).parent.parent.parent.parent / "data" / "attack_taxonomy.json"


def _load_taxonomy_file() -> list[dict]:
    if _TAXONOMY_PATH.exists():
        with open(_TAXONOMY_PATH) as f:
            data = json.load(f)
            for idx, item in enumerate(data, 1):
                if "id" not in item:
                    item["id"] = idx
            return data
    return []


@router.get("/", response_model=List[AttackResponse])
async def list_attacks(
    category: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List all attacks, optionally filtered by category."""
    try:
        query = select(Attack)
        if category:
            query = query.where(Attack.category == category)
        result = await db.execute(query)
        attacks = result.scalars().all()
        if attacks:
            return attacks
    except Exception:
        pass

    # Fallback to JSON taxonomy file
    data = _load_taxonomy_file()
    if category:
        data = [a for a in data if a.get("category") == category]
    return data


@router.get("/{attack_id}", response_model=AttackResponse)
async def get_attack(
    attack_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific attack by ID."""
    try:
        query = select(Attack).where(Attack.attack_id == attack_id)
        result = await db.execute(query)
        attack = result.scalar_one_or_none()
        if attack:
            return attack
    except Exception:
        pass

    # Fallback to JSON taxonomy file
    data = _load_taxonomy_file()
    for item in data:
        if item.get("attack_id") == attack_id:
            return item

    raise HTTPException(status_code=404, detail="Attack not found")


@router.get("/categories/list")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """Get all unique attack categories."""
    try:
        query = select(Attack.category).distinct()
        result = await db.execute(query)
        categories = [row[0] for row in result.all()]
        if categories:
            return {"categories": categories}
    except Exception:
        pass

    # Fallback to JSON taxonomy file
    data = _load_taxonomy_file()
    categories = sorted(list(set(a["category"] for a in data if "category" in a)))
    return {"categories": categories}
