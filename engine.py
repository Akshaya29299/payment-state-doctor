def diagnose_transaction(transaction, timeline):

    order_status = str(
        transaction["order_status"]
    ).upper()

    payment_status = str(
        transaction["payment_status"]
    ).upper()

    webhook_status = str(
        transaction["webhook_status"]
    ).upper()

    timeline = timeline or []

    events = [
        str(event).lower()
        for _, event, _ in timeline
    ]

    evidence = []

    for timestamp, event, status in timeline:

        evidence.append({
            "timestamp": timestamp,
            "event": event,
            "status": status
        })


    # --------------------------------------------------
    # 1. Duplicate Payment
    # --------------------------------------------------

    if any(
        "second payment successful" in event
        for event in events
    ):

        return {
            "status": "ANOMALY",

            "diagnosis":
                "A second successful payment was detected for the same order.",

            "reason":
                "The payment timeline contains more than one successful payment event, which indicates a possible duplicate charge.",

            "action":
                "VERIFY_DUPLICATE_PAYMENT",

            "severity":
                "HIGH",

            "confidence":
                0.97,

            "evidence":
                evidence,

            "recovery":
                "Verify the payment IDs and order mapping. If the second charge is confirmed as a duplicate, initiate a refund for the duplicate payment."
        }


    # --------------------------------------------------
    # 2. Duplicate Webhook
    # --------------------------------------------------

    if webhook_status == "DUPLICATE":

        return {
            "status": "ANOMALY",

            "diagnosis":
                "The same payment webhook was received more than once.",

            "reason":
                "Multiple webhook deliveries were detected for the same payment event.",

            "action":
                "IDEMPOTENCY_CHECK",

            "severity":
                "MEDIUM",

            "confidence":
                0.99,

            "evidence":
                evidence,

            "recovery":
                "Use the webhook event ID as an idempotency key and ignore already processed events."
        }


    # --------------------------------------------------
    # 3. Payment Timeout
    # IMPORTANT:
    # This must come BEFORE the generic
    # SUCCESS + FAILED mismatch rule.
    # --------------------------------------------------

    if (
        any("timeout" in event for event in events)
        and payment_status == "SUCCESS"
    ):

        return {
            "status": "RECOVERABLE",

            "diagnosis":
                "The client timed out, but the payment later succeeded.",

            "reason":
                "The client did not receive a timely response, but the payment processor subsequently confirmed the transaction.",

            "action":
                "RECONCILE_ORDER",

            "severity":
                "HIGH",

            "confidence":
                0.94,

            "evidence":
                evidence,

            "recovery":
                "Check the final payment state and reconcile the order before notifying the customer that the payment was successful."
        }


    # --------------------------------------------------
    # 4. Payment Success + Order Failed
    # --------------------------------------------------

    if (
        payment_status == "SUCCESS"
        and order_status == "FAILED"
    ):

        return {
            "status": "MISMATCH",

            "diagnosis":
                "Payment succeeded but the order state remains FAILED.",

            "reason":
                "The payment processor confirmed the payment, but the order state was not updated successfully after payment completion.",

            "action":
                "RECONCILE_ORDER",

            "severity":
                "HIGH",

            "confidence":
                0.96,

            "evidence":
                evidence,

            "recovery":
                "Verify the payment ID against the order ID and update the order state to PAID after successful reconciliation."
        }


    # --------------------------------------------------
    # 5. Refund State Mismatch
    # --------------------------------------------------

    if (
        payment_status == "REFUNDED"
        and order_status == "PAID"
    ):

        return {
            "status": "MISMATCH",

            "diagnosis":
                "Payment was refunded but the order still appears as PAID.",

            "reason":
                "The payment state indicates a completed refund while the order database still contains the PAID state.",

            "action":
                "RECONCILE_REFUND",

            "severity":
                "HIGH",

            "confidence":
                0.98,

            "evidence":
                evidence,

            "recovery":
                "Verify the refund transaction and synchronize the order state with the refunded payment."
        }


    # --------------------------------------------------
    # 6. Payment Failed
    # --------------------------------------------------

    if payment_status == "FAILED":

        return {
            "status": "UNCERTAIN",

            "diagnosis":
                "Payment failed and there is insufficient evidence for automated recovery.",

            "reason":
                "The payment state is FAILED, but the available transaction evidence does not provide enough information to safely perform automatic recovery.",

            "action":
                "HUMAN_REVIEW",

            "severity":
                "MEDIUM",

            "confidence":
                0.61,

            "evidence":
                evidence,

            "recovery":
                "Review the payment gateway response, failure reason and order state before attempting another payment or recovery operation."
        }


    # --------------------------------------------------
    # 7. Healthy Transaction
    # --------------------------------------------------

    return {
        "status":
            "HEALTHY",

        "diagnosis":
            "No payment-state inconsistency detected.",

        "reason":
            "Payment, order and webhook states are consistent with the available timeline.",

        "action":
            "NO_ACTION",

        "severity":
            "LOW",

        "confidence":
            0.99,

        "evidence":
            evidence,

        "recovery":
            "No recovery action is required. Continue normal transaction processing."
    }
