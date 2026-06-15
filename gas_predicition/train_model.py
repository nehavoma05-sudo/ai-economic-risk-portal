import os
import pickle

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


DATASET_FILE = r"C:\Users\HP\economic-ai\gas_predicition\middle_east.csv"
MODEL_DIR = "models"
RANDOM_SEED = 42

FEATURE_COLUMNS = [
    "war_score",
    "oil_price",
    "usd_inr",
    "shipping_score",
    "gold_price",
]

TARGET_MODELS = {
    "petrol_rise": "petrol_model.pkl",
    "diesel_rise": "diesel_model.pkl",
    "lpg_rise": "lpg_model.pkl",
    "rupee_change": "rupee_model.pkl",
    "inflation": "inflation_model.pkl",
}


def validate_columns(df):
    required_columns = ["date"] + FEATURE_COLUMNS + list(TARGET_MODELS.keys())
    missing_columns = [column for column in required_columns if column not in df.columns]

    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: " + ", ".join(missing_columns)
        )


def main():
    if not os.path.exists(DATASET_FILE):
        print(f"Error: Dataset file not found: {DATASET_FILE}")
        return

    df = pd.read_csv(DATASET_FILE)
    validate_columns(df)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    X = df[FEATURE_COLUMNS]
    os.makedirs(MODEL_DIR, exist_ok=True)

    for target_column, model_filename in TARGET_MODELS.items():
        y = df[target_column]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=RANDOM_SEED,
        )

        model = RandomForestRegressor(
            n_estimators=200,
            random_state=RANDOM_SEED,
            n_jobs=-1,
        )
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)

        print(f"\nTarget: {target_column}")
        print(f"MAE:  {mae:.4f}")
        print(f"RMSE: {rmse:.4f}")
        print(f"R2:   {r2:.4f}")

        model_path = os.path.join(MODEL_DIR, model_filename)
        with open(model_path, "wb") as file:
            pickle.dump(model, file)

    feature_columns_path = os.path.join(MODEL_DIR, "feature_columns.pkl")
    with open(feature_columns_path, "wb") as file:
        pickle.dump(FEATURE_COLUMNS, file)

    print("\nSuccess: All models and feature column order saved.")


if __name__ == "__main__":
    main()