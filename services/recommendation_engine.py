"""
Recommendation Engine with Hardcoded Sample Data
Provides investment baskets without any external API calls
"""
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Basket type constants
BASKET_TYPES = ("conservative", "moderate", "aggressive")

# Rules for selecting recommended basket based on goal type and investment mode
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

# Fallback rules for basket selection by mode
MODE_FALLBACK_RULES: dict[str, str] = {
    "autopilot": "conservative",
    "copilot": "moderate",
    "manual": "aggressive",
}


def get_recommended_basket(goal_type: str, investment_mode: str) -> str:
    """Get the recommended basket type for a goal based on type and investment mode."""
    return GOAL_MODE_BASKET_RULES.get(
        (goal_type, investment_mode),
        MODE_FALLBACK_RULES.get(investment_mode, "moderate"),
    )


class RecommendationEngine:
    """
    Build recommendation baskets using hardcoded sample mutual funds.
    Applies goal type, investment mode, and time horizon constraints.
    """

    # Hardcoded sample mutual funds with realistic Indian fund data
    SAMPLE_FUNDS = {
        "conservative": [
            {
                "scheme_code": "SBI_MAGNUM_GILT",
                "scheme_name": "SBI Magnum Gilt Fund Direct Growth",
                "category": "Debt",
                "fund_house": "SBI",
                "returns_1y": 7.2,
                "returns_3y": 6.8,
                "returns_5y": 7.1,
            },
            {
                "scheme_code": "HDFC_SHORT_DURATION",
                "scheme_name": "HDFC Short Duration Fund Direct Growth",
                "category": "Debt",
                "fund_house": "HDFC",
                "returns_1y": 7.5,
                "returns_3y": 7.1,
                "returns_5y": 7.4,
            },
            {
                "scheme_code": "ICICI_LIQUID",
                "scheme_name": "ICICI Prudential Liquid Fund Direct Growth",
                "category": "Liquid",
                "fund_house": "ICICI Prudential",
                "returns_1y": 6.8,
                "returns_3y": 6.5,
                "returns_5y": 6.7,
            },
        ],
        "moderate": [
            {
                "scheme_code": "MIRAE_LARGE_CAP",
                "scheme_name": "Mirae Asset Large Cap Fund Direct Growth",
                "category": "Large Cap",
                "fund_house": "Mirae Asset",
                "returns_1y": 18.2,
                "returns_3y": 15.6,
                "returns_5y": 16.1,
            },
            {
                "scheme_code": "AXIS_BLUECHIP",
                "scheme_name": "Axis Bluechip Fund Direct Growth",
                "category": "Large Cap",
                "fund_house": "Axis",
                "returns_1y": 16.8,
                "returns_3y": 14.2,
                "returns_5y": 15.3,
            },
            {
                "scheme_code": "HDFC_BALANCED_ADVANTAGE",
                "scheme_name": "HDFC Balanced Advantage Fund Direct Growth",
                "category": "Hybrid",
                "fund_house": "HDFC",
                "returns_1y": 14.5,
                "returns_3y": 13.2,
                "returns_5y": 12.8,
            },
        ],
        "aggressive": [
            {
                "scheme_code": "QUANT_SMALL_CAP",
                "scheme_name": "Quant Small Cap Fund Direct Growth",
                "category": "Small Cap",
                "fund_house": "Quant",
                "returns_1y": 42.3,
                "returns_3y": 38.1,
                "returns_5y": 28.6,
            },
            {
                "scheme_code": "NIPPON_SMALL_CAP",
                "scheme_name": "Nippon India Small Cap Fund Direct Growth",
                "category": "Small Cap",
                "fund_house": "Nippon India",
                "returns_1y": 38.7,
                "returns_3y": 32.4,
                "returns_5y": 24.8,
            },
            {
                "scheme_code": "HDFC_MID_CAP_OPP",
                "scheme_name": "HDFC Mid Cap Opportunities Fund Direct Growth",
                "category": "Mid Cap",
                "fund_house": "HDFC",
                "returns_1y": 31.2,
                "returns_3y": 26.8,
                "returns_5y": 22.1,
            },
        ],
    }

    @staticmethod
    def get_horizon_category(target_date: datetime) -> str:
        """
        Calculate investment horizon based on target date.
        Short: < 36 months, Medium: 36-120 months, Long: > 120 months
        """
        # Convert target_date to datetime if it's a date object
        if isinstance(target_date, datetime):
            target_datetime = target_date
        else:
            from datetime import date
            if isinstance(target_date, date):
                target_datetime = datetime.combine(target_date, datetime.min.time())
            else:
                target_datetime = target_date

        months_remaining = (target_datetime - datetime.utcnow()).days / 30.44

        if months_remaining < 36:
            return "short"
        elif months_remaining < 120:
            return "medium"
        else:
            return "long"

    @staticmethod
    async def build_recommendation_baskets_dynamic(
        db: AsyncSession,
        goal_type: str,
        investment_mode: str,
        target_date: datetime,
        use_real_data: bool = True,
        as_of_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Build recommendation baskets using hardcoded sample data.
        Applies time horizon constraints to basket selection.

        Args:
            db: AsyncSession (not used with hardcoded data)
            goal_type: Goal type (retirement, house, education, wealth)
            investment_mode: Mode (autopilot, copilot, manual)
            target_date: Goal target date for horizon calculation
            use_real_data: (ignored - always uses hardcoded data)
            as_of_date: (unused with hardcoded data)

        Returns:
            Dict with baskets and metadata
        """
        try:
            recommended_basket = get_recommended_basket(goal_type, investment_mode)
            recommended_at = datetime.utcnow()
            horizon = RecommendationEngine.get_horizon_category(target_date)

            baskets: List[Dict[str, Any]] = []
            horizon_note = None

            # Apply horizon-based constraints
            if horizon == "short":
                # Short horizon: only conservative basket
                basket_types_to_show = ["conservative"]
                horizon_note = "Short investment horizon — equity not recommended"
            elif horizon == "medium":
                # Medium horizon: all baskets but cap aggressive
                basket_types_to_show = BASKET_TYPES
                horizon_note = "Medium horizon — moderate equity allocation recommended"
            else:
                # Long horizon: full equity allowed
                basket_types_to_show = BASKET_TYPES
                horizon_note = None

            for basket_type in BASKET_TYPES:
                if basket_type not in basket_types_to_show:
                    # Skip baskets not recommended for this horizon
                    baskets.append(
                        {
                            "basket_type": basket_type,
                            "recommended": False,
                            "funds": [],
                            "data_source": "hidden_by_horizon",
                            "hidden_reason": f"Not suitable for {horizon}-term horizon",
                        }
                    )
                    continue

                # Get hardcoded funds for this basket type
                funds = RecommendationEngine.SAMPLE_FUNDS.get(basket_type, [])
                
                # Add basket_type to each fund for schema compliance
                funds_with_basket = [
                    {**fund, "basket_type": basket_type}
                    for fund in funds
                ]

                # For medium horizon, cap aggressive basket to 50%
                if horizon == "medium" and basket_type == "aggressive":
                    aggressive_limit = max(1, len(funds_with_basket) // 2)
                    funds_with_basket = funds_with_basket[:aggressive_limit]

                # Determine if this basket is recommended
                is_recommended = basket_type == recommended_basket

                baskets.append(
                    {
                        "basket_type": basket_type,
                        "recommended": is_recommended,
                        "funds": funds_with_basket,
                        "data_source": "hardcoded_sample",
                    }
                )

            return {
                "recommended_at": recommended_at,
                "baskets": baskets,
                "horizon": horizon,
                "horizon_note": horizon_note,
            }

        except Exception as e:
            logger.error(f"Error in build_recommendation_baskets_dynamic: {e}")
            raise
