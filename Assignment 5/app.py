"""Orders service — Flask app (Assignment 5: methods, headers, caching, safe retries)."""
import os
import re
import gzip
import hashlib
import json
import time
from datetime import datetime, timezone
from io import BytesIO

from flask import Flask, request, jsonify, g, make_response

from models import Order, VALID_STATUSES
import store
import errors
from payment_client import call_payments_create_order

app = Flask(__name__)

# ---------- validation ----------

def validate_create_order(body: dict) -> str | None:
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

def compute_etag(order: Order) -> str:
    # Weak ETag based on updated_at + status + id (changes when resource changes — B4)
    raw = f"{order.id}:{order.status}:{order.updated_at}"
    return 'W/"' + hashlib.md5(raw.encode()).hexdigest()[:16] + '"'

def accepts_json() -> bool:
    accept = request.headers.get("Accept", "")
    if not accept or accept.strip() in ("*/*", ""):
        return True
    # Accept may contain multiple values with q-weights; simple check
    parts = [p.strip().split(";")[0].strip().lower() for p in accept.split(",")]
    return "application/json" in parts or "application/*" in parts or "*/*" in parts

def require_accept_json():
    """Return 406 if Accept does not allow JSON (B1)."""
    accept = request.headers.get("Accept", "")
    if accept and accept.strip() not in ("", "*/*"):
        parts = [p.strip().split(";")[0].strip().lower() for p in accept.split(",")]
        if "application/json" not in parts and "application/*" not in parts and "*/*" not in parts:
            return errors.problem(
                type_="https://campuseats.example.com/problems/not-acceptable",
                title="Not Acceptable", status=406,
                detail="this resource only produces application/json; send Accept: application/json"
            )
    return None

def require_auth():
    """B3: protected endpoints require Authorization: Bearer <token>; missing/empty -> 401."""
    # health and OPTIONS are public
    if request.method == "OPTIONS":
        return None
    if request.path == "/api/health":
        return None
    # For this assignment, ALL /api/orders* require auth
    auth = request.headers.get("Authorization", "")
    if not auth or not auth.strip():
        return errors.problem(
            type_="https://campuseats.example.com/problems/unauthorized",
            title="Unauthorized", status=401,
            detail="missing Authorization: Bearer <token> header"
        )
    if not auth.startswith("Bearer ") or not auth[7:].strip():
        return errors.problem(
            type_="https://campuseats.example.com/problems/unauthorized",
            title="Unauthorized", status=401,
            detail="Authorization header must be 'Bearer <token>' with a non-empty token"
        )
    return None

# ---------- rate limiting (B5) — per-client budget ----------
RATE_LIMIT = 20  # per window per client
RATE_WINDOW_SEC = 60
_rate_buckets: dict[str, list[float]] = {}

def _client_id() -> str:
    # Prefer Authorization token as client id, else IP
    tok = request.headers.get("Authorization", "")
    if tok.startswith("Bearer "):
        return "tok:" + tok[7:].strip()[:32]
    return "ip:" + (request.remote_addr or "unknown")

def check_rate_limit():
    cid = _client_id()
    now = time.time()
    bucket = _rate_buckets.get(cid, [])
    # prune old entries
    bucket = [t for t in bucket if now - t < RATE_WINDOW_SEC]
    if len(bucket) >= RATE_LIMIT:
        # 429
        retry_after = int(RATE_WINDOW_SEC - (now - bucket[0])) + 1
        resp = errors.problem(
            type_="https://campuseats.example.com/problems/too-many-requests",
            title="Too Many Requests", status=429,
            detail=f"rate limit exceeded: {RATE_LIMIT} requests per {RATE_WINDOW_SEC}s"
        )
        resp.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
        resp.headers["X-RateLimit-Remaining"] = "0"
        resp.headers["Retry-After"] = str(retry_after)
        return resp
    bucket.append(now)
    _rate_buckets[cid] = bucket
    g._rate_remaining = RATE_LIMIT - len(bucket)
    g._rate_limit = RATE_LIMIT
    return None

def clear_rate_limit():
    _rate_buckets.clear()

# ---------- global before/after request ----------

@app.before_request
def _before():
    # X-HTTP-Method-Override (A5): honour only as documented fallback
    override = request.headers.get("X-HTTP-Method-Override", "").strip().upper()
    if override and request.method == "POST" and override in ("PUT", "PATCH", "DELETE"):
        # WSGI environ override — Flask reads from environ
        request.environ["REQUEST_METHOD"] = override

    # Content negotiation (B1) — check Accept before anything else
    if request.path.startswith("/api/"):
        neg = require_accept_json()
        if neg:
            return neg

    # Rate limit (B5) — per client
    if request.path.startswith("/api/"):
        rl = check_rate_limit()
        if rl:
            return rl

@app.after_request
def _after(resp):
    # Rate limit signalling (B5)
    if hasattr(g, "_rate_limit"):
        resp.headers.setdefault("X-RateLimit-Limit", str(g._rate_limit))
        resp.headers.setdefault("X-RateLimit-Remaining", str(g._rate_remaining))
    # CORS (B6)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, PUT, DELETE, OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, Idempotency-Key, If-Match, If-None-Match, X-HTTP-Method-Override, X-RateLimit-Limit"
    resp.headers["Access-Control-Expose-Headers"] = "Location, ETag, X-RateLimit-Limit, X-RateLimit-Remaining, Retry-After, Idempotency-Key, Idempotency-Replayed"
    # Security headers (B7)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Content-Type enforcement (B1) — bodies must be application/json
    if resp.mimetype == "application/json":
        resp.headers["Content-Type"] = "application/json"
    # Ensure Content-Type for Problem bodies (errors.py already does jsonify)
    return resp

# Optional gzip (B1) for large JSON when client sends Accept-Encoding: gzip
@app.route("/api/orders/<order_id>/override", methods=["POST", "OPTIONS"])
def method_override_proxy(order_id: str):
    """Constrained-client fallback: POST + X-HTTP-Method-Override: PUT|PATCH|DELETE."""
    if request.method == "OPTIONS":
        resp = make_response("", 204)
        resp.headers["Allow"] = "POST, OPTIONS"
        return resp
    override = request.headers.get("X-HTTP-Method-Override", "").strip().upper()
    if override == "DELETE":
        return delete_order(order_id)
    if override == "PATCH":
        return patch_order_status(order_id)
    if override == "PUT":
        return put_order(order_id)
    return errors.bad_request("X-HTTP-Method-Override must be PUT, PATCH or DELETE when using POST")

@app.after_request
def _maybe_gzip(resp):
    enc = request.headers.get("Accept-Encoding", "")
    if "gzip" in enc.lower() and resp.mimetype == "application/json":
        raw = resp.get_data()
        if len(raw) > 800:  # only for large payloads
            buf = BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
                gz.write(raw)
            gzipped = buf.getvalue()
            resp.set_data(gzipped)
            resp.headers["Content-Encoding"] = "gzip"
            resp.headers["Content-Length"] = str(len(gzipped))
            # Flask's default Vary not set; add for caches
            resp.headers["Vary"] = "Accept-Encoding"
    return resp

# ---------- routes ----------

@app.route("/api/health", methods=["GET", "OPTIONS"])
def health():
    if request.method == "OPTIONS":
        resp = make_response("", 204)
        resp.headers["Allow"] = "GET, OPTIONS"
        return resp
    return jsonify({"status": "ok"})

@app.route("/api/orders", methods=["GET", "POST", "OPTIONS"])
def orders_collection():
    if request.method == "OPTIONS":
        resp = make_response("", 204)
        resp.headers["Allow"] = "GET, POST, OPTIONS"
        return resp
    if request.method == "GET":
        return list_orders()
    return create_order()

def create_order():
    # Auth (B3)
    auth_err = require_auth()
    if auth_err:
        return auth_err
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
            resp.headers["ETag"] = compute_etag(existing)
            return resp

    order = Order(
        user_id=body["user_id"],
        address_id=body["address_id"],
        items=body["items"],
        total_amount=body["total_amount"],
        idempotency_key=idem,
    )

    if os.getenv("CALL_PAYMENTS", "0") == "1":
        try:
            call_payments_create_order(order_id=order.id, amount=order.total_amount,
                                       idempotency_key=idem or order.id)
        except Exception as e:
            app.logger.warning("Payments unreachable, order kept PENDING_PAYMENT: %s", e)

    store.save(order)
    resp = jsonify(order.as_json())
    resp.status_code = 201
    resp.headers["Location"] = f"/api/orders/{order.id}"
    resp.headers["ETag"] = compute_etag(order)
    resp.headers["Cache-Control"] = "no-store"  # B6: creation response not cacheable
    if idem:
        resp.headers["Idempotency-Key"] = idem
    return resp

def list_orders():
    # Auth (B3)
    auth_err = require_auth()
    if auth_err:
        return auth_err
    user_id = request.args.get("user_id")
    status = request.args.get("status")
    # A4: reads use query string for filter/sort/paginate — pure read, safe
    if status and status not in VALID_STATUSES:
        return errors.bad_request(f"unknown status filter: {status}")
    sort = request.args.get("sort", "created_at")
    page = request.args.get("page", "1")
    limit = request.args.get("limit", "20")
    try:
        page_i = int(page)
        limit_i = int(limit)
        if page_i < 1 or limit_i < 1 or limit_i > 100:
            raise ValueError
    except ValueError:
        return errors.bad_request("page and limit must be positive integers (limit <= 100)")
    orders = store.list_orders(user_id=user_id, status=status)
    # simple sort support (already sorted by created_at desc in store)
    total = len(orders)
    start = (page_i - 1) * limit_i
    paged = orders[start:start+limit_i]
    resp = jsonify([o.as_json() for o in paged])
    resp.headers["Cache-Control"] = "no-store"  # list not cacheable (personal)
    resp.headers["X-Total-Count"] = str(total)
    return resp

@app.route("/api/orders/<order_id>", methods=["GET", "PATCH", "PUT", "DELETE", "OPTIONS"])
def order_item(order_id: str):
    if request.method == "OPTIONS":
        resp = make_response("", 204)
        resp.headers["Allow"] = "GET, PATCH, PUT, DELETE, OPTIONS"
        return resp
    # Handle X-HTTP-Method-Override style DELETE via POST already rewritten in before_request
    if request.method == "DELETE":
        return delete_order(order_id)
    if request.method == "PUT":
        return put_order(order_id)
    if request.method == "PATCH":
        return patch_order_status(order_id)
    return get_order(order_id)

def get_order(order_id: str):
    auth_err = require_auth()
    if auth_err:
        return auth_err
    order = store.get(order_id)
    if not order:
        return errors.not_found(f"order {order_id} not found")
    etag = compute_etag(order)
    # C1 conditional GET
    inm = request.headers.get("If-None-Match")
    if inm and inm.strip() == etag:
        resp = make_response("", 304)
        resp.headers["ETag"] = etag
        resp.headers["Cache-Control"] = "private, max-age=60"
        return resp
    resp = jsonify(order.as_json())
    resp.headers["ETag"] = etag
    resp.headers["Cache-Control"] = "private, max-age=60"  # B4 cacheable read
    return resp

def patch_order_status(order_id: str):
    auth_err = require_auth()
    if auth_err:
        return auth_err
    order = store.get(order_id)
    if not order:
        return errors.not_found(f"order {order_id} not found")
    # C2 conditional write — require If-Match
    etag = compute_etag(order)
    if_match = request.headers.get("If-Match")
    # Enforce If-Match when provided; if missing we still allow (doc says support, not require)
    # But if header is present and mismatches -> 412
    if if_match is not None and if_match.strip() != etag:
        resp = errors.problem(
            type_="https://campuseats.example.com/problems/precondition-failed",
            title="Precondition Failed", status=412,
            detail=f"ETag mismatch: expected {etag}, got {if_match}"
        )
        resp.headers["ETag"] = etag
        return resp
    body = request.get_json(silent=True) or {}
    new_status = body.get("status")
    if new_status not in VALID_STATUSES:
        return errors.bad_request(f"invalid status: {new_status}")
    if new_status == order.status:
        return errors.conflict(f"order already in status {new_status}")
    if not order.can_transition(new_status):
        return errors.conflict(f"cannot transition from {order.status} to {new_status}")
    order.status = new_status
    order.updated_at = datetime.now(timezone.utc).isoformat()
    store.save(order)
    resp = jsonify(order.as_json())
    resp.headers["ETag"] = compute_etag(order)
    resp.headers["Cache-Control"] = "no-store"
    return resp

def put_order(order_id: str):
    """PUT replaces the order's status-relevant fields — idempotent."""
    auth_err = require_auth()
    if auth_err:
        return auth_err
    order = store.get(order_id)
    if not order:
        return errors.not_found(f"order {order_id} not found")
    etag = compute_etag(order)
    if_match = request.headers.get("If-Match")
    if if_match is not None and if_match.strip() != etag:
        resp = errors.problem(
            type_="https://campuseats.example.com/problems/precondition-failed",
            title="Precondition Failed", status=412,
            detail=f"ETag mismatch: expected {etag}, got {if_match}"
        )
        resp.headers["ETag"] = etag
        return resp
    body = request.get_json(silent=True)
    if body is None:
        return errors.bad_request("invalid JSON body")
    # For PUT, require status field to replace
    new_status = body.get("status")
    if new_status not in VALID_STATUSES:
        return errors.bad_request(f"invalid status: {new_status}")
    if new_status == order.status:
        resp = jsonify(order.as_json())
        resp.headers["ETag"] = etag
        return resp
    if not order.can_transition(new_status):
        return errors.conflict(f"cannot transition from {order.status} to {new_status}")
    order.status = new_status
    order.updated_at = datetime.now(timezone.utc).isoformat()
    store.save(order)
    resp = jsonify(order.as_json())
    resp.headers["ETag"] = compute_etag(order)
    resp.headers["Cache-Control"] = "no-store"
    return resp

def delete_order(order_id: str):
    auth_err = require_auth()
    if auth_err:
        return auth_err
    order = store.get(order_id)
    if not order:
        return errors.not_found(f"order {order_id} not found")
    # Domain rule: cannot delete delivered order
    if order.status == "DELIVERED":
        return errors.unprocessable(f"cannot delete order in status {order.status}")
    # If-Match guard for safe delete
    etag = compute_etag(order)
    if_match = request.headers.get("If-Match")
    if if_match is not None and if_match.strip() != etag:
        resp = errors.problem(
            type_="https://campuseats.example.com/problems/precondition-failed",
            title="Precondition Failed", status=412,
            detail=f"ETag mismatch: expected {etag}, got {if_match}"
        )
        resp.headers["ETag"] = etag
        return resp
    # Soft delete: mark CANCELLED and return 204 if already cancelled, else cancel
    if order.status != "CANCELLED":
        order.status = "CANCELLED"
        order.cancellation = {"reason": "deleted via API", "cancelled_at": datetime.now(timezone.utc).isoformat()}
        order.updated_at = datetime.now(timezone.utc).isoformat()
        store.save(order)
    resp = make_response("", 204)
    resp.headers["Cache-Control"] = "no-store"
    return resp

@app.route("/api/orders/<order_id>/cancellation", methods=["POST", "OPTIONS"])
def cancellation_resource(order_id: str):
    if request.method == "OPTIONS":
        resp = make_response("", 204)
        resp.headers["Allow"] = "POST, OPTIONS"
        return resp
    auth_err = require_auth()
    if auth_err:
        return auth_err
    order = store.get(order_id)
    if not order:
        return errors.not_found(f"order {order_id} not found")
    body = request.get_json(silent=True)
    if body is None:
        return errors.bad_request("invalid JSON body")
    err = validate_cancellation(body)
    if err:
        return errors.bad_request(err)
    if order.status in ("SHIPPED", "DELIVERED", "CANCELLED"):
        return errors.unprocessable(f"order cannot be cancelled in status {order.status}")
    if order.status not in ("PENDING_PAYMENT", "PAID", "PACKED"):
        return errors.unprocessable(f"order cannot be cancelled in status {order.status}")
    if order.cancellation is not None:
        return errors.conflict("order already has a cancellation")
    order.status = "CANCELLED"
    order.cancellation = {"reason": body["reason"], "cancelled_at": datetime.now(timezone.utc).isoformat()}
    order.updated_at = datetime.now(timezone.utc).isoformat()
    store.save(order)
    resp = jsonify(order.as_json())
    resp.status_code = 202
    resp.headers["ETag"] = compute_etag(order)
    resp.headers["Cache-Control"] = "no-store"
    return resp

@app.route("/api/orders/<order_id>/status", methods=["PATCH", "OPTIONS"])
def legacy_status_route(order_id: str):
    """Kept for Assignment 4 backward compat — alias to PATCH /api/orders/{id}."""
    if request.method == "OPTIONS":
        resp = make_response("", 204)
        resp.headers["Allow"] = "PATCH, OPTIONS"
        return resp
    return patch_order_status(order_id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")))
