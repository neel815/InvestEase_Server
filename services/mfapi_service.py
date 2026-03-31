"""
Service for fetching real mutual fund data from MFAPI.in
Free public API - no authentication required.
"""

from typing import Optional
import httpx
from datetime import datetime, timedelta


MFAPI_BASE_URL = "https://api.mfapi.in/mf"


async def fetch_all_funds() -> list[dict]:
    """
    Fetch all available mutual funds from MFAPI.
    
    Returns:
        List of dicts with scheme_code and scheme_name
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MFAPI_BASE_URL}")
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])


async def fetch_fund_nav_history(scheme_code: str) -> list[dict]:
    """
    Fetch NAV history for a specific fund.
    
    Args:
        scheme_code: The MFAPI scheme code
        
    Returns:
        List of dicts with date and nav (sorted newest first as MFAPI returns)
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{MFAPI_BASE_URL}/{scheme_code}")
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])


def calculate_returns(nav_history: list[dict]) -> dict[str, Optional[float]]:
    """
    Calculate returns for 1y, 3y, and 5y from NAV history.
    
    NAV history is provided by MFAPI sorted newest first.
    Finds NAV values at exactly 1, 3, and 5 years ago by date matching.
    
    Args:
        nav_history: List of dicts with 'date' and 'nav' keys
        
    Returns:
        Dict with returns_1y, returns_3y, returns_5y as float percentages or None
    """
    if not nav_history:
        return {"returns_1y": None, "returns_3y": None, "returns_5y": None}
    
    # Get today's NAV (first entry is newest)
    today_nav = float(nav_history[0]["nav"])
    today_date = datetime.strptime(nav_history[0]["date"], "%d-%m-%Y")
    
    # Target dates
    one_year_ago = today_date - timedelta(days=365)
    three_years_ago = today_date - timedelta(days=365*3)
    five_years_ago = today_date - timedelta(days=365*5)
    
    # Find closest matching NAV values by date
    nav_1y_past = None
    nav_3y_past = None
    nav_5y_past = None
    
    for entry in nav_history[1:]:  # Skip first (today)
        entry_date = datetime.strptime(entry["date"], "%d-%m-%Y")
        entry_nav = float(entry["nav"])
        
        # Find 1 year ago
        if nav_1y_past is None and entry_date <= one_year_ago:
            nav_1y_past = entry_nav
        
        # Find 3 years ago
        if nav_3y_past is None and entry_date <= three_years_ago:
            nav_3y_past = entry_nav
        
        # Find 5 years ago
        if nav_5y_past is None and entry_date <= five_years_ago:
            nav_5y_past = entry_nav
            break  # Found all, can stop
    
    # Calculate returns as percentages
    returns_1y = ((today_nav - nav_1y_past) / nav_1y_past * 100) if nav_1y_past else None
    returns_3y = ((today_nav - nav_3y_past) / nav_3y_past * 100) if nav_3y_past else None
    returns_5y = ((today_nav - nav_5y_past) / nav_5y_past * 100) if nav_5y_past else None
    
    return {
        "returns_1y": returns_1y,
        "returns_3y": returns_3y,
        "returns_5y": returns_5y,
    }


def categorize_fund(scheme_name: str) -> str:
    """
    Categorize a fund based on its scheme name.
    
    Args:
        scheme_name: The fund's scheme name
        
    Returns:
        Category string
    """
    name_lower = scheme_name.lower()
    
    if "small cap" in name_lower or "smallcap" in name_lower:
        return "Small Cap"
    elif "mid cap" in name_lower or "midcap" in name_lower:
        return "Mid Cap"
    elif "large cap" in name_lower or "largecap" in name_lower:
        return "Large Cap"
    elif "liquid" in name_lower:
        return "Liquid"
    elif "debt" in name_lower or "gilt" in name_lower or "bond" in name_lower:
        return "Debt"
    elif "balanced" in name_lower or "hybrid" in name_lower or "aggressive hybrid" in name_lower:
        return "Hybrid"
    elif "sectoral" in name_lower or "sector" in name_lower or "thematic" in name_lower:
        return "Sectoral"
    else:
        return "Other"


async def get_top_funds_by_category(category: str, top_n: int = 3) -> list[dict]:
    """
    Get top N funds for a specific category based on 1-year returns.
    
    Args:
        category: Fund category (e.g., "Large Cap", "Debt", "Hybrid")
        top_n: Number of top funds to return
        
    Returns:
        List of dicts with scheme_code, scheme_name, category, returns_1y, returns_3y, returns_5y
    """
    # Fetch all funds
    all_funds = await fetch_all_funds()
    
    # Filter by category
    category_funds = []
    for fund in all_funds:
        fund_category = categorize_fund(fund.get("scheme_name", ""))
        if fund_category == category:
            category_funds.append(fund)
    
    # Fetch NAV history and calculate returns
    funds_with_returns = []
    for fund in category_funds:
        try:
            nav_history = await fetch_fund_nav_history(fund["scheme_code"])
            returns = calculate_returns(nav_history)
            
            # Only include if 1-year returns exist
            if returns["returns_1y"] is not None:
                funds_with_returns.append({
                    "scheme_code": fund["scheme_code"],
                    "scheme_name": fund["scheme_name"],
                    "category": category,
                    "returns_1y": returns["returns_1y"],
                    "returns_3y": returns["returns_3y"],
                    "returns_5y": returns["returns_5y"],
                })
        except Exception:
            # Skip funds that fail to fetch
            continue
    
    # Sort by 1-year returns descending
    funds_with_returns.sort(key=lambda x: x["returns_1y"], reverse=True)
    
    # Return top N
    return funds_with_returns[:top_n]
