import json
import pickle
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"

MODEL_FILES = {
    "petrol_rise": "petrol_model.pkl",
    "diesel_rise": "diesel_model.pkl",
    "lpg_rise": "lpg_model.pkl",
    "rupee_change": "rupee_model.pkl",
    "inflation": "inflation_model.pkl",
}

FEATURE_COLUMNS_FILE = "feature_columns.pkl"


def load_pickle_file(file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"Required file not found: {file_path}")

    with open(file_path, "rb") as file:
        return pickle.load(file)


def load_models():
    feature_columns_path = MODEL_DIR / FEATURE_COLUMNS_FILE
    feature_columns = load_pickle_file(feature_columns_path)

    models = {}
    for target_name, model_filename in MODEL_FILES.items():
        model_path = MODEL_DIR / model_filename
        models[target_name] = load_pickle_file(model_path)

    return models, feature_columns


def parse_json_input(json_input):
    if isinstance(json_input, str):
        input_data = json.loads(json_input)
    elif isinstance(json_input, dict):
        input_data = json_input
    else:
        raise ValueError("Input must be a JSON string or a dictionary.")

    if not isinstance(input_data, dict):
        raise ValueError("Invalid JSON input: expected a JSON object.")

    return input_data


def predict(json_input):
    models, feature_columns = load_models()
    input_data = parse_json_input(json_input)

    missing_fields = [
        feature for feature in feature_columns if feature not in input_data
    ]

    if missing_fields:
        raise ValueError("Missing input fields: " + ", ".join(missing_fields))

    ordered_input = {
        feature: input_data[feature]
        for feature in feature_columns
    }

    input_df = pd.DataFrame([ordered_input], columns=feature_columns)

    predictions = {}

    for target_name, model in models.items():
        predicted_value = model.predict(input_df)[0]
        predictions[target_name] = round(float(predicted_value), 2)

    return predictions

if __name__ == "__main__":  
    sample_input = {
        "war_score": 0.8,
        "oil_price": 70.5,
        "usd_inr": 75.3,
        "shipping_score": 0.9,
        "gold_price": 1800.0
    }
    result = predict(sample_input)
    print(json.dumps(result, indent=4)) 


