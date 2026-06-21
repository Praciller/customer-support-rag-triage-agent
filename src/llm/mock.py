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
            "grounding_check": self._grounding_check,
        }
        payload = handlers[request.task](request)
        return ProviderResponse(
            text=json.dumps(payload),
            provider=self.name,
            model=request.model,
        )

    @staticmethod
    def _classify_intent(request: LLMRequest) -> dict:
        text = MockProvider._customer_message(request.prompt)
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
        return {"intent": intent, "confidence": 0.91}

    @staticmethod
    def _detect_urgency(request: LLMRequest) -> dict:
        text = MockProvider._customer_message(request.prompt)
        critical_terms = ("fraud", "stolen", "identity theft", "unsafe", "legal action")
        high_terms = ("refund", "asap", "immediately", "ignored", "urgent", "now")
        if any(term in text for term in critical_terms):
            urgency = "critical"
        elif any(term in text for term in high_terms):
            urgency = "high"
        elif any(
            term in text
            for term in ("not arrived", "not working", "late", "problem", "issue")
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
        prompt = request.prompt.lower()
        if "delivery_issue" in prompt:
            response = (
                "I'm sorry your order has not arrived. Please share your order ID so the "
                "delivery status and available refund options can be reviewed."
            )
        elif "account_access" in prompt:
            response = (
                "I'm sorry you cannot access your account. Please confirm the sign-in method "
                "and any error message so the next recovery step can be identified."
            )
        elif "complaint" in prompt:
            response = (
                "I'm sorry this activity is concerning. Please share the transaction reference "
                "and avoid posting account credentials so a support specialist can review it."
            )
        elif "refund_request" in prompt:
            response = (
                "I'm sorry the payment needs review. Please share the transaction reference and "
                "date so the support team can check the available next steps."
            )
        elif "billing_issue" in prompt:
            response = (
                "I'm sorry this transaction is unresolved. Please share its reference, date, and "
                "current status so the support team can investigate."
            )
        elif "technical_issue" in prompt:
            response = (
                "I'm sorry the feature is not working. Please share the exact error and the last "
                "step completed so the issue can be investigated."
            )
        elif "cancellation" in prompt:
            response = (
                "I understand you want to stop this request. Please share the transfer or account "
                "reference so a support specialist can review what actions remain available."
            )
        elif "product_question" in prompt:
            response = (
                "Thanks for the question. Please confirm the country and feature you are asking "
                "about so the relevant public guidance can be checked."
            )
        else:
            response = (
                "I'm sorry you encountered this issue. Please share the relevant reference "
                "number and any missing details so the support team can review it."
            )
        return {"suggested_response": response}

    @staticmethod
    def _grounding_check(request: LLMRequest) -> dict:
        has_context = bool(request.context.strip())
        unsupported = [] if has_context else ["No retrieved cases were available."]
        return {
            "grounded": has_context,
            "grounding_score": 0.86 if has_context else 0.25,
            "unsupported_claims": unsupported,
            "confidence": 0.88 if has_context else 0.4,
        }

    @staticmethod
    def _customer_message(prompt: str) -> str:
        marker = "message:"
        _, separator, message = prompt.lower().rpartition(marker)
        return message.strip() if separator else prompt.lower()
