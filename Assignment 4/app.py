"""Orders service — Flask app following Tutorial 4 shape."""
import os
import re
from flask import Flask, request, jsonify
from models import Order, VALID_STATUSES
import store
import errors
from payment_client import call_payments_create_order

app = Flask(__name__)

# ---------- validation (hand-written, replaces XML Schema) ----------

def validate_create_order(body: dict) -> str | None:
    """Return error detail if invalid, else None."""
    if not isinstance(body, dict):
        return "body must be a JSON object"
    for field in ("user_id", "address_id", "items", "total_amount"):
        if field not in body:
            return f"missing required field: {field}"
    if not isinstance(body["user_id"], str) or not body["user_id"].strip():
        return "user_id must be a non-empty string"
    if not isinstance(body["address_id"], str) or not body["address_id"].strip():
        return "address_id must be a non-empty string"
    if not isinstance(body["items"], list) or len(body["items"]) == 0:
        return "items must be a non-empty array"
    for i, it in enumerate(body["items"]):
        if not isinstance(it, dict):
            return f"items[{i}] must be an object"
        for f in ("product_id", "product_name", "unit_price", "quantity"):
            if f not in it:
                return f"items[{i}] missing field: {f}"
        if not isinstance(it["product_id"], str) or not it["product_id"].strip():
            return f"items[{i}].product_id must be a non-empty string"
        if not isinstance(it["product_name"], str) or not it["product_name"].strip():
            return f"items[{i}].product_name must be a non-empty string"
        try:
            up = float(it["unit_price"])
            if up <= 0:
                return f"items[{i}].unit_price must be > 0"
        except (TypeError, ValueError):
            return f"items[{i}].unit_price must be a number"
        if not isinstance(it["quantity"], int) or it["quantity"] < 1:
            return f"items[{i}].quantity must be an integer >= 1"
    try:
        ta = float(body["total_amount"])
        if ta <= 0:
            return "total_amount must be > 0"
    except (TypeError, ValueError):
        return "total_amount must be a number"
    # Cross-check total vs sum
    calc = sum(float(it["unit_price"]) * int(it["quantity"]) for it in body["items"])
    if abs(calc - float(body["total_amount"])) > 0.01:
        return f"total_amount {body['total_amount']} does not match sum of items {calc:.2f}"
    return None

def validate_cancellation(body: dict) -> str | None:
    if not isinstance(body, dict):
        return "body must be a JSON object"
    if "reason" not in body or not isinstance(body["reason"], str) or not body["reason"].strip():
        return "reason is required and must be a non-empty string"
    if len(body["reason"]) > 500:
        return "reason must be <= 500 characters"
    return None

# ---------- helpers ----------

UUID_RE = re.compile(r"^[0-9a-fA-F-]{36}$")

def is_uuid(v: str) -> bool:
    return bool(UUID_RE.match(v))

# ---------- routes ----------

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.post("/api/orders")
def create_order():
    body = request.get_json(silent=True)
    if body is None:
        return errors.bad_request("invalid JSON body")
    err = validate_create_order(body)
    if err:
        return errors.bad_request(err)

    idem = request.headers.get("Idempotency-Key")
    if idem:
        existing = store.find_by_idempotency_key(idem)
        if existing:
            resp = jsonify(existing.as_json())
            resp.status_code = 200
            resp.headers["Idempotency-Replayed"] = "true"
            return resp

    order = Order(
        user_id=body["user_id"],
        address_id=body["address_id"],
        items=body["items"],
        total_amount=body["total_amount"],
        idempotency_key=idem,
    )

    # Optional hardened call to Payments — gracefully degraded if unreachable
    # Controlled by env var CALL_PAYMENTS; off by default so tests stay hermetic
    if os.getenv("CALL_PAYMENTS", "0") == "1":
        try:
            call_payments_create_order(order_id=order.id, amount=order.total_amount,
                                       idempotency_key=idem or order.id)
        except Exception as e:
            # Fallback: keep order as PENDING_PAYMENT; payment will be created async
            # This choice is documented in NOTES.md D3
            app.logger.warning("Payments unreachable, order kept PENDING_PAYMENT: %s", e)

    store.save(order)
    resp = jsonify(order.as_json())
    resp.status_code = 201
    resp.headers["Location"] = f"/api/orders/{order.id}"
    if idem:
        resp.headers["Idempotency-Key"] = idem
    return resp

@app.get("/api/orders/<order_id>")
def get_order(order_id: str):
    order = store.get(order_id)
    if not order:
        return errors.not_found(f"order {order_id} not found")
    return jsonify(order.as_json())

@app.get("/api/orders")
def list_orders():
    user_id = request.args.get("user_id")
    status = request.args.get("status")
    if status and status not in VALID_STATUSES:
        return errors.bad_request(f"unknown status filter: {status}")
    orders = store.list_orders(user_id=user_id, status=status)
    return jsonify([o.as_json() for o in orders])

@app.post("/api/orders/<order_id>/cancellation")
def cancel_order(order_id: str):
    order = store.get(order_id)
    if not order:
        return errors.not_found(f"order {order_id} not found")
    body = request.get_json(silent=True)
    if body is None:
        return errors.bad_request("invalid JSON body")
    err = validate_cancellation(body)
    if err:
        return errors.bad_request(err)

    # 422 — valid request but domain refuses (already cancelled/shipped etc.)
    if order.status in ("SHIPPED", "DELIVERED", "CANCELLED"):
        return errors.unprocessable(f"order cannot be cancelled in status {order.status}")
    if order.status not in ("PENDING_PAYMENT", "PAID", "PACKED"):
        return errors.unprocessable(f"order cannot be cancelled in status {order.status}")

    # 409 — state conflict (e.g. second cancel racing)
    if order.cancellation is not None:
        return errors.conflict("order already has a cancellation")

    from datetime import datetime, timezone
    order.status = "CANCELLED"
    order.cancellation = {"reason": body["reason"], "cancelled_at": datetime.now(timezone.utc).isoformat()}
    order.updated_at = datetime.now(timezone.utc).isoformat()
    store.save(order)
    # 202 — cancellation accepted, downstream refund continues async
    resp = jsonify(order.as_json())
    resp.status_code = 202
    return resp

# Optional endpoint to exercise state conflicts: update status (for curl transcript)
@app.patch("/api/orders/<order_id>/status")
def update_status(order_id: str):
    order = store.get(order_id)
    if not order:
        return errors.not_found(f"order {order_id} not found")
    body = request.get_json(silent=True) or {}
    new_status = body.get("status")
    if new_status not in VALID_STATUSES:
        return errors.bad_request(f"invalid status: {new_status}")
    if new_status == order.status:
        return errors.conflict(f"order already in status {new_status}")
    if not order.can_transition(new_status):
        return errors.conflict(f"cannot transition from {order.status} to {new_status}")
    from datetime import datetime, timezone
    order.status = new_status
    order.updated_at = datetime.now(timezone.utc).isoformat()
    store.save(order)
    return jsonify(order.as_json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")))
