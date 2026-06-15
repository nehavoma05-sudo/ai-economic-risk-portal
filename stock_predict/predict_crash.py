import json
import os
import pickle
from datetime import datetime

import pandas as pd


MODEL_FILE = os.path.join("stock_predict", "models", "crash_model.pkl")
FEATURE_COLUMNS_FILE = os.path.join("stock_predict", "models", "crash_feature_columns.pkl")


def load_pickle_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Required file not found: {file_path}")

    with open(file_path, "rb") as file:
        return pickle.load(file)


def get_risk_level(probability):
    if probability < 0.30:
        return "LOW"
    if probability < 0.60:
        return "MEDIUM"
    if probability < 0.80:
        return "HIGH"
    return "EXTREME"


def get_market_alert(risk_level):
    alerts = {
        "LOW": "Market conditions appear stable",
        "MEDIUM": "Market volatility is increasing",
        "HIGH": "Possible market correction warning",
        "EXTREME": "High probability of market crash",
    }
    return alerts[risk_level]


def generate_reasons(input_data):
    reasons = []

    if input_data.get("india_vix", 0) >= 15:
        reasons.append("India VIX is elevated")

    if input_data.get("nifty_daily_return", 0) <= -1:
        reasons.append("Nifty daily return is strongly negative")

    if input_data.get("nifty_7_day_return", 0) < 0:
        reasons.append("Nifty 7-day return is negative")

    if input_data.get("crude_oil_price", 0) >= 80:
        reasons.append("Crude oil price is high")

    if input_data.get("usd_inr", 0) >= 94.5:
        reasons.append("USD/INR is rising")

    if input_data.get("inflation", 0) >= 5:
        reasons.append("Inflation is elevated")

    if input_data.get("war_score", 0) >= 0.60:
        reasons.append("War score is high")

    if input_data.get("shipping_score", 0) >= 0.50:
        reasons.append("Shipping disruption risk is high")

    if input_data.get("news_sentiment", 0) < 0:
        reasons.append("News sentiment is negative")

    if input_data.get("fii_dii_flow", 0) <= -3000:
        reasons.append("Strong FII outflows detected")

    return reasons


def predict_crash_risk(input_data):
    try:
        model = load_pickle_file(MODEL_FILE)
        feature_columns = load_pickle_file(FEATURE_COLUMNS_FILE)

        missing_features = [
            feature for feature in feature_columns if feature not in input_data
        ]
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")

        ordered_input = {
            feature: input_data[feature] for feature in feature_columns
        }
        input_dataframe = pd.DataFrame([ordered_input], columns=feature_columns)

        probability = float(model.predict(input_dataframe)[0])
        probability = max(0, min(1, probability))
        probability = round(probability, 2)

        risk_level = get_risk_level(probability)

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "crash_probability": probability,
            "crash_risk_level": risk_level,
            "market_alert": get_market_alert(risk_level),
            "reason": generate_reasons(input_data),
        }

    except Exception as error:
        return {
            "error": str(error),
        }


if __name__ == "__main__":
    sample_input = {
    "nifty_50_price": 25250.40,
    "sensex_price": 82950.80,

    "nifty_daily_return": 0.85,
    "nifty_7_day_return": 2.40,
    "nifty_30_day_return": 5.80,

    "india_vix": 11.20,

    "usd_inr": 83.10,

    "crude_oil_price": 68.50,
    "gold_price": 2250.00,

    "fii_dii_flow": 3250.75,

    "repo_rate": 6.00,
    "inflation": 3.90,

    "war_score": 0.15,
    "shipping_score": 0.10,

    "news_sentiment": 0.65,
}

    result = predict_crash_risk(sample_input)
    print(json.dumps(result, indent=4))