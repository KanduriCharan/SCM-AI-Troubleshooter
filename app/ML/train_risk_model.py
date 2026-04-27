from pathlib import Path
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "dynamic_supply_chain_logistics_dataset.csv"
MODEL_PATH = Path(__file__).resolve().parent / "risk_model.pkl"


FEATURE_COLUMNS = [

    "fuel_consumption_rate",

    "eta_variation_hours",

    "traffic_congestion_level",

    "warehouse_inventory_level",

    "loading_unloading_time",

    "handling_equipment_availability",

    "weather_condition_severity",

    "port_congestion_level",

    "shipping_costs",

    "supplier_reliability_score",

    "lead_time_days",

    "historical_demand",

    "iot_temperature",

    "route_risk_level",

    "customs_clearance_time",

    "driver_behavior_score",

    "fatigue_monitoring_score",

]

TARGET_COLUMN = "risk_classification"

def main():
    df = pd.read_csv(DATA_PATH)

    # Keep only needed columns
    df = df[FEATURE_COLUMNS + [TARGET_COLUMN]].dropna()

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("Accuracy:", round(accuracy_score(y_test, y_pred), 4))
    print()
    print(classification_report(y_test, y_pred))

    joblib.dump(
        {
            "model": model,
            "feature_columns": FEATURE_COLUMNS,
            "target_column": TARGET_COLUMN,
        },
        MODEL_PATH,
    )

    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()