import csv
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_csv_file(filename: str) -> list[dict[str, Any]]:
    file_path = DATA_DIR / filename
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def load_canonical_docs() -> list[dict[str, Any]]:
    return load_csv_file("canonical_docs.csv")


def load_incidents() -> list[dict[str, Any]]:
    return load_csv_file("incidents.csv")


def load_policies() -> list[dict[str, Any]]:
    return load_csv_file("policies.csv")


def load_live_transactions() -> list[dict[str, Any]]:
    records = load_csv_file("live_transactions.csv")

    for record in records:
        if "retry_count" in record and record["retry_count"] != "":
            record["retry_count"] = int(record["retry_count"])
        else:
            record["retry_count"] = 0

    return records