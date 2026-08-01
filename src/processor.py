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
    original_vendor_raw = transaction.get("vendor_raw", "")
    transaction = apply_alias(transaction)

    prompt = MATCH_PROMPT.format(
        transaction=json.dumps(transaction), candidates=json.dumps(candidates)
    )

    try:
        response = client.models.generate_content(
            model="gemini-flash-lite-latest", contents=prompt
        )
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
    except Exception as e:
        # If the model call fails or returns something we can't parse,
        # don't guess — flag it for a human rather than crashing the batch.
        return {
            "decision": "needs_clarification",
            "receipt_id": None,
            "confidence": "low",
            "clarifying_question": (
                "The matching model didn't return a usable response for this "
                "transaction — can you check it manually?"
            ),
            "reasoning": (
                f"Automated matching failed ({type(e).__name__}: {e}); "
                "flagged for manual review instead of guessing."
            ),
        }

    # Learn from confident matches: if this raw bank string hasn't been
    # aliased yet, remember the real vendor name from the matched receipt.
    # Recurring vendors (subscriptions, regular coffee runs, etc.) reuse the
    # exact same raw descriptor every cycle, so this makes future matches
    # for that vendor faster and more reliable without needing a human.
    if (
        result.get("decision") == "matched"
        and result.get("confidence") == "high"
        and original_vendor_raw
        and original_vendor_raw not in load_aliases()
    ):
        matched_receipt = next(
            (c for c in candidates if c.get("id") == result.get("receipt_id")), None
        )
        if matched_receipt and matched_receipt.get("vendor"):
            save_alias(original_vendor_raw, matched_receipt["vendor"])

    return result


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
    # Not yet called from main.py / app.py — wired for a future tax-categorization pass.
    prompt = CATEGORIZE_PROMPT.format(vendor=vendor, amount=amount, date=date)
    try:
        response = client.models.generate_content(
            model="gemini-flash-lite-latest", contents=prompt
        )
        text = response.text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        return {
            "category": "Uncategorized",
            "deductible_pct": 0,
            "flag_for_review": True,
            "flag_reason": f"Categorization failed ({type(e).__name__}); needs manual review.",
        }
