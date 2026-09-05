# --------------------------------------------------
# PAYMENT STATE DOCTOR
# Deterministic Incident Explanation Engine
# --------------------------------------------------


def local_ai_response(transaction, result):
    """
    Generates a human-readable incident report
    using the deterministic diagnosis engine.

    No external AI/API dependency.
    """

    status = result["status"]
    severity = result["severity"]
    amount = transaction["amount"]

    # --------------------------------------------------
    # CUSTOMER IMPACT
    # --------------------------------------------------

    if (
        transaction["payment_status"] == "SUCCESS"
        and transaction["order_status"] == "FAILED"
    ):

        customer_impact = (
            f"The customer may have been charged "
            f"₹{amount:,.0f}, but the order remains "
            f"marked as FAILED. This can result in a "
            f"paid-but-unfulfilled order and may require "
            f"reconciliation before any refund or retry."
        )

    elif status == "ANOMALY":

        customer_impact = (
            "The transaction contains an abnormal payment "
            "event. If the event is processed incorrectly, "
            "the customer could experience duplicate "
            "processing or an incorrect payment state."
        )

    elif status == "RECOVERABLE":

        customer_impact = (
            f"The customer may have experienced a temporary "
            f"payment delay or timeout for the ₹{amount:,.0f} "
            f"transaction. The payment should be verified "
            f"before asking the customer to retry."
        )

    elif status == "UNCERTAIN":

        customer_impact = (
            "The available transaction evidence is "
            "insufficient to safely determine the final "
            "customer impact. Human review is recommended."
        )

    else:

        customer_impact = (
            "No customer impact was detected from the "
            "available transaction evidence."
        )

    # --------------------------------------------------
    # INCIDENT REPORT
    # --------------------------------------------------

    return f"""
### 🎯 Root Cause

{result["reason"]}

### 👤 Customer Impact

{customer_impact}

### ⚠️ Risk Assessment

This transaction is classified as
**{severity} risk**.

Diagnosis confidence:
**{result["confidence"] * 100:.0f}%**

### 🛠️ Recommended Next Step

**{result["action"]}**

{result["recovery"]}
"""


# --------------------------------------------------
# ASK AI
# --------------------------------------------------

def ask_ai(question, transaction, result):
    """
    Answers common investigation questions using
    the deterministic transaction diagnosis.

    LLM integration can be added later.
    """

    question_lower = question.lower().strip()

    # --------------------------------------------------
    # WHY / RISK
    # --------------------------------------------------

    if any(
        word in question_lower
        for word in [
            "why",
            "risk",
            "risky"
        ]
    ):

        return (
            f"This transaction is classified as "
            f"**{result['severity']} risk** because "
            f"{result['diagnosis'].lower()} "
            f"The diagnosis has "
            f"**{result['confidence'] * 100:.0f}% confidence**."
        )

    # --------------------------------------------------
    # ROOT CAUSE
    # --------------------------------------------------

    if any(
        word in question_lower
        for word in [
            "wrong",
            "happen",
            "cause",
            "root",
            "problem"
        ]
    ):

        return (
            f"The likely root cause is:\n\n"
            f"**{result['reason']}**"
        )

    # --------------------------------------------------
    # CUSTOMER IMPACT
    # --------------------------------------------------

    if any(
        word in question_lower
        for word in [
            "customer",
            "impact",
            "charged",
            "money"
        ]
    ):

        amount = transaction["amount"]

        if (
            transaction["payment_status"] == "SUCCESS"
            and transaction["order_status"] == "FAILED"
        ):

            return (
                f"The payment of **₹{amount:,.0f}** was "
                f"successful, but the order is currently "
                f"marked as **FAILED**.\n\n"
                f"The customer may therefore experience a "
                f"paid-but-unfulfilled order. The payment and "
                f"order should be reconciled before taking "
                f"further action."
            )

        return (
            "Based on the available transaction evidence, "
            "no direct customer impact has been established."
        )

    # --------------------------------------------------
    # RECOVERY
    # --------------------------------------------------

    if any(
        word in question_lower
        for word in [
            "recover",
            "fix",
            "action",
            "solve",
            "repair"
        ]
    ):

        return (
            f"The recommended action is "
            f"**{result['action']}**.\n\n"
            f"{result['recovery']}"
        )

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------

    if any(
        word in question_lower
        for word in [
            "status",
            "state"
        ]
    ):

        return (
            f"Transaction **{transaction['transaction_id']}** "
            f"is classified as **{result['status']}** "
            f"with **{result['severity']} severity**.\n\n"
            f"Payment: **{transaction['payment_status']}**\n\n"
            f"Order: **{transaction['order_status']}**\n\n"
            f"Webhook: **{transaction['webhook_status']}**"
        )

    # --------------------------------------------------
    # DEFAULT RESPONSE
    # --------------------------------------------------

    return (
        f"Transaction **{transaction['transaction_id']}** "
        f"is classified as **{result['status']}** with "
        f"**{result['severity']} severity**.\n\n"
        f"Diagnosis:\n"
        f"{result['diagnosis']}\n\n"
        f"Recommended action:\n"
        f"**{result['action']}**"
    )
