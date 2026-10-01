"""In-memory illustration. Production requires durable atomic operation storage."""
from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass
class BookingLedger:
    outcomes: Dict[str, Tuple[Tuple[str, str], dict]] = field(default_factory=dict)
    writes: int = 0

    def book(self, operation_key: str, account: str, slot: str) -> dict:
        if not operation_key or not account or not slot:
            raise ValueError("Operation key, account, and slot are required")
        fingerprint = (account, slot)
        if operation_key in self.outcomes:
            saved_request, saved_result = self.outcomes[operation_key]
            if saved_request != fingerprint:
                raise ValueError("Idempotency conflict: the same key has different arguments")
            return dict(saved_result)
        self.writes += 1
        result = {"status": "success", "booking_id": "booking-" + str(self.writes)}
        self.outcomes[operation_key] = (fingerprint, result)
        return dict(result)


if __name__ == "__main__":
    ledger = BookingLedger()
    first = ledger.book("operation-42", "synthetic-account", "2030-01-05T14:00:00Z")
    retry = ledger.book("operation-42", "synthetic-account", "2030-01-05T14:00:00Z")
    print("First:", first, "| Retry:", retry, "| Writes:", ledger.writes)
    try:
        ledger.book("operation-42", "synthetic-account", "2030-01-06T14:00:00Z")
    except ValueError as error:
        print("Conflicting retry rejected:", error)
