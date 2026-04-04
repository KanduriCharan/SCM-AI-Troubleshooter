from typing import Optional
from app.retrieval.data_loader import load_live_transactions


def get_transaction_by_id(transaction_id: str | None) -> Optional[dict]:
    if not transaction_id:
        return None

    transactions = load_live_transactions()

    for tx in transactions:
        if tx["transaction_id"] == transaction_id:
            return tx

    return None