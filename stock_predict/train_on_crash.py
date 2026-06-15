import json
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


DATASET_FILE = r"C:\Users\HP\economic-ai\stock_predict\stock_crash_dataset.csv"

MODELS_DIR = "models"
MODEL_FILE = os.path.join(MODELS_DIR, "crash_model.pkl")
FEATURE_COLUMNS_FILE = os.path.join(MODELS_DIR, "crash_feature_columns.pkl")
METRICS_FILE = os.path.join(MODELS_DIR, "model_metrics.json")

TARGET_COLUMN = "crash_probability"
DROP_COLUMNS = ["date", "stock_crash_label"]

RANDOM_STATE = 42

FEATURE_COLUMNS = [
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
]


def load_dataset():
    if not os.path.exists(DATASET_FILE):
        raise FileNotFoundError(f"Dataset file not found: {DATASET_FILE}")

    return pd.read_csv(DATASET_FILE)


def main():
    try:
        dataset = load_dataset()

        missing_columns = [
            column
            for column in FEATURE_COLUMNS + DROP_COLUMNS + [TARGET_COLUMN]
            if column not in dataset.columns
        ]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        dataset = dataset.drop(columns=DROP_COLUMNS)

        X = dataset[FEATURE_COLUMNS]
        y = dataset[TARGET_COLUMN]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=RANDOM_STATE,
        )

        model = RandomForestRegressor(
            n_estimators=300,
            max_depth=8,
            random_state=RANDOM_STATE,
        )

        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        predictions = np.clip(predictions, 0, 1)

        metrics = {
            "mean_absolute_error": mean_absolute_error(y_test, predictions),
            "mean_squared_error": mean_squared_error(y_test, predictions),
            "root_mean_squared_error": mean_squared_error(
                y_test, predictions
            ) ** 0.5,
            "r2_score": r2_score(y_test, predictions),
        }

        os.makedirs(MODELS_DIR, exist_ok=True)

        with open(MODEL_FILE, "wb") as file:
            pickle.dump(model, file)

        with open(FEATURE_COLUMNS_FILE, "wb") as file:
            pickle.dump(FEATURE_COLUMNS, file)

        with open(METRICS_FILE, "w", encoding="utf-8") as file:
            json.dump(metrics, file, indent=4)

        print("Crash probability regression model trained successfully.")
        print("Model saved to:", MODEL_FILE)
        print("Feature columns saved to:", FEATURE_COLUMNS_FILE)
        print("Metrics saved to:", METRICS_FILE)

        print("\nMetrics:")
        for key, value in metrics.items():
            print(f"{key}: {value:.4f}")

        print("\nTraining Rows:", len(X_train))
        print("Testing Rows:", len(X_test))

    except Exception as error:
        print(f"Training failed: {error}")


if __name__ == "__main__":
    main()