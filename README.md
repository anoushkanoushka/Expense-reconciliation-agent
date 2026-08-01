# 🧾 Reconcile: AI Expense Reconciliation Agent

An agentic tool that matches bank transactions to receipts automatically, asks a clarifying question only when genuinely ambiguous, and remembers vendor aliases so it never asks the same question twice.

**[Live demo](https://anoushkanoushka.github.io/Expense-reconciliation-agent/)**

## The problem

Small businesses and freelancers spend hours matching receipts to bank statements for bookkeeping and taxes, or they just don't, and panic at tax time. Existing tools either require manual review of every transaction, or auto-match everything with no way to catch mistakes.

## The approach

Rather than blindly auto-matching every transaction, the core agent scores each bank transaction against candidate receipts on three dimensions: amount, date proximity, and vendor name similarity. It only takes one of three actions:

- **Matched**: one candidate is clearly correct, matched automatically
- **No match**: no receipt exists for this transaction
- **Needs clarification**: two or more candidates are plausible, so it asks a specific, answerable question instead of guessing

This "ask only when it matters" design is deliberate. A wrong auto-match is worse than an extra question, so the system is tuned to be conservative.

## The learning loop

The most important piece: every time a human resolves an ambiguous case, the vendor name mapping (for example, "SQ *JOES DINER" to "Joe's Diner") is saved to an alias table. The next time that same vendor string appears, it resolves automatically. The system gets less annoying to use over time instead of asking the same question forever.

## Architecture**Stack:**
- **LLM:** Google Gemini API (free tier), used for matching and categorization reasoning
- **Data processing:** pandas, for bank CSV normalization
- **Storage:** SQLite, for persistent match history and audit trail
- **Review UI:** Streamlit, an interactive dashboard to resolve ambiguous cases
- **Showcase site:** static HTML, CSS, and JS in `index.html`, deployed via GitHub Pages

## What it does end to end

1. Parses a bank statement CSV into a standard schema
2. For each transaction, filters candidate receipts within a date window
3. Sends the transaction and candidates to the LLM with a structured prompt requiring one of three JSON decisions
4. Applies known vendor aliases before matching, to avoid re-asking resolved ambiguities
5. Persists every decision, plus reasoning for audit purposes, to SQLite
6. Surfaces ambiguous cases in a dashboard where a human can resolve them in one click, which updates the alias table for next time

## Example: the learning loop in action

A transaction from "WM SUPERCENTER #3312" initially returned `no_match`, since the model didn't confidently connect the abbreviation to the receipt vendor "Walmart Supercenter." After manually confirming the alias once, the identical transaction pattern now resolves automatically on every future run.

## Tested on

25 synthetic but realistic transactions with deliberate edge cases: near duplicate vendors (two similarly named restaurants on the same day, for testing ambiguity), a refund, and several transactions with no corresponding receipt.

## Known limitations

- Receipt data is currently structured JSON, not photos. OCR or vision based receipt extraction (using Gemini's multimodal capability) is a planned next step.
- Tested on synthetic data, not a live bank feed.
- No automated test suite yet.

## Running it locally

```bash
pip install -r requirements.txt
# Add your Gemini API key as an environment variable: GEMINI_API_KEY
python3 -m src.main          # run the matching pipeline
streamlit run app.py         # launch the review dashboard
```

## Built with

Claude (Anthropic), for architecture and debugging assistance, and the Google Gemini API (free tier), for the LLM reasoning layer.
