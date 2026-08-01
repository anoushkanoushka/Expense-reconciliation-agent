import json
import time
import pandas as pd
from src.normalize import load_statement
from src.processor import match_transaction
from src.db import init_db, save_match


def load_receipts(filepath: str) -> list:
    with open(filepath) as f:
        return json.load(f)


def find_candidates(transaction: dict, receipts: list, day_window: int = 5) -> list:
    t_date = pd.to_datetime(transaction["date"])
    candidates = []
    for r in receipts:
        r_date = pd.to_datetime(r["date"])
        if abs((t_date - r_date).days) <= day_window:
            candidates.append(r)
    return candidates


if __name__ == "__main__":
    init_db()
    statement = load_statement("data/test_statement.csv")
    receipts = load_receipts("data/receipts.json")

    results = []
    for i, (_, row) in enumerate(statement.iterrows()):
        transaction = {
            "date": row["date"],
            "amount": abs(row["amount"]),
            "description": row["description"],
            "vendor_raw": row["description"],
        }
        candidates = find_candidates(transaction, receipts)
        result = match_transaction(transaction, candidates)
        result["transaction_date"] = row["date"]
        result["transaction_desc"] = row["description"]
        result["transaction_amount"] = row["amount"]
        results.append(result)
        save_match(result)
        print(f"[{i + 1}/{len(statement)}] {row['description']} -> {result['decision']}")

        time.sleep(13)  # stay under free-tier 5 requests/minute limit

    print("\n--- Full results ---")
    for r in results:
        print(json.dumps(r, indent=2))
        print("---")
