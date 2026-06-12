Classify this customer message into exactly one intent:
delivery_issue, refund_request, billing_issue, technical_issue, account_access,
product_question, complaint, cancellation, other.

Prefer delivery_issue when a delayed or missing delivery also mentions a refund.
Return JSON with keys intent and confidence.

Message:
{message}
