import streamlit as st
from src.db import init_db, get_all_matches, get_needs_clarification, resolve_match

st.set_page_config(page_title="Reconcile", page_icon="🧾", layout="wide")

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #0a0a0f; }

    .hero {
        text-align: center;
        padding: 40px 0 20px 0;
    }
    .hero h1 {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(90deg, #ffffff, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
    .hero p {
        color: #9d9db8;
        font-size: 16px;
    }

    .stat-card {
        background: radial-gradient(circle at top, rgba(139,92,246,0.15), #14141f 70%);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        border: 1px solid #2a2440;
        box-shadow: 0 0 30px rgba(139,92,246,0.05);
    }
    .stat-number { font-size: 36px; font-weight: 800; color: #fff; }
    .stat-label { font-size: 13px; color: #9d9db8; margin-top: 6px; letter-spacing: 0.5px; text-transform: uppercase; }

    .txn-card {
        background: #14141f;
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 12px;
        border: 1px solid #262238;
        transition: border 0.2s;
    }
    .txn-card:hover { border: 1px solid #8b5cf6; }
    .txn-matched { border-left: 3px solid #22c55e; }
    .txn-clarify { border-left: 3px solid #a78bfa; }
    .txn-nomatch { border-left: 3px solid #ef4444; }

    .txn-title { font-weight: 700; font-size: 15px; color: #fff; }
    .txn-meta { color: #9d9db8; font-size: 13px; margin-top: 2px; }
    .txn-note { font-size: 13px; margin-top: 8px; }

    .stButton>button {
        background: linear-gradient(90deg, #7c3aed, #a78bfa);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 6px 16px;
    }
    div[data-testid="stTabs"] button { font-weight: 600; }
</style>
""",
    unsafe_allow_html=True,
)

init_db()

st.markdown(
    """
<div class="hero">
    <h1>🧾 Reconcile</h1>
    <p>Automated receipt-to-transaction matching, with a human in the loop only when it matters.</p>
</div>
""",
    unsafe_allow_html=True,
)

all_matches = get_all_matches()
needs_review = get_needs_clarification()
matched = [m for m in all_matches if m["decision"] == "matched"]
no_match = [m for m in all_matches if m["decision"] == "no_match"]

col1, col2, col3, col4 = st.columns(4)
stats = [
    (len(all_matches), "Total Transactions", "#fff"),
    (len(matched), "Matched", "#22c55e"),
    (len(needs_review), "Needs Review", "#a78bfa"),
    (len(no_match), "No Receipt", "#ef4444"),
]
for col, (num, label, color) in zip([col1, col2, col3, col4], stats):
    with col:
        st.markdown(
            f'<div class="stat-card"><div class="stat-number" style="color:{color}">{num}</div><div class="stat-label">{label}</div></div>',
            unsafe_allow_html=True,
        )

st.write("")

tab1, tab2, tab3 = st.tabs(["⚠️ Needs Review", "✅ Matched", "❌ No Receipt"])

with tab1:
    if not needs_review:
        st.success("Nothing needs review right now.")
    for m in needs_review:
        with st.container():
            st.markdown(
                f"""
            <div class="txn-card txn-clarify">
                <div class="txn-title">{m["transaction_desc"]}</div>
                <div class="txn-meta">${m["transaction_amount"]} · {m["transaction_date"]}</div>
                <div class="txn-note" style="color:#a78bfa">❓ {m["clarifying_question"]}</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            c1, c2 = st.columns([3, 1])
            with c1:
                receipt_choice = st.text_input(
                    "Confirm receipt ID", key=f"input_{m['id']}", placeholder="e.g. r1"
                )
            with c2:
                st.write("")
                if st.button("Resolve", key=f"resolve_{m['id']}"):
                    if receipt_choice:
                        resolve_match(m["id"], receipt_choice)
                        st.rerun()

with tab2:
    for m in matched:
        st.markdown(
            f"""
        <div class="txn-card txn-matched">
            <div class="txn-title">{m["transaction_desc"]}</div>
            <div class="txn-meta">${m["transaction_amount"]} · {m["transaction_date"]}</div>
            <div class="txn-note" style="color:#22c55e">✅ Matched to receipt {m["receipt_id"]} ({m["confidence"]} confidence)</div>
            <div class="txn-meta" style="margin-top:4px">{m["reasoning"]}</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

with tab3:
    for m in no_match:
        st.markdown(
            f"""
        <div class="txn-card txn-nomatch">
            <div class="txn-title">{m["transaction_desc"]}</div>
            <div class="txn-meta">${m["transaction_amount"]} · {m["transaction_date"]}</div>
            <div class="txn-note" style="color:#ef4444">❌ No matching receipt found</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
