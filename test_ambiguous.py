from src.processor import match_transaction
from src.db import init_db, save_match
import json

init_db()

transaction = {
    "date": "2026-06-16",
    "amount": 19.50,
    "description": "SQ *THAI",
    "vendor_raw": "SQ *THAI",
}
candidates = [
    {"id": "r13", "vendor": "Thai Garden Restaurant", "date": "2026-06-16", "total_amount": 19.50},
    {"id": "r14", "vendor": "Thai Grand Cafe", "date": "2026-06-16", "total_amount": 19.50},
]

result = match_transaction(transaction, candidates)
result["transaction_date"] = transaction["date"]
result["transaction_desc"] = transaction["description"]
result["transaction_amount"] = -transaction["amount"]

print(json.dumps(result, indent=2))
save_match(result)
print("Saved to database.")
