from pathlib import Path
from typing import Any

import joblib
import pandas as pd


ML_DIR = Path(__file__).resolve().parent
DATA_DIR = ML_DIR.parent / "data"

MODEL_PATH = ML_DIR / "risk_model.pkl"
CURRENT_SHIPMENTS_PATH = DATA_DIR / "current_shipments.csv"


def load_model_bundle() -> dict[str, Any]:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def load_current_shipments() -> pd.DataFrame:
    if not CURRENT_SHIPMENTS_PATH.exists():
        raise FileNotFoundError(f"Current shipments file not found: {CURRENT_SHIPMENTS_PATH}")
    return pd.read_csv(CURRENT_SHIPMENTS_PATH)


def predict_shipment_risk(shipment_id: str) -> dict[str, Any]:
    bundle = load_model_bundle()
    model = bundle["model"]
    feature_columns = bundle["feature_columns"]

    shipments_df = load_current_shipments()

    shipment_rows = shipments_df[shipments_df["shipment_id"] == shipment_id]

    if shipment_rows.empty:
        raise ValueError(f"Shipment ID not found: {shipment_id}")

    shipment = shipment_rows.iloc[0]
    X = shipment_rows[feature_columns]

    predicted_risk = model.predict(X)[0]

    probabilities = {}
    if hasattr(model, "predict_proba"):
        probability_values = model.predict_proba(X)[0]
        probabilities = {
            class_name: round(float(probability), 3)
            for class_name, probability in zip(model.classes_, probability_values)
        }

    return {
        "shipment_id": shipment_id,
        "predicted_risk": predicted_risk,
        "risk_probabilities": probabilities,
        "shipment_snapshot": shipment.to_dict(),
    }