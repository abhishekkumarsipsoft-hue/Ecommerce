import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import app as orders_app
import store

def client():
    orders_app.app.config["TESTING"] = True
    return orders_app.app.test_client()

PAYLOAD = {
    "user_id": "user_abhi_01",
    "address_id": "addr_01",
    "items": [
        {"product_id": "prod_001", "product_name": "Urban Daypack 25L", "unit_price": 899, "quantity": 2}
    ],
    "total_amount": 1798
}

def test_create_succeeds_with_201_and_location():
    store.clear()
    c = client()
    r = c.post("/api/orders", json=PAYLOAD)
    assert r.status_code == 201, r.data
    assert "Location" in r.headers
    assert r.headers["Location"].startswith("/api/orders/")
    body = r.get_json()
    assert body["status"] == "PENDING_PAYMENT"
    assert "internal_idempotency_key" not in body
    assert "internal_retry_count" not in body
    assert body["id"]

def test_idempotent_repeat_returns_original():
    store.clear()
    c = client()
    headers = {"Idempotency-Key": "11111111-1111-1111-1111-111111111111"}
    r1 = c.post("/api/orders", json=PAYLOAD, headers=headers)
    assert r1.status_code == 201
    oid1 = r1.get_json()["id"]
    r2 = c.post("/api/orders", json=PAYLOAD, headers=headers)
    assert r2.status_code == 200
    assert r2.headers.get("Idempotency-Replayed") == "true"
    assert r2.get_json()["id"] == oid1
    # no duplicate created
    assert len(store.list_orders()) == 1

def test_failure_path_returns_4xx_problem():
    store.clear()
    c = client()
    # malformed: missing items
    bad = {"user_id": "u1", "address_id": "a1", "total_amount": 100}
    r = c.post("/api/orders", json=bad)
    assert r.status_code == 400
    body = r.get_json()
    assert set(body.keys()) == {"type", "title", "status", "detail"}
    assert body["status"] == 400

def test_unknown_id_returns_404():
    store.clear()
    c = client()
    r = c.get("/api/orders/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
    body = r.get_json()
    assert body["status"] == 404
    assert body["type"].endswith("not-found")
