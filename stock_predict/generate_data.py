from datetime import datetime, timedelta
import random

import numpy as np
import pandas as pd


ROWS = 10000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2026, 5, 29)
OUTPUT_FILE = "stock_crash_dataset.csv"


REFERENCE_SAMPLES = {
    "high": {
        "nifty_50_price": 23547.75,
        "sensex_price": 74775.74,
        "nifty_daily_return": -1.50,
        "nifty_7_day_return": -2.10,
        "nifty_30_day_return": -1.80,
        "india_vix": 16.85,
        "usd_inr": 94.88,
        "crude_oil_price": 72.50,
        "gold_price": 2350.00,
        "fii_dii_flow": -4341.72,
        "repo_rate": 6.50,
        "inflation": 4.85,
        "war_score": 0.65,
        "shipping_score": 0.55,
        "news_sentiment": -0.75,
    },
    "low": {
        "nifty_50_price": 24150.00,
        "sensex_price": 76820.50,
        "nifty_daily_return": 1.15,
        "nifty_7_day_return": 1.85,
        "nifty_30_day_return": 3.20,
        "india_vix": 12.10,
        "usd_inr": 94.15,
        "crude_oil_price": 76.80,
        "gold_price": 2310.00,
        "fii_dii_flow": 5495.80,
        "repo_rate": 6.50,
        "inflation": 4.70,
        "war_score": 0.20,
        "shipping_score": 0.15,
        "news_sentiment": 0.60,
    },
    "medium": {
        "nifty_50_price": 23907.15,
        "sensex_price": 75867.80,
        "nifty_daily_return": -0.34,
        "nifty_7_day_return": 0.45,
        "nifty_30_day_return": 1.10,
        "india_vix": 13.40,
        "usd_inr": 94.55,
        "crude_oil_price": 74.20,
        "gold_price": 2335.00,
        "fii_dii_flow": -1046.50,
        "repo_rate": 6.50,
        "inflation": 4.80,
        "war_score": 0.35,
        "shipping_score": 0.25,
        "news_sentiment": -0.10,
    },
}
NOISE = {
    "high": {
        "nifty_50_price": 450,
        "sensex_price": 1400,
        "nifty_daily_return": 0.65,
        "nifty_7_day_return": 0.90,
        "nifty_30_day_return": 1.25,
        "india_vix": 2.70,
        "usd_inr": 0.45,
        "crude_oil_price": 5.50,
        "gold_price": 80,
        "fii_dii_flow": 2600,
        "repo_rate": 0.15,
        "inflation": 0.35,
        "war_score": 0.16,
        "shipping_score": 0.16,
        "news_sentiment": 0.22,
    },
    "low": {
        "nifty_50_price": 520,
        "sensex_price": 1600,
        "nifty_daily_return": 0.55,
        "nifty_7_day_return": 0.85,
        "nifty_30_day_return": 1.35,
        "india_vix": 1.60,
        "usd_inr": 0.35,
        "crude_oil_price": 4.80,
        "gold_price": 65,
        "fii_dii_flow": 2400,
        "repo_rate": 0.15,
        "inflation": 0.30,
        "war_score": 0.10,
        "shipping_score": 0.09,
        "news_sentiment": 0.24,
    },
    "medium": {
        "nifty_50_price": 480,
        "sensex_price": 1500,
        "nifty_daily_return": 0.55,
        "nifty_7_day_return": 0.85,
        "nifty_30_day_return": 1.15,
        "india_vix": 2.00,
        "usd_inr": 0.40,
        "crude_oil_price": 5.00,
        "gold_price": 70,
        "fii_dii_flow": 2200,
        "repo_rate": 0.15,
        "inflation": 0.30,
        "war_score": 0.12,
        "shipping_score": 0.11,
        "news_sentiment": 0.28,
    },
}
def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def random_date():
    days_between = (END_DATE - START_DATE).days
    return START_DATE + timedelta(days=random.randint(0, days_between))


def noisy_value(pattern, column):
    base_value = REFERENCE_SAMPLES[pattern][column]
    noise = NOISE[pattern][column]
    return base_value + np.random.normal(0, noise)
def calculate_crash_probability(row):
    score = 0.05

    score += max(0, -row["nifty_daily_return"]) * 0.12
    score += max(0, -row["nifty_7_day_return"]) * 0.07
    score += max(0, -row["nifty_30_day_return"]) * 0.05
    score += max(0, row["india_vix"] - 12) * 0.035
    score += max(0, row["usd_inr"] - 94) * 0.09
    score += max(0, row["crude_oil_price"] - 72) * 0.012
    score += max(0, row["gold_price"] - 2300) * 0.0012
    score += max(0, -row["fii_dii_flow"]) / 12000
    score += max(0, row["inflation"] - 4.5) * 0.10
    score += row["war_score"] * 0.22
    score += row["shipping_score"] * 0.16
    score += max(0, -row["news_sentiment"]) * 0.18

    score += np.random.normal(0, 0.05)
    return clamp(score, 0, 1)

