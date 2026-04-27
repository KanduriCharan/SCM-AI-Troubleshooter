from pathlib import Path
from datetime import datetime, timedelta
import random

import numpy as np
import pandas as pd


DATA_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = DATA_DIR / "current_shipments.csv"

random.seed(42)
np.random.seed(42)


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


def generate_current_shipments(row_count: int = 100):
    origins = ["Los Angeles", "Dallas", "Chicago", "Atlanta", "New York", "Seattle"]
    destinations = ["Phoenix", "Houston", "Miami", "Denver", "Boston", "San Francisco"]
    carriers = ["FedEx", "UPS", "DHL", "XPO Logistics", "J.B. Hunt"]
    statuses = ["In Transit", "Dispatched", "At Port", "Customs Review", "Warehouse Processing"]
    priorities = ["Normal", "High", "Critical"]
    modes = ["Truck", "Air", "Rail", "Ocean"]

    rows = []

    for i in range(row_count):
        priority = random.choices(priorities, weights=[0.6, 0.3, 0.1])[0]
        shipment_mode = random.choice(modes)

        traffic = np.random.uniform(1, 10)
        weather = np.random.uniform(1, 10)
        route_risk = np.random.uniform(1, 10)
        supplier_reliability = np.random.uniform(1, 10)
        warehouse_inventory = np.random.uniform(1, 10)
        equipment_availability = np.random.uniform(1, 10)
        customs_time = np.random.uniform(0.5, 8)
        lead_time = np.random.uniform(1, 15)

        rows.append({
            "shipment_id": f"SHP-{1000 + i}",
            "order_id": f"ORD-{5000 + i}",
            "customer_name": f"Customer {i + 1}",
            "origin_city": random.choice(origins),
            "destination_city": random.choice(destinations),
            "carrier": random.choice(carriers),
            "shipment_status": random.choice(statuses),
            "priority": priority,
            "shipment_mode": shipment_mode,

            # Model feature columns
            "fuel_consumption_rate": round(np.random.uniform(5, 22), 2),
            "eta_variation_hours": round(np.random.uniform(-4, 12), 2),
            "traffic_congestion_level": round(traffic, 2),
            "warehouse_inventory_level": round(warehouse_inventory, 2),
            "loading_unloading_time": round(np.random.uniform(0.5, 8), 2),
            "handling_equipment_availability": round(equipment_availability, 2),
            "weather_condition_severity": round(weather, 2),
            "port_congestion_level": round(np.random.uniform(1, 10), 2),
            "shipping_costs": round(np.random.uniform(300, 8000), 2),
            "supplier_reliability_score": round(supplier_reliability, 2),
            "lead_time_days": round(lead_time, 2),
            "historical_demand": round(np.random.uniform(100, 10000), 2),
            "iot_temperature": round(np.random.uniform(-5, 35), 2),
            "route_risk_level": round(route_risk, 2),
            "customs_clearance_time": round(customs_time, 2),
            "driver_behavior_score": round(np.random.uniform(1, 10), 2),
            "fatigue_monitoring_score": round(np.random.uniform(1, 10), 2),

            # Extra demo context
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "estimated_delivery_time": (
                datetime.now() + timedelta(days=float(lead_time))
            ).isoformat(timespec="seconds"),
        })

    return pd.DataFrame(rows)


def main():
    df = generate_current_shipments(row_count=100)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Generated {len(df)} current shipment records")
    print(f"Saved to: {OUTPUT_PATH}")
    print()
    print(df.head())


if __name__ == "__main__":
    main()