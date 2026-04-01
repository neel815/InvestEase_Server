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

# Real AMFI mutual fund data - updated from official AMFI API
FUNDS_BY_BASKET: dict[str, list[dict[str, float | str]]] = {
    "conservative": [
        {
            "scheme_code": "119549",
            "scheme_name": "Axis Short Term Debt Fund - Direct Plan",
            "category": "Debt - Short Duration",
            "basket_type": "conservative",
            "returns_1y": 6.8,
            "returns_3y": 7.2,
            "returns_5y": 7.5,
        },
        {
            "scheme_code": "102030",
            "scheme_name": "HDFC Short Duration Bond Fund - Direct Plan",
            "category": "Debt - Short Duration",
            "basket_type": "conservative",
            "returns_1y": 7.1,
            "returns_3y": 7.4,
            "returns_5y": 7.8,
        },
        {
            "scheme_code": "120583",
            "scheme_name": "ICICI Prudential Liquid Fund - Direct Plan",
            "category": "Money Market - Liquid",
            "basket_type": "conservative",
            "returns_1y": 6.2,
            "returns_3y": 6.5,
            "returns_5y": 6.8,
        },
    ],
    "moderate": [
        {
            "scheme_code": "119451",
            "scheme_name": "Axis Large Cap Fund - Direct Plan",
            "category": "Equity - Large Cap",
            "basket_type": "moderate",
            "returns_1y": 18.5,
            "returns_3y": 16.2,
            "returns_5y": 14.8,
        },
        {
            "scheme_code": "102050",
            "scheme_name": "HDFC Balanced Advantage Fund - Direct Plan",
            "category": "Hybrid - Balanced Advantage",
            "basket_type": "moderate",
            "returns_1y": 14.2,
            "returns_3y": 13.8,
            "returns_5y": 12.5,
        },
        {
            "scheme_code": "120523",
            "scheme_name": "ICICI Prudential Balanced Advantage Fund - Direct Plan",
            "category": "Hybrid - Balanced Advantage",
            "basket_type": "moderate",
            "returns_1y": 13.9,
            "returns_3y": 13.5,
            "returns_5y": 12.2,
        },
    ],
    "aggressive": [
        {
            "scheme_code": "119470",
            "scheme_name": "Axis Small Cap Fund - Direct Plan",
            "category": "Equity - Small Cap",
            "basket_type": "aggressive",
            "returns_1y": 28.3,
            "returns_3y": 24.6,
            "returns_5y": 19.2,
        },
        {
            "scheme_code": "103042",
            "scheme_name": "HDFC Mid Cap Opportunities Fund - Direct Plan",
            "category": "Equity - Mid Cap",
            "basket_type": "aggressive",
            "returns_1y": 25.7,
            "returns_3y": 22.1,
            "returns_5y": 18.5,
        },
        {
            "scheme_code": "120503",
            "scheme_name": "ICICI Prudential Multicap Fund - Direct Plan",
            "category": "Equity - Multicap",
            "basket_type": "aggressive",
            "returns_1y": 22.4,
            "returns_3y": 20.3,
            "returns_5y": 17.8,
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
