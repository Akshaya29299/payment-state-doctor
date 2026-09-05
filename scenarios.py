SCENARIOS = {
    "TXN001": [
        ("10:42:01", "Order created", "SUCCESS"),
        ("10:42:03", "Payment initiated", "SUCCESS"),
        ("10:42:21", "Payment successful", "SUCCESS"),
        ("10:42:52", "Webhook received", "DELAYED"),
        ("10:42:53", "Order update", "FAILED"),
    ],

"TXN002": [
    ("11:15:01", "Order created", "SUCCESS"),
    ("11:15:04", "Payment initiated", "SUCCESS"),
    ("11:15:08", "Payment successful", "SUCCESS"),
    ("11:15:13", "Webhook received", "SUCCESS"),
    ("11:15:14", "Order marked as PAID", "SUCCESS"),
],


    "TXN003": [
        ("12:01:01", "Order created", "SUCCESS"),
        ("12:01:03", "Payment initiated", "SUCCESS"),
        ("12:01:09", "Payment successful", "SUCCESS"),
        ("12:01:10", "Webhook received", "SUCCESS"),
        ("12:01:11", "Webhook received", "DUPLICATE"),
    ],

    "TXN004": [
        ("13:22:01", "Order created", "SUCCESS"),
        ("13:22:03", "Payment initiated", "SUCCESS"),
        ("13:22:15", "Client timeout", "TIMEOUT"),
        ("13:22:57", "Payment successful", "SUCCESS"),
        ("13:23:39", "Webhook received", "DELAYED"),
    ],

    "TXN005": [
        ("14:05:01", "Order created", "SUCCESS"),
        ("14:05:03", "Payment initiated", "SUCCESS"),
        ("14:05:07", "Payment successful", "SUCCESS"),
        ("14:05:08", "Second payment successful", "DUPLICATE"),
        ("14:05:10", "Webhook received", "SUCCESS"),
    ],

    "TXN006": [
        ("15:11:01", "Order created", "SUCCESS"),
        ("15:11:03", "Payment successful", "SUCCESS"),
        ("15:11:06", "Webhook received", "SUCCESS"),
        ("15:12:01", "Refund initiated", "SUCCESS"),
        ("15:12:04", "Refund successful", "SUCCESS"),
    ],

    "TXN007": [
        ("16:30:01", "Order created", "SUCCESS"),
        ("16:30:04", "Payment initiated", "SUCCESS"),
        ("16:30:20", "Payment failed", "FAILED"),
    ],
}