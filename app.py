import streamlit as st
import pandas as pd

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from engine import diagnose_transaction
from scenarios import SCENARIOS


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Payment State Doctor",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==========================================================
# PRESENTATION CSS
# ==========================================================

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1450px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .hero {
            background: linear-gradient(115deg, #101a38 0%, #243f91 100%);
            border-radius: 0 0 22px 22px;
            padding: 34px 40px;
            margin-bottom: 28px;
            color: white;
            box-shadow: 0 12px 35px rgba(20, 40, 90, 0.16);
        }

        .hero-title {
            font-size: 42px;
            font-weight: 800;
            margin: 0;
            letter-spacing: -1px;
        }

        .hero-subtitle {
            margin-top: 10px;
            font-size: 17px;
            color: #dce7ff;
        }

        .section-title {
            font-size: 25px;
            font-weight: 750;
            margin: 8px 0 20px 0;
            color: #202536;
        }

        .section-subtitle {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 8px;
            color: #303747;
        }

        .verdict {
            border: 1px solid #e6e9f0;
            border-radius: 18px;
            padding: 22px 25px;
            background: #ffffff;
            box-shadow: 0 7px 22px rgba(30, 45, 80, 0.07);
        }

        .verdict-label {
            font-size: 13px;
            font-weight: 800;
            letter-spacing: 1px;
            color: #697386;
            text-transform: uppercase;
        }

        .verdict-title {
            font-size: 27px;
            font-weight: 800;
            margin: 6px 0 10px 0;
        }

        .verdict-text {
            font-size: 16px;
            line-height: 1.55;
            color: #424b5f;
        }

        .action-box {
            background: #f5f8ff;
            border: 1px solid #dce6ff;
            border-radius: 14px;
            padding: 14px 17px;
            margin-top: 15px;
        }

        .state-card {
            border: 1px solid #e5e8ef;
            border-radius: 16px;
            padding: 17px;
            text-align: center;
            background: white;
            box-shadow: 0 5px 16px rgba(30, 45, 80, 0.05);
        }

        .state-name {
            font-size: 13px;
            color: #697386;
            font-weight: 700;
            margin-bottom: 6px;
        }

        .state-value {
            font-size: 21px;
            font-weight: 800;
        }

        .status-pill {
            display: inline-block;
            padding: 5px 11px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: .3px;
        }

        .healthy { background: #e8f8ef; color: #147a42; }
        .mismatch { background: #fdebec; color: #c62839; }
        .anomaly { background: #fff0f2; color: #b4233a; }
        .recoverable { background: #fff2e8; color: #b85b18; }
        .uncertain { background: #fff7dc; color: #916a00; }

        .footer {
            text-align: center;
            color: #7a8496;
            font-size: 13px;
            padding-top: 28px;
        }

        div[data-testid="stMetric"] {
            padding: 4px 0;
        }

        div[data-testid="stMetricValue"] {
            font-size: 31px;
        }

        .timeline-line {
            border-left: 3px solid #dbe3f4;
            padding-left: 18px;
            margin-left: 9px;
            padding-bottom: 14px;
        }

        .timeline-time {
            color: #5d6b82;
            font-size: 13px;
            font-weight: 750;
        }

        .timeline-event {
            font-size: 16px;
            font-weight: 650;
            margin-top: 3px;
        }

        .small-muted {
            color: #737e91;
            font-size: 13px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# HELPERS
# ==========================================================

STATUS_META = {
    "HEALTHY": ("🟢", "healthy"),
    "MISMATCH": ("🔴", "mismatch"),
    "ANOMALY": ("🚨", "anomaly"),
    "RECOVERABLE": ("🟠", "recoverable"),
    "UNCERTAIN": ("🟡", "uncertain"),
}

STATUS_ORDER = [
    "HEALTHY",
    "MISMATCH",
    "ANOMALY",
    "RECOVERABLE",
    "UNCERTAIN",
]


def status_badge(status):
    emoji, css_class = STATUS_META.get(status, ("⚪", "uncertain"))
    return (
        f'<span class="status-pill {css_class}">'
        f"{emoji} {status}</span>"
    )


def get_customer_impact(transaction, result):
    payment_status = transaction["payment_status"]
    order_status = transaction["order_status"]
    amount = transaction["amount"]
    status = result["status"]

    if payment_status == "SUCCESS" and order_status == "FAILED":
        return (
            f"The customer may have been charged ₹{amount:,.0f}, "
            "but the order remains marked as FAILED. This can create "
            "a paid-but-unfulfilled order and may require reconciliation."
        )

    if status == "ANOMALY":
        return (
            "The transaction contains an abnormal event that could "
            "result in duplicate processing or incorrect payment handling."
        )

    if status == "RECOVERABLE":
        return (
            "The customer may have experienced a timeout or delayed "
            "confirmation even though the payment subsequently completed."
        )

    if status == "UNCERTAIN":
        return (
            "There is insufficient evidence to safely determine the "
            "final customer impact. Human review is recommended."
        )

    if status == "MISMATCH":
        return (
            "The payment and order states are inconsistent and require "
            "reconciliation before the transaction is considered resolved."
        )

    return "No direct customer impact was detected."


def get_risk_explanation(result):
    severity = result["severity"]
    status = result["status"]

    if severity == "HIGH":
        return (
            f"This is a HIGH-risk {status} because the detected payment "
            "state inconsistency could lead to financial loss, an "
            "incorrect order state, or customer-facing payment issues."
        )

    if severity == "MEDIUM":
        return (
            f"This is a MEDIUM-risk {status}. The transaction contains "
            "an abnormal condition that should be investigated."
        )

    return (
        f"This is a LOW-risk {status}. No immediate corrective action "
        "is required."
    )


def answer_transaction_question(question, transaction, result):
    question = question.lower().strip()

    if any(word in question for word in [
        "why", "risk", "risky", "danger", "severity"
    ]):
        return (
            f"### 🔴 Risk Assessment\n\n"
            f"This transaction is classified as **{result['severity']} risk** "
            f"because {result['diagnosis'].lower()} "
            f"The diagnosis confidence is "
            f"**{result['confidence'] * 100:.0f}%**."
        )

    if any(word in question for word in [
        "wrong", "happen", "cause", "root", "problem", "issue"
    ]):
        return (
            f"### 🔎 Root Cause\n\n"
            f"{result['reason']}\n\n"
            f"**Diagnosis:** {result['diagnosis']}"
        )

    if any(word in question for word in [
        "customer", "impact", "charged", "money", "refund"
    ]):
        return (
            f"### 👤 Customer Impact\n\n"
            f"{get_customer_impact(transaction, result)}"
        )

    if any(word in question for word in [
        "recover", "fix", "action", "solve", "resolve", "repair"
    ]):
        return (
            f"### 🛠️ Recommended Recovery\n\n"
            f"**Action:** `{result['action']}`\n\n"
            f"{result['recovery']}"
        )

    if any(word in question for word in [
        "payment", "order", "state", "status"
    ]):
        return (
            f"### 💳 Current State\n\n"
            f"Payment: **{transaction['payment_status']}**  \n"
            f"Order: **{transaction['order_status']}**  \n"
            f"Webhook: **{transaction['webhook_status']}**  \n"
            f"Amount: **₹{transaction['amount']:,.0f}**"
        )

    return (
        f"### 🩺 Transaction Summary\n\n"
        f"**Status:** {result['status']}  \n"
        f"**Severity:** {result['severity']}  \n"
        f"**Diagnosis:** {result['diagnosis']}  \n"
        f"**Recommended action:** `{result['action']}`"
    )


def show_state(label, value, icon):
    if value in ["SUCCESS", "PAID", "RECEIVED"]:
        css = "healthy"
    elif value in ["FAILED"]:
        css = "mismatch"
    else:
        css = "uncertain"

    st.markdown(
        f"""
        <div class="state-card">
            <div class="state-name">{icon} {label}</div>
            <div class="state-value">
                <span class="status-pill {css}">{value}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def simulate_recovery(transaction, result):
    payment_status = transaction["payment_status"]
    order_status = transaction["order_status"]
    webhook_status = transaction["webhook_status"]
    action = result["action"]

    st.markdown("### 🔄 Recovery Process")
    st.caption(
        "Simulation environment. No real payment or order data is modified."
    )

    st.markdown("#### 1️⃣ Current State")
    c1, c2, c3 = st.columns(3)

    with c1:
        show_state("Payment", payment_status, "💰")
    with c2:
        show_state("Order", order_status, "📦")
    with c3:
        show_state("Webhook", webhook_status, "🔔")

    st.markdown("#### 2️⃣ Recovery Action")

    if action == "RECONCILE_ORDER":
        st.info("🔎 Verifying payment ID against the associated order...")
        st.success("✓ Payment verification successful")
        st.info("🔄 Simulating idempotent order reconciliation...")

        if payment_status == "SUCCESS" and order_status == "FAILED":
            st.success("✓ Payment is SUCCESS while order is FAILED.")
            st.success("✓ Simulated state transition: **FAILED → PAID**")
            final_order_status = "PAID"
        else:
            st.warning(
                "Available evidence does not support an automatic "
                "order-state change."
            )
            final_order_status = order_status

    elif action == "RECONCILE_REFUND":
        st.info("🔎 Verifying refund state against the payment record...")
        st.success("✓ Refund verification completed")
        st.info("🔄 Simulating refund reconciliation...")
        st.success("✓ Refund reconciliation would be performed after verification.")
        final_order_status = order_status

    elif action == "VERIFY_DUPLICATE_PAYMENT":
        st.info("🔎 Checking transaction for duplicate payment...")
        st.success("✓ Duplicate-payment verification simulated.")
        final_order_status = order_status

    elif action == "IDEMPOTENCY_CHECK":
        st.info("🔎 Checking webhook/event idempotency...")
        st.success("✓ Idempotency check simulated.")
        final_order_status = order_status

    elif action == "HUMAN_REVIEW":
        st.warning(
            "👤 Human review is required because the available evidence "
            "is insufficient."
        )
        final_order_status = order_status

    else:
        st.success("✓ No recovery action is required.")
        final_order_status = order_status

    st.markdown("#### 3️⃣ Simulated Final State")

    c1, c2, c3 = st.columns(3)

    with c1:
        show_state("Payment", payment_status, "💰")

    with c2:
        show_state("Order", final_order_status, "📦")
        if final_order_status == "PAID" and order_status != "PAID":
            st.success("✓ Reconciled")

    with c3:
        show_state("Webhook", webhook_status, "🔔")

    st.success("🎯 Recovery simulation completed.")
    st.info(
        "🛡️ Simulation only. No real payment, order, refund, "
        "webhook, or customer data was modified."
    )


# ==========================================================
# HEADER
# ==========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">🩺 Payment State Doctor</div>
        <div class="hero-subtitle">
            Intelligent payment inconsistency detection, diagnosis & recovery
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# LOAD DATA
# ==========================================================

try:
    df = pd.read_csv("data/transactions.csv")
except FileNotFoundError:
    st.error("❌ Could not find `data/transactions.csv`.")
    st.stop()


# ==========================================================
# DIAGNOSE ALL TRANSACTIONS
# ==========================================================

results = []

for _, row in df.iterrows():
    transaction_id = row["transaction_id"]
    timeline = SCENARIOS.get(transaction_id, [])
    results.append(diagnose_transaction(row, timeline))

df["status"] = [r["status"] for r in results]
df["diagnosis"] = [r["diagnosis"] for r in results]
df["action"] = [r["action"] for r in results]
df["severity"] = [r["severity"] for r in results]


# ==========================================================
# TOP METRICS
# ==========================================================

total_transactions = len(df)
issues_detected = int((df["status"] != "HEALTHY").sum())
revenue_at_risk = df.loc[
    df["status"] != "HEALTHY", "amount"
].sum()

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Transactions Analyzed", total_transactions)

with c2:
    st.metric(
        "Issues Detected",
        issues_detected,
        help="Transactions requiring attention",
    )
    st.caption(f"🔴 {issues_detected} transaction(s) requiring attention")

with c3:
    st.metric("Revenue at Risk", f"₹{revenue_at_risk:,.0f}")


# ==========================================================
# ISSUE OVERVIEW
# ==========================================================

st.divider()
st.markdown(
    '<div class="section-title">📊 Issue Overview</div>',
    unsafe_allow_html=True,
)

status_counts = (
    df["status"]
    .value_counts()
    .reindex(STATUS_ORDER, fill_value=0)
)

cols = st.columns(5)

for col, status in zip(cols, STATUS_ORDER):
    emoji, _ = STATUS_META[status]
    with col:
        st.markdown(f"{emoji} **{status.title()}**")
        st.metric("", int(status_counts[status]))


# ==========================================================
# ANALYTICS
# ==========================================================

st.divider()
st.markdown(
    '<div class="section-title">📈 Payment Health Analytics</div>',
    unsafe_allow_html=True,
)

issue_distribution = (
    status_counts[status_counts.index != "HEALTHY"]
    .reset_index()
)
issue_distribution.columns = ["Issue Type", "Count"]

revenue_by_status = (
    df[df["status"] != "HEALTHY"]
    .groupby("status")["amount"]
    .sum()
    .reindex(
        ["ANOMALY", "MISMATCH", "UNCERTAIN", "RECOVERABLE"],
        fill_value=0,
    )
    .reset_index()
)
revenue_by_status.columns = ["Issue Type", "Revenue"]


if PLOTLY_AVAILABLE:
    chart_colors = {
        "ANOMALY": "#d7263d",
        "MISMATCH": "#e5484d",
        "RECOVERABLE": "#f08c46",
        "UNCERTAIN": "#e4b44c",
    }

    fig_issue = px.bar(
        issue_distribution,
        x="Count",
        y="Issue Type",
        orientation="h",
        text="Count",
        category_orders={
            "Issue Type": [
                "UNCERTAIN",
                "RECOVERABLE",
                "MISMATCH",
                "ANOMALY",
            ]
        },
    )
    fig_issue.update_traces(
        marker_color=[
            chart_colors.get(x, "#4472c4")
            for x in issue_distribution["Issue Type"]
        ],
        textposition="outside",
        hovertemplate="%{y}: %{x}<extra></extra>",
    )
    fig_issue.update_layout(
        height=310,
        margin=dict(l=5, r=35, t=10, b=10),
        xaxis_title="Transactions",
        yaxis_title="",
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    fig_revenue = px.bar(
        revenue_by_status,
        x="Revenue",
        y="Issue Type",
        orientation="h",
        text="Revenue",
        category_orders={
            "Issue Type": [
                "RECOVERABLE",
                "UNCERTAIN",
                "MISMATCH",
                "ANOMALY",
            ]
        },
    )
    fig_revenue.update_traces(
        marker_color=[
            chart_colors.get(x, "#4472c4")
            for x in revenue_by_status["Issue Type"]
        ],
        texttemplate="₹%{x:,.0f}",
        textposition="outside",
        hovertemplate="%{y}: ₹%{x:,.0f}<extra></extra>",
    )
    fig_revenue.update_layout(
        height=310,
        margin=dict(l=5, r=55, t=10, b=10),
        xaxis_title="Revenue at Risk",
        yaxis_title="",
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            '<div class="section-subtitle">Issue Distribution</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig_issue, use_container_width=True)

    with c2:
        st.markdown(
            '<div class="section-subtitle">Revenue at Risk by Issue Type</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig_revenue, use_container_width=True)

else:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Issue Distribution**")
        st.bar_chart(issue_distribution.set_index("Issue Type"))

    with c2:
        st.markdown("**Revenue at Risk by Issue Type**")
        st.bar_chart(revenue_by_status.set_index("Issue Type"))


# ==========================================================
# TRANSACTION HEALTH
# ==========================================================

st.divider()
st.markdown(
    '<div class="section-title">📋 Transaction Health</div>',
    unsafe_allow_html=True,
)

health_table = df[
    [
        "transaction_id",
        "scenario",
        "status",
        "severity",
        "action",
        "amount",
    ]
].copy()

health_table.columns = [
    "Transaction",
    "Scenario",
    "Status",
    "Severity",
    "Recommended Action",
    "Amount",
]

health_table["Status"] = health_table["Status"].apply(status_badge)
health_table["Amount"] = health_table["Amount"].apply(
    lambda x: f"₹{x:,.0f}"
)

# HTML table gives us presentation-grade status badges.
table_html = """
<style>
.presentation-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}
.presentation-table th {
    text-align: left;
    padding: 12px 10px;
    background: #f5f7fb;
    color: #4d586d;
    font-weight: 750;
    border-bottom: 1px solid #e2e6ee;
}
.presentation-table td {
    padding: 13px 10px;
    border-bottom: 1px solid #edf0f5;
    color: #303747;
}
.presentation-table tr:hover {
    background: #fafbfe;
}
</style>
<table class="presentation-table">
<thead><tr>
"""

for col in health_table.columns:
    table_html += f"<th>{col}</th>"

table_html += "</tr></thead><tbody>"

for _, row in health_table.iterrows():
    table_html += "<tr>"
    for col in health_table.columns:
        table_html += f"<td>{row[col]}</td>"
    table_html += "</tr>"

table_html += "</tbody></table>"

st.markdown(table_html, unsafe_allow_html=True)


# ==========================================================
# TRANSACTION INVESTIGATION
# ==========================================================

st.divider()
st.markdown(
    '<div class="section-title">🔍 Transaction Investigation</div>',
    unsafe_allow_html=True,
)

transaction_ids = df["transaction_id"].tolist()

transaction_id = st.selectbox(
    "Select a transaction to investigate",
    transaction_ids,
)

transaction = df[
    df["transaction_id"] == transaction_id
].iloc[0]

timeline = SCENARIOS.get(transaction_id, [])
result = diagnose_transaction(transaction, timeline)


# ==========================================================
# INVESTIGATION HEADER
# ==========================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Transaction", transaction_id)

with c2:
    st.metric("Amount", f"₹{transaction['amount']:,.0f}")

with c3:
    st.metric("Severity", result["severity"])

with c4:
    st.metric(
        "Confidence",
        f"{result['confidence'] * 100:.0f}%",
    )


# ==========================================================
# DOCTOR'S VERDICT
# ==========================================================

st.markdown("<br>", unsafe_allow_html=True)

verdict_color = {
    "HIGH": "#c62839",
    "MEDIUM": "#b85b18",
    "LOW": "#147a42",
}.get(result["severity"], "#5f6b7a")

st.markdown(
    f"""
    <div class="verdict">
        <div class="verdict-label">🩺 Doctor's Verdict</div>
        <div class="verdict-title" style="color:{verdict_color};">
            {result["status"]} • {result["severity"]} RISK
        </div>
        <div class="verdict-text">
            {result["diagnosis"]}
        </div>
        <div class="action-box">
            <b>Recommended treatment:</b>
            <code>{result["action"]}</code><br>
            <span class="small-muted">{result["recovery"]}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# TIMELINE
# ==========================================================

st.divider()
st.markdown(
    '<div class="section-title">⏱️ Transaction Timeline</div>',
    unsafe_allow_html=True,
)

if timeline:
    for timestamp, event, status in timeline:
        if status == "SUCCESS":
            icon = "✓"
        elif status in ["DELAYED", "TIMEOUT", "DUPLICATE"]:
            icon = "⚠"
        else:
            icon = "✗"

        st.markdown(
            f"""
            <div class="timeline-line">
                <div class="timeline-time">{timestamp} · {icon}</div>
                <div class="timeline-event">{event}</div>
                <div class="small-muted">{status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info("No timeline events available.")


# ==========================================================
# CURRENT PAYMENT STATE
# ==========================================================

st.divider()
st.markdown(
    '<div class="section-title">💳 Current Payment State</div>',
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)

with c1:
    show_state(
        "Payment",
        transaction["payment_status"],
        "💰",
    )

with c2:
    show_state(
        "Order",
        transaction["order_status"],
        "📦",
    )

with c3:
    show_state(
        "Webhook",
        transaction["webhook_status"],
        "🔔",
    )


# ==========================================================
# DIAGNOSIS + INCIDENT REPORT
# ==========================================================

st.divider()
st.markdown(
    '<div class="section-title">🧠 Diagnosis & Incident Report</div>',
    unsafe_allow_html=True,
)

if result["severity"] == "HIGH":
    st.error(f"🚨 {result['diagnosis']}")
elif result["severity"] == "MEDIUM":
    st.warning(f"⚠️ {result['diagnosis']}")
else:
    st.success(f"✅ {result['diagnosis']}")

c1, c2 = st.columns(2)

with c1:
    st.markdown("#### 🎯 Root Cause")
    st.write(result["reason"])

    st.markdown("#### 👤 Customer Impact")
    st.write(get_customer_impact(transaction, result))

with c2:
    st.markdown("#### ⚠️ Risk Assessment")
    st.write(get_risk_explanation(result))

    st.markdown("#### 🛠️ Recommended Next Step")
    st.success(f"`{result['action']}`")
    st.write(result["recovery"])


# ==========================================================
# EVIDENCE
# ==========================================================

st.divider()
st.markdown(
    '<div class="section-title">🔎 Evidence Used for Diagnosis</div>',
    unsafe_allow_html=True,
)

if result.get("evidence"):
    evidence_df = pd.DataFrame(result["evidence"])
    st.dataframe(
        evidence_df,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No additional timeline evidence detected.")


# ==========================================================
# RECOVERY RECOMMENDATION
# ==========================================================

st.divider()
st.markdown(
    '<div class="section-title">🛠️ Recovery Recommendation</div>',
    unsafe_allow_html=True,
)

st.info(
    f"**Recommended System Action:** `{result['action']}`"
)

st.write(result["recovery"])


# ==========================================================
# RECOVERY SIMULATOR
# ==========================================================

st.divider()
st.markdown(
    '<div class="section-title">⚡ Recovery Simulator</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Safely simulates the recommended recovery path. "
    "No real payment or order data is modified."
)

if result["action"] == "NO_ACTION":
    st.success("✅ No automated recovery is required.")
else:
    if st.button(
        "⚡ Run Recovery Simulation",
        type="primary",
        use_container_width=False,
        key=f"recovery_{transaction_id}",
    ):
        simulate_recovery(transaction, result)


# ==========================================================
# ASK ABOUT TRANSACTION
# ==========================================================

st.divider()
st.markdown(
    '<div class="section-title">💬 Ask About This Transaction</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Ask about risk, root cause, customer impact, payment state, or recovery."
)

suggested_questions = [
    "Why is this risky?",
    "What went wrong?",
    "What is the customer impact?",
    "How should I recover it?",
]

# Suggested buttons
qcols = st.columns(4)

for i, question_text in enumerate(suggested_questions):
    with qcols[i]:
        if st.button(
            question_text,
            key=f"suggested_{transaction_id}_{i}",
            use_container_width=True,
        ):
            st.session_state["question_input"] = question_text

question = st.text_input(
    "Your question",
    placeholder="Why is this transaction risky?",
    key="question_input",
)

if question:
    answer = answer_transaction_question(
        question,
        transaction,
        result,
    )

    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(answer)


# ==========================================================
# RAW TRANSACTION DETAILS
# ==========================================================

st.divider()

with st.expander("🔍 View Raw Transaction Details"):
    st.dataframe(
        transaction.to_frame("Value"),
        use_container_width=True,
    )


# ==========================================================
# FOOTER
# ==========================================================

st.markdown(
    """
    <div class="footer">
        🩺 Payment State Doctor • Intelligent payment consistency
        monitoring & recovery simulation
    </div>
    """,
    unsafe_allow_html=True,
)
