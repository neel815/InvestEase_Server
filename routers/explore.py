"""
Explore Bucket Router - Fund search and investment management.
Uses funds_master DB for fund directory, individual MFAPI calls for live NAV.
"""

import asyncio
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import requests

from core.dependenices import get_current_user
from core.acl import verify_goal_ownership, require_mode
from db.session import get_db
from models.explore_holding import ExploreHolding
from models.goal import Goal
from models.funds_master import FundsMaster
from schemas.explore import (
    FundSearchResultOut,
    FundDetailsOut,
    ExploreInvestIn,
    ExploreHoldingOut,
    ExploreHoldingsListOut,
)

router = APIRouter(prefix="/explore", tags=["explore"])

MFAPI_BASE_URL = "https://api.mfapi.in/mf"


def fetch_mfapi_nav(scheme_code: str) -> dict | None:
    """
    Fetch current NAV and 30-day history from MFAPI.
    Returns dict with current_nav and nav_history, or None if fetch fails.
    """
    try:
        url = f"{MFAPI_BASE_URL}/{scheme_code}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if "data" not in data or not data["data"]:
            return None
        
        # Get current NAV from first entry
        current_entry = data["data"][0]
        current_nav = float(current_entry.get("nav", 0))
        
        # Get last 30 days of NAV history
        nav_history = []
        for entry in data["data"][:30]:
            nav_history.append({
                "date": entry.get("date"),
                "nav": float(entry.get("nav", 0))
            })
        
        return {
            "scheme_code": scheme_code,
            "scheme_name": data.get("meta", {}).get("scheme_name", ""),
            "current_nav": current_nav,
            "nav_history": nav_history,
        }
    except Exception as e:
        print(f"MFAPI fetch failed for {scheme_code}: {e}")
        return None


@router.get("/ping")
async def ping():
    """Health check endpoint."""
    return {"status": "explore router ready"}


@router.get("/search", response_model=list[FundSearchResultOut])
async def search_explore_funds(
    q: str = Query(..., min_length=1),
    _user_id: str = Depends(get_current_user),
    _db: AsyncSession = Depends(get_db),
):
    """
    Search for funds by name in funds_master table.
    Returns top 20 matching active funds.
    No external API calls - pure DB lookup.
    """
    if not q or len(q) < 1:
        raise HTTPException(status_code=400, detail="Query must be at least 1 character")
    
    # Query funds_master using ilike
    stmt = select(FundsMaster).where(
        FundsMaster.scheme_name.ilike(f"%{q}%"),
        FundsMaster.is_active == True
    ).limit(20)
    
    result = await _db.execute(stmt)
    funds = result.scalars().all()
    
    return [
        FundSearchResultOut(
            scheme_code=f.scheme_code,
            scheme_name=f.scheme_name,
        )
        for f in funds
    ]


@router.get("/fund/{scheme_code}", response_model=FundDetailsOut)
async def get_explore_fund_details(
    scheme_code: str,
    _user_id: str = Depends(get_current_user),
    _db: AsyncSession = Depends(get_db),
):
    """
    Get fund details from DB + live NAV from MFAPI.
    If MFAPI fails, return DB data with null current_nav.
    """
    # Fetch from funds_master
    stmt = select(FundsMaster).where(FundsMaster.scheme_code == scheme_code)
    result = await _db.execute(stmt)
    fund = result.scalar_one_or_none()
    
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    
    # Fetch live NAV from MFAPI in executor (non-blocking)
    loop = asyncio.get_event_loop()
    nav_data = await loop.run_in_executor(None, fetch_mfapi_nav, scheme_code)
    
    if nav_data:
        return FundDetailsOut(
            scheme_code=fund.scheme_code,
            scheme_name=fund.scheme_name,
            category=fund.category,
            current_nav=nav_data["current_nav"],
            nav_history=nav_data["nav_history"],
        )
    else:
        # Return DB data with null NAV if fetch fails
        return FundDetailsOut(
            scheme_code=fund.scheme_code,
            scheme_name=fund.scheme_name,
            category=fund.category,
            current_nav=None,
            nav_history=[],
        )


@router.post("/invest", response_model=ExploreHoldingOut)
async def invest_explore(
    payload: ExploreInvestIn,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Invest in a fund through explore bucket.
    Verifies goal ownership and copilot/manual mode.
    Fetches live NAV from MFAPI.
    """
    # ACL checks
    await verify_goal_ownership(payload.goal_id, user_id, db)
    await require_mode(["copilot", "manual"], payload.goal_id, user_id, db)
    
    # Fetch live NAV
    loop = asyncio.get_event_loop()
    nav_data = await loop.run_in_executor(None, fetch_mfapi_nav, payload.scheme_code)
    
    if not nav_data:
        raise HTTPException(status_code=503, detail="Unable to fetch fund NAV from MFAPI")
    
    current_nav = nav_data["current_nav"]
    units_to_add = float(payload.amount) / current_nav
    
    # Check if holding exists
    stmt = select(ExploreHolding).where(
        ExploreHolding.user_id == UUID(user_id),
        ExploreHolding.goal_id == payload.goal_id,
        ExploreHolding.scheme_code == payload.scheme_code,
    )
    result = await db.execute(stmt)
    existing_holding = result.scalar_one_or_none()
    
    if existing_holding:
        # Update existing holding
        prev_invested = float(existing_holding.invested_amount)
        prev_units = existing_holding.units
        
        new_invested = prev_invested + float(payload.amount)
        new_units = prev_units + units_to_add
        new_average_nav = new_invested / new_units if new_units > 0 else current_nav
        
        existing_holding.units = new_units
        existing_holding.average_nav = new_average_nav
        existing_holding.invested_amount = Decimal(str(new_invested))
        existing_holding.current_value = Decimal(str(new_units * current_nav))
        existing_holding.last_known_nav = current_nav
        existing_holding.nav_last_updated = datetime.utcnow()
        existing_holding.last_updated = datetime.utcnow()
        
        db.add(existing_holding)
        await db.commit()
        await db.refresh(existing_holding)
        holding = existing_holding
    else:
        # Create new holding
        new_holding = ExploreHolding(
            user_id=UUID(user_id),
            goal_id=payload.goal_id,
            scheme_code=payload.scheme_code,
            scheme_name=payload.scheme_name,
            category=payload.category,
            units=units_to_add,
            average_nav=current_nav,
            invested_amount=payload.amount,
            current_value=Decimal(str(units_to_add * current_nav)),
            last_known_nav=current_nav,
            nav_last_updated=datetime.utcnow(),
            last_updated=datetime.utcnow(),
        )
        db.add(new_holding)
        await db.commit()
        await db.refresh(new_holding)
        holding = new_holding
    
    return ExploreHoldingOut(
        id=holding.id,
        scheme_code=holding.scheme_code,
        scheme_name=holding.scheme_name,
        category=holding.category,
        units=holding.units,
        average_nav=holding.average_nav,
        invested_amount=float(holding.invested_amount),
        current_value=float(holding.current_value),
    )


@router.get("/holdings/{goal_id}", response_model=ExploreHoldingsListOut)
async def get_explore_holdings(
    goal_id: UUID,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all holdings for a goal with live NAV updates.
    Fetches latest NAV from MFAPI for each holding.
    If MFAPI fails, uses last_known_nav and sets nav_is_stale flag.
    """
    # ACL check
    await require_mode(["copilot", "manual"], goal_id, user_id, db)
    
    # Fetch holdings
    stmt = select(ExploreHolding).where(
        ExploreHolding.user_id == UUID(user_id),
        ExploreHolding.goal_id == goal_id,
    )
    result = await db.execute(stmt)
    holdings = result.scalars().all()
    
    holdings_data = []
    total_invested = 0.0
    total_current_value = 0.0
    
    loop = asyncio.get_event_loop()
    
    for holding in holdings:
        # Fetch live NAV
        nav_data = await loop.run_in_executor(None, fetch_mfapi_nav, holding.scheme_code)
        
        if nav_data:
            # Update holding with fresh NAV
            current_nav = nav_data["current_nav"]
            current_value = holding.units * current_nav
            
            # Save to DB
            holding.current_value = Decimal(str(current_value))
            holding.last_known_nav = current_nav
            holding.nav_last_updated = datetime.utcnow()
            db.add(holding)
            
            return_pct = ((current_value - float(holding.invested_amount)) / float(holding.invested_amount) * 100) if float(holding.invested_amount) > 0 else 0
            
            holdings_data.append({
                "id": holding.id,
                "scheme_code": holding.scheme_code,
                "scheme_name": holding.scheme_name,
                "category": holding.category,
                "units": holding.units,
                "average_nav": holding.average_nav,
                "invested_amount": float(holding.invested_amount),
                "current_value": current_value,
                "return_percentage": return_pct,
                "nav_is_stale": False,
                "nav_last_updated": holding.nav_last_updated,
            })
            
            total_invested += float(holding.invested_amount)
            total_current_value += current_value
        else:
            # Use last known NAV
            current_value = (holding.last_known_nav * holding.units) if holding.last_known_nav else float(holding.current_value)
            return_pct = ((current_value - float(holding.invested_amount)) / float(holding.invested_amount) * 100) if float(holding.invested_amount) > 0 else 0
            
            holdings_data.append({
                "id": holding.id,
                "scheme_code": holding.scheme_code,
                "scheme_name": holding.scheme_name,
                "category": holding.category,
                "units": holding.units,
                "average_nav": holding.average_nav,
                "invested_amount": float(holding.invested_amount),
                "current_value": current_value,
                "return_percentage": return_pct,
                "nav_is_stale": True,
                "nav_last_updated": holding.nav_last_updated,
            })
            
            total_invested += float(holding.invested_amount)
            total_current_value += current_value
    
    # Commit any updates
    if holdings:
        await db.commit()
    
    overall_return_pct = ((total_current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
    
    return ExploreHoldingsListOut(
        holdings=holdings_data,
        total_invested=total_invested,
        total_current_value=total_current_value,
        overall_return_percentage=overall_return_pct,
    )


@router.delete("/holdings/{holding_id}")
async def delete_explore_holding(
    holding_id: UUID,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an explore holding."""
    stmt = select(ExploreHolding).where(ExploreHolding.id == holding_id)
    result = await db.execute(stmt)
    holding = result.scalar_one_or_none()
    
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    
    # ACL check
    await require_mode(["copilot", "manual"], holding.goal_id, user_id, db)
    
    await db.delete(holding)
    await db.commit()
    
    return {"message": "Holding deleted successfully"}
