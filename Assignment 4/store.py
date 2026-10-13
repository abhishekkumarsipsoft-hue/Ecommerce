"""In-process dictionary store — no other service may import this."""
from models import Order

_orders: dict[str, Order] = {}
# idempotency_key -> order_id
_idempotency_index: dict[str, str] = {}

def save(order: Order) -> None:
    _orders[order.id] = order
    if order.internal_idempotency_key:
        _idempotency_index[order.internal_idempotency_key] = order.id

def get(order_id: str) -> Order | None:
    return _orders.get(order_id)

def list_orders(user_id: str | None = None, status: str | None = None) -> list[Order]:
    result = list(_orders.values())
    if user_id is not None:
        result = [o for o in result if o.user_id == user_id]
    if status is not None:
        result = [o for o in result if o.status == status]
    return sorted(result, key=lambda o: o.created_at, reverse=True)

def find_by_idempotency_key(key: str) -> Order | None:
    oid = _idempotency_index.get(key)
    return _orders.get(oid) if oid else None

def clear() -> None:
    _orders.clear()
    _idempotency_index.clear()
