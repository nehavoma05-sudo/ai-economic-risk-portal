import importlib.util
from pathlib import Path
import sys

import yfinance as yf
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

sys.path.append(str(PROJECT_ROOT))
from gas_predicition.predict import predict



def load_weighted_scores_function():
    module_path = Path("C:/Users/HP/economic-ai/budget_planner/avg_7.py")

    if not module_path.exists():
        raise FileNotFoundError(f"avg_7.py not found at {module_path}")

    module_spec = importlib.util.spec_from_file_location(
        "budget_planner.seven_day_avg",
        module_path
    )

    if module_spec is None or module_spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")

    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)

    return module.get_7_day_weighted_scores


def get_latest_gold_price():
    try:
        gold_data = yf.Ticker("GC=F").history(period="5d")
        closing_prices = gold_data["Close"].dropna()

        if closing_prices.empty:
            raise ValueError("No gold price data returned for GC=F")

        return float(closing_prices.iloc[-1])

    except Exception as error:
        print(f"Error fetching latest gold price: {error}")
        return None


def safe_float(value, default=0):
    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def predict_next_month_impact():
    try:
        get_7_day_weighted_scores = load_weighted_scores_function()
        weighted_scores = get_7_day_weighted_scores()

        if not weighted_scores or weighted_scores.get("days_used", 0) == 0:
            raise ValueError("No daily average data found for last 7 days")

        gold_price = get_latest_gold_price()

        model_input = {
            "war_score": safe_float(weighted_scores.get("weighted_war_score")),
            "oil_price": safe_float(weighted_scores.get("weighted_oil_price")),
            "usd_inr": safe_float(weighted_scores.get("weighted_usd_inr")),
            "shipping_score": safe_float(
                weighted_scores.get("weighted_shipping_score")
            ),
            "gold_price": safe_float(gold_price),
        }

        prediction = predict(model_input)

        return {
            "petrol_rise": round(
                safe_float(prediction.get("petrol_rise")), 2
            ),
            "diesel_rise": round(
                safe_float(prediction.get("diesel_rise")), 2
            ),
            "lpg_rise": round(
                safe_float(prediction.get("lpg_rise")), 2
            ),
            "rupee_change": round(
                safe_float(prediction.get("rupee_change")), 2
            ),
            "inflation_percent": round(
                safe_float(prediction.get("inflation")), 2
            )
        }

    except Exception as error:
        print(f"Error predicting next month impact: {error}")
        return {}


if __name__ == "__main__":
    result = predict_next_month_impact()
    print(result)