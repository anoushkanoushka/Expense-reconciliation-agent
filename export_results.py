import json
from src.db import get_all_matches

matches = get_all_matches()
with open("results.json", "w") as f:
    json.dump(matches, f, indent=2)

print(f"Exported {len(matches)} results to results.json")
