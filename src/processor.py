import os
import json
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MATCH_PROMPT = """You are reconciling one bank transaction against a list of candidate receipts.

Transaction: {transaction}
Candidate receipts: {candidates}

Task:
1. Score each candidate on: amount match (exact/tolerance ±$0.50), date match (same day or ±3 days), vendor name similarity (handle abbreviations like "SQ *JOES" = "Joe's Diner").
2. If exactly one candidate scores high confidence on all three dimensions, return it as the match.
3. If zero candidates are plausible, return "no_match".
4. If two or more candidates are both plausible, or the vendor name is too ambiguous to resolve confidently, return "needs_clarification" with a short, specific question a human could answer in one sentence.

Return ONLY JSON, no preamble, no markdown fences:
{{"decision": "matched" | "no_match" | "needs_clarification",
 "receipt_id": string or null,
 "confidence": "high" | "medium" | "low",
 "clarifying_question": string or null,
 "reasoning": string}}
"""


def match_transaction(transaction: dict, candidates: list) -> dict:
    transaction = apply_alias(transaction)
    prompt = MATCH_PROMPT.format(
        transaction=json.dumps(transaction), candidates=json.dumps(candidates)
    )
    response = client.models.generate_content(model="gemini-flash-lite-latest", contents=prompt)
    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


ALIASES_PATH = "aliases.json"


def load_aliases() -> dict:
    if not os.path.exists(ALIASES_PATH):
        return {}
    with open(ALIASES_PATH, "r") as f:
        return json.load(f)


def save_alias(raw_vendor: str, resolved_vendor: str) -> None:
    aliases = load_aliases()
    aliases[raw_vendor] = resolved_vendor
    with open(ALIASES_PATH, "w") as f:
        json.dump(aliases, f, indent=2)


def apply_alias(transaction: dict) -> dict:
    """If we've seen this raw vendor string before, substitute the resolved name."""
    aliases = load_aliases()
    raw = transaction.get("vendor_raw", "")
    if raw in aliases:
        transaction = {**transaction, "vendor_raw": aliases[raw]}
    return transaction


CATEGORIZE_PROMPT = """Categorize this business expense for tax purposes using Schedule C categories (US).

Transaction: vendor={vendor}, amount={amount}, date={date}

Return ONLY JSON, no preamble, no markdown fences:
{{"category": string, "deductible_pct": number, "flag_for_review": boolean, "flag_reason": string or null}}

Flag for review if: category is ambiguous between personal/business use (meals, home office, mixed-use travel), or amount is unusually large for the vendor type.
"""


def categorize_transaction(vendor: str, amount: float, date: str) -> dict:
    prompt = CATEGORIZE_PROMPT.format(vendor=vendor, amount=amount, date=date)
    response = client.models.generate_content(model="gemini-flash-lite-latest", contents=prompt)
    text = response.text.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(text)
