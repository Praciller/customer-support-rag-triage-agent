import json

from src.llm.base import LLMRequest, ProviderResponse


class MockProvider:
    def __init__(self, name: str = "mock") -> None:
        self.name = name

    def generate(self, request: LLMRequest) -> ProviderResponse:
        handlers = {
            "classify_intent": self._classify_intent,
            "detect_urgency": self._detect_urgency,
            "generate_response": self._generate_response,
        }
        payload = handlers[request.task](request)
        return ProviderResponse(
            text=json.dumps(payload),
            provider=self.name,
            model=request.model,
        )

    @staticmethod
    def _classify_intent(request: LLMRequest) -> dict:
        text = request.user_ticket.lower()
        rules = [
            (
                "complaint",
                (
                    "not mine",
                    "not recognised",
                    "not recognized",
                    "stolen",
                    "fraud",
                    "complaint",
                    "ignored",
                    "unacceptable",
                    "angry",
                ),
            ),
            ("delivery_issue", ("not arrived", "delivery", "tracking", "late order", "shipment")),
            ("refund_request", ("refund", "money back", "reimburse")),
            ("account_access", ("login", "password", "locked", "sign in", "pin")),
            ("technical_issue", ("error", "broken", "not working", "bug", "crash")),
            ("cancellation", ("cancel", "close account", "terminate")),
            (
                "product_question",
                ("how do", "what is", "can i", "where can", "which countries", "support this"),
            ),
            (
                "billing_issue",
                (
                    "charged",
                    "payment",
                    "billing",
                    "fee",
                    "transaction",
                    "transfer",
                    "withdrawal",
                    "cash",
                    "pending",
                ),
            ),
        ]
        intent = next(
            (label for label, keywords in rules if any(keyword in text for keyword in keywords)),
            "other",
        )
        return {"intent": intent}

    @staticmethod
    def _detect_urgency(request: LLMRequest) -> dict:
        text = request.user_ticket.lower()
        critical_terms = ("fraud", "stolen", "identity theft", "unsafe", "legal action")
        high_terms = ("refund", "asap", "immediately", "ignored", "urgent", "now")
        if any(term in text for term in critical_terms):
            urgency = "critical"
        elif any(term in text for term in high_terms):
            urgency = "high"
        elif any(
            term in text for term in ("not arrived", "not working", "late", "problem", "issue")
        ):
            urgency = "medium"
        else:
            urgency = "low"
        escalate = urgency in {"high", "critical"}
        return {
            "urgency": urgency,
            "escalate": escalate,
            "escalation_reason": (
                "Customer language indicates immediate financial or service risk"
                if escalate
                else ""
            ),
        }

    @staticmethod
    def _generate_response(request: LLMRequest) -> dict:
        prompt = request.workflow_instructions.lower()
        if "delivery_issue" in prompt:
            proposals = [
                "Ask the customer for an order ID to review delivery status.",
                "Offer available refund options for the delayed item.",
            ]
        elif "account_access" in prompt:
            proposals = ["Ask the customer to confirm the sign-in method and error message."]
        elif "complaint" in prompt:
            proposals = [
                "Ask for the transaction reference.",
                "Tell the customer not to post account credentials.",
            ]
        elif "refund_request" in prompt:
            proposals = ["Ask for the transaction reference and date to review the payment."]
        elif "billing_issue" in prompt:
            proposals = ["Ask for the transaction reference, date, and current status."]
        elif "technical_issue" in prompt:
            proposals = ["Ask for the exact error and the last step completed."]
        elif "cancellation" in prompt:
            proposals = ["Ask for the transfer or account reference."]
        elif "product_question" in prompt:
            proposals = ["Ask which country and feature the customer means."]
        else:
            proposals = ["Ask what issue the customer needs help with."]
        return {"proposals": proposals}
