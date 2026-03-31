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

# Hardcoded MVP dataset: 9 realistic-looking Indian mutual funds.
FUNDS_BY_BASKET: dict[str, list[dict[str, float | str]]] = {
    "conservative": [
        {
            "scheme_code": "INVCON001",
            "scheme_name": "Surya Short Duration Income Fund",
            "category": "Debt - Short Duration",
            "basket_type": "conservative",
            "returns_1y": 7.2,
            "returns_3y": 7.8,
            "returns_5y": 8.1,
        },
        {
            "scheme_code": "INVCON002",
            "scheme_name": "Pragati Corporate Bond Fund",
            "category": "Debt - Corporate Bond",
            "basket_type": "conservative",
            "returns_1y": 7.9,
            "returns_3y": 8.4,
            "returns_5y": 8.7,
        },
        {
            "scheme_code": "INVCON003",
            "scheme_name": "Nivesh Balanced Savings Fund",
            "category": "Hybrid - Conservative",
            "basket_type": "conservative",
            "returns_1y": 8.6,
            "returns_3y": 9.1,
            "returns_5y": 9.5,
        },
    ],
    "moderate": [
        {
            "scheme_code": "INVMOD001",
            "scheme_name": "Aarohan Large & Midcap Opportunities Fund",
            "category": "Equity - Large & Mid Cap",
            "basket_type": "moderate",
            "returns_1y": 13.8,
            "returns_3y": 15.2,
            "returns_5y": 14.6,
        },
        {
            "scheme_code": "INVMOD002",
            "scheme_name": "Dhanvriddhi Aggressive Hybrid Fund",
            "category": "Hybrid - Aggressive",
            "basket_type": "moderate",
            "returns_1y": 12.7,
            "returns_3y": 13.9,
            "returns_5y": 13.4,
        },
        {
            "scheme_code": "INVMOD003",
            "scheme_name": "Sampatti Flexi Cap Fund",
            "category": "Equity - Flexi Cap",
            "basket_type": "moderate",
            "returns_1y": 14.4,
            "returns_3y": 16.1,
            "returns_5y": 15.3,
        },
    ],
    "aggressive": [
        {
            "scheme_code": "INVAGG001",
            "scheme_name": "Tejas Small Cap Alpha Fund",
            "category": "Equity - Small Cap",
            "basket_type": "aggressive",
            "returns_1y": 22.1,
            "returns_3y": 21.4,
            "returns_5y": 18.8,
        },
        {
            "scheme_code": "INVAGG002",
            "scheme_name": "Udaan Midcap Momentum Fund",
            "category": "Equity - Mid Cap",
            "basket_type": "aggressive",
            "returns_1y": 19.3,
            "returns_3y": 18.6,
            "returns_5y": 16.9,
        },
        {
            "scheme_code": "INVAGG003",
            "scheme_name": "Navchetna Thematic Innovation Fund",
            "category": "Equity - Thematic",
            "basket_type": "aggressive",
            "returns_1y": 24.6,
            "returns_3y": 19.8,
            "returns_5y": 17.2,
        },
    ],
}


def get_recommended_basket(goal_type: str, investment_mode: str) -> str:
    return GOAL_MODE_BASKET_RULES.get(
        (goal_type, investment_mode),
        MODE_FALLBACK_RULES.get(investment_mode, "moderate"),
    )


def build_recommendation_baskets(goal_type: str, investment_mode: str) -> dict[str, object]:
    recommended_basket = get_recommended_basket(goal_type, investment_mode)
    recommended_at = datetime.utcnow()

    baskets: list[dict[str, object]] = []
    for basket_type in BASKET_TYPES:
        baskets.append(
            {
                "basket_type": basket_type,
                "recommended": basket_type == recommended_basket,
                "funds": FUNDS_BY_BASKET[basket_type],
            }
        )

    return {
        "recommended_at": recommended_at,
        "baskets": baskets,
    }
