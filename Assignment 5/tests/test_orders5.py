import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import app as orders_app
import store
from app import clear_rate_limit

AUTH = {"Authorization": "Bearer tok_test_abc123"}

def client():
    orders_app.app.config["TESTING"] = True
    return orders_app.app.test_client()

PAYLOAD = {
    "user_id": "user_abhi_01",
    "address_id": "addr_01",
    "items": [{"product_id": "prod_001", "product_name": "Urban Daypack 25L", "unit_price": 899, "quantity": 2}],
    "total_amount": 1798
}

def setup_function(fn):
    store.clear()
    clear_rate_limit()

# C8-ish: create + replay + failure + 404 (ported) + new behaviours

def test_create_succeeds_with_201_location_etag():
    c = client()
    r = c.post("/api/orders", json=PAYLOAD, headers=AUTH)
    assert r.status_code == 201, r.data
    assert "Location" in r.headers
    assert "ETag" in r.headers
    assert r.headers["Cache-Control"] == "no-store"
    assert r.get_json()["status"] == "PENDING_PAYMENT"

def test_idempotent_repeat_returns_original_replayed():
    c = client()
    h = {**AUTH, "Idempotency-Key": "11111111-2222-3333-4444-555555555555"}
    r1 = c.post("/api/orders", json=PAYLOAD, headers=h)
    assert r1.status_code == 201
    oid = r1.get_json()["id"]
    r2 = c.post("/api/orders", json=PAYLOAD, headers=h)
    assert r2.status_code == 200
    assert r2.headers.get("Idempotency-Replayed") == "true"
    assert r2.get_json()["id"] == oid
    assert len(store.list_orders()) == 1

def test_malformed_body_returns_400_problem():
    c = client()
    r = c.post("/api/orders", json={"user_id": "u1"}, headers=AUTH)
    assert r.status_code == 400
    body = r.get_json()
    assert set(body.keys()) == {"type", "title", "status", "detail"}
    assert body["status"] == 400

def test_unknown_id_returns_404():
    c = client()
    r = c.get("/api/orders/00000000-0000-0000-0000-000000000000", headers=AUTH)
    assert r.status_code == 404

def test_missing_auth_returns_401():
    c = client()
    r = c.get("/api/orders/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 401
    assert r.get_json()["status"] == 401

def test_accept_non_json_returns_406():
    c = client()
    r = c.get("/api/orders/00000000-0000-0000-0000-000000000000", headers={**AUTH, "Accept": "text/html"})
    assert r.status_code == 406

def test_conditional_get_returns_304_when_etag_matches():
    c = client()
    rc = c.post("/api/orders", json=PAYLOAD, headers=AUTH)
    oid = rc.get_json()["id"]
    etag = rc.headers["ETag"]
    r = c.get(f"/api/orders/{oid}", headers={**AUTH, "If-None-Match": etag})
    assert r.status_code == 304
    assert r.data == b""

def test_conditional_get_returns_200_when_etag_stale():
    c = client()
    rc = c.post("/api/orders", json=PAYLOAD, headers=AUTH)
    oid = rc.get_json()["id"]
    r = c.get(f"/api/orders/{oid}", headers={**AUTH, "If-None-Match": 'W/"stale123456789012"'})
    assert r.status_code == 200

def test_conditional_write_returns_412_on_mismatch():
    c = client()
    rc = c.post("/api/orders", json=PAYLOAD, headers=AUTH)
    oid = rc.get_json()["id"]
    r = c.patch(f"/api/orders/{oid}", json={"status": "PAID"}, headers={**AUTH, "If-Match": 'W/"stale123456789012"'})
    assert r.status_code == 412
    assert r.get_json()["status"] == 412

def test_conditional_write_succeeds_when_etag_matches():
    c = client()
    rc = c.post("/api/orders", json=PAYLOAD, headers=AUTH)
    oid = rc.get_json()["id"]
    etag = rc.headers["ETag"]
    r = c.patch(f"/api/orders/{oid}", json={"status": "PAID"}, headers={**AUTH, "If-Match": etag})
    assert r.status_code == 200

def test_rate_limit_returns_429_and_retry_after():
    c = client()
    for _ in range(20):
        r = c.get("/api/health")
        assert r.status_code == 200
    r = c.get("/api/health")
    assert r.status_code == 429
    assert "Retry-After" in r.headers
    assert r.headers["X-RateLimit-Limit"] == "20"

def test_cors_and_security_headers_present():
    c = client()
    r = c.get("/api/health")
    assert r.headers.get("Access-Control-Allow-Origin") == "*"
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert "Strict-Transport-Security" in r.headers
    assert "Content-Type" in r.headers

def test_options_returns_allow():
    c = client()
    r = c.options("/api/orders")
    assert r.status_code == 204
    assert "Allow" in r.headers
    assert "GET" in r.headers["Allow"]

def test_delete_returns_204():
    c = client()
    rc = c.post("/api/orders", json=PAYLOAD, headers=AUTH)
    oid = rc.get_json()["id"]
    r = c.delete(f"/api/orders/{oid}", headers=AUTH)
    assert r.status_code == 204

def test_x_http_method_override_fallback():
    c = client()
    rc = c.post("/api/orders", json=PAYLOAD, headers=AUTH)
    oid = rc.get_json()["id"]
    # constrained client: POST + override to DELETE (fallback, Assignment 5 A5)
    r = c.post(f"/api/orders/{oid}/override", headers={**AUTH, "X-HTTP-Method-Override": "DELETE"})
    assert r.status_code == 204
