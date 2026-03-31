from datetime import datetime

BASKET_TYPES = ("conservative", "moderate", "aggressive")

GOAL_MODE_BASKET_RULES: dict[tuple[str, str], str] = {
    ("retirement", "autopilot"): "moderate",
    ("retirement", "copilot"): "aggressive",
    ("retirement", "manual"): "aggressive",
    ("house", "autopilot"): "conservative",
    ("house", "copilot"): "moderate",
    ("house", "manual"): "moderate",
    ("education", "autopilot"): "conservative",
    ("education", "copilot"): "moderate",
    ("education", "manual"): "aggressive",
    ("wealth", "autopilot"): "moderate",
    ("wealth", "copilot"): "aggressive",
    ("wealth", "manual"): "aggressive",
}

MODE_FALLBACK_RULES: dict[str, str] = {
    "autopilot": "conservative",
    "copilot": "moderate",
    "manual": "aggressive",
}

# Basket to fund categories mapping
# Each basket type should contain 3 fund categories (retrieved from MFAPI at runtime)
BASKET_CATEGORY_RULES: dict[str, list[str]] = {
    "conservative": ["Debt", "Liquid", "Hybrid"],
    "moderate": ["Large Cap", "Hybrid", "Mid Cap"],
    "aggressive": ["Small Cap", "Mid Cap", "Sectoral"],
}


def get_recommended_basket(goal_type: str, investment_mode: str) -> str:
    return GOAL_MODE_BASKET_RULES.get(
        (goal_type, investment_mode),
        MODE_FALLBACK_RULES.get(investment_mode, "moderate"),
    )


def get_basket_category_rules(basket_type: str) -> list[str]:
    """Get the fund categories for a basket type."""
    return BASKET_CATEGORY_RULES.get(basket_type, ["Large Cap", "Hybrid", "Debt"])


def build_recommendation_baskets(goal_type: str, investment_mode: str) -> dict[str, object]:
    recommended_basket = get_recommended_basket(goal_type, investment_mode)
    recommended_at = datetime.utcnow()

    baskets: list[dict[str, object]] = []
    for basket_type in BASKET_TYPES:
        # Category rules will be resolved in the service layer with real MFAPI data
        categories = get_basket_category_rules(basket_type)
        baskets.append(
            {
                "basket_type": basket_type,
                "recommended": basket_type == recommended_basket,
                "categories": categories,  # Will be replaced with actual funds in service
            }
        )

    return {
        "recommended_at": recommended_at,
        "baskets": baskets,
    }

