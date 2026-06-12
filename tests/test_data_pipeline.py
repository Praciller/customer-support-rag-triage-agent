from src.data.clean_dataset import clean_record
from src.data.load_dataset import map_banking77_intent


def test_banking77_labels_map_to_project_intents() -> None:
    assert map_banking77_intent("card_arrival") == "delivery_issue"
    assert map_banking77_intent("cash_withdrawal") == "billing_issue"
    assert map_banking77_intent("cash_withdrawal_charge") == "billing_issue"
    assert map_banking77_intent("cash_withdrawal_not_recognised") == "complaint"
    assert map_banking77_intent("cash_withdrawal_wrong_exchange_rate") == "billing_issue"
    assert map_banking77_intent("cash_withdrawal_wrong_amount") == "billing_issue"
    assert map_banking77_intent("card_payment_fee_charged") == "billing_issue"
    assert map_banking77_intent("cash_withdrawal_cancelled") == "cancellation"
    assert map_banking77_intent("cash_withdrawal_reverted") == "refund_request"


def test_clean_record_normalizes_text_and_preserves_source_metadata() -> None:
    record = clean_record(
        {
            "id": "42",
            "message": "  My   card has not arrived. \n",
            "intent": "delivery_issue",
            "response": None,
            "source": "PolyAI/banking77",
            "created_at": None,
            "metadata": {"original_intent": "card_arrival"},
        }
    )

    assert record["message"] == "My card has not arrived."
    assert record["response"] == ""
    assert record["metadata"]["original_intent"] == "card_arrival"