def generate_row():
    pattern = random.choices(
        ["low", "medium", "high"],
        weights=[0.55, 0.30, 0.15],
        k=1,
    )[0]

    row = {
        "date": random_date().date().isoformat(),
        "nifty_50_price": noisy_value(pattern, "nifty_50_price"),
        "sensex_price": noisy_value(pattern, "sensex_price"),
        "nifty_daily_return": noisy_value(pattern, "nifty_daily_return"),
        "nifty_7_day_return": noisy_value(pattern, "nifty_7_day_return"),
        "nifty_30_day_return": noisy_value(pattern, "nifty_30_day_return"),
        "india_vix": noisy_value(pattern, "india_vix"),
        "usd_inr": noisy_value(pattern, "usd_inr"),
        "crude_oil_price": noisy_value(pattern, "crude_oil_price"),
        "gold_price": noisy_value(pattern, "gold_price"),
        "fii_dii_flow": noisy_value(pattern, "fii_dii_flow"),
        "repo_rate": noisy_value(pattern, "repo_rate"),
        "inflation": noisy_value(pattern, "inflation"),
        "war_score": noisy_value(pattern, "war_score"),
        "shipping_score": noisy_value(pattern, "shipping_score"),
        "news_sentiment": noisy_value(pattern, "news_sentiment"),
    }

    row["nifty_50_price"] = clamp(row["nifty_50_price"], 19000, 27000)
    row["sensex_price"] = clamp(row["sensex_price"], 61000, 86000)
    row["nifty_daily_return"] = clamp(row["nifty_daily_return"], -5, 4)
    row["nifty_7_day_return"] = clamp(row["nifty_7_day_return"], -9, 8)
    row["nifty_30_day_return"] = clamp(row["nifty_30_day_return"], -14, 14)
    row["india_vix"] = clamp(row["india_vix"], 9, 30)
    row["usd_inr"] = clamp(row["usd_inr"], 82, 98)
    row["crude_oil_price"] = clamp(row["crude_oil_price"], 55, 105)
    row["gold_price"] = clamp(row["gold_price"], 1850, 2700)
    row["fii_dii_flow"] = clamp(row["fii_dii_flow"], -12000, 12000)
    row["repo_rate"] = clamp(row["repo_rate"], 5.75, 7.25)
    row["inflation"] = clamp(row["inflation"], 3.5, 7.5)
    row["war_score"] = clamp(row["war_score"], 0, 1)
    row["shipping_score"] = clamp(row["shipping_score"], 0, 1)
    row["news_sentiment"] = clamp(row["news_sentiment"], -1, 1)

    row["crash_probability"] = calculate_crash_probability(row)
    row["stock_crash_label"] = 1 if row["crash_probability"] >= 0.60 else 0

    return row

def main():
    random.seed(42)
    np.random.seed(42)

    rows = [generate_row() for _ in range(ROWS)]
    dataset = pd.DataFrame(rows)

    numeric_columns = [
        "nifty_50_price",
        "sensex_price",
        "nifty_daily_return",
        "nifty_7_day_return",
        "nifty_30_day_return",
        "india_vix",
        "usd_inr",
        "crude_oil_price",
        "gold_price",
        "fii_dii_flow",
        "repo_rate",
        "inflation",
        "war_score",
        "shipping_score",
        "news_sentiment",
        "crash_probability",
    ]
    dataset[numeric_columns] = dataset[numeric_columns].round(2)

    dataset = dataset[
        [
            "date",
            "nifty_50_price",
            "sensex_price",
            "nifty_daily_return",
            "nifty_7_day_return",
            "nifty_30_day_return",
            "india_vix",
            "usd_inr",
            "crude_oil_price",
            "gold_price",
            "fii_dii_flow",
            "repo_rate",
            "inflation",
            "war_score",
            "shipping_score",
            "news_sentiment",
            "crash_probability",
            "stock_crash_label",
        ]
    ]

    dataset.to_csv(OUTPUT_FILE, index=False)

    print(dataset.head(10))
    print("Dataset shape:", dataset.shape)
    print("Label distribution:")
    print(dataset["stock_crash_label"].value_counts())


if __name__ == "__main__":
    main()