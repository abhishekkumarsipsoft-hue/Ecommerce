"""Order domain model — record vs representation separation."""
import uuid
from datetime import datetime, timezone

# Valid state transitions
ALLOWED_TRANSITIONS = {
    "PENDING_PAYMENT": {"PAID", "CANCELLED"},
    "PAID": {"PACKED", "CANCELLED"},
    "PACKED": {"SHIPPED"},
    "SHIPPED": {"DELIVERED"},
}

VALID_STATUSES = {"PENDING_PAYMENT", "PAID", "PACKED", "SHIPPED", "DELIVERED", "CANCELLED"}

class Order:
    """Internal record — holds what we store. Differs from as_json() in at least one field."""

    def __init__(self, *, user_id: str, address_id: str, items: list, total_amount: float,
                 idempotency_key: str | None = None):
        self.id = str(uuid.uuid4())
        # INTERNAL fields (never leaked):
        self.internal_idempotency_key = idempotency_key  # stored but not exposed
        self.internal_retry_count = 0
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at
        # DOMAIN fields:
        self.user_id = user_id
        self.address_id = address_id
        self.items = items  # list of {product_id, product_name, unit_price, quantity}
        self.total_amount = round(float(total_amount), 2)
        self.status = "PENDING_PAYMENT"
        self.cancellation = None  # {reason, cancelled_at} when cancelled

    def as_json(self) -> dict:
        """Public representation — what the API returns. Differs from stored model."""
        out = {
            "id": self.id,
            "user_id": self.user_id,
            "address_id": self.address_id,
            "items": self.items,
            "total_amount": self.total_amount,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.cancellation:
            out["cancellation"] = self.cancellation
        return out

    def can_transition(self, new_status: str) -> bool:
        return new_status in ALLOWED_TRANSITIONS.get(self.status, set())
