# CampusEats — Assignment 5 NOTES.md

**TeamID:** MCA-CS543-G07  |  **Course:** CS543 Web Services — Dr. Pramit Mazumdar
**pramit.mazumdar@iiitvadodara.ac.in**  |  **Due before Lecture 6**

| Roll / Name | Assignment 2 role |
|---|---|
| Abhishek | Auth + Payment |
| Binamra Rana | Auth + Payment |
| Navendu | Auth + Order |
| Shruti | Catalogue + Order |
| Yatindra | Catalogue + Order + Payment |

> Repository: `Ecommerce-1` (bags store — backpack / laptop bag / sling bag / duffel). Brief still calls it *CampusEats*; behaviour identical. This folder is a sibling to `Assignment 4`.

```
Assignment 5/
  openapi.yaml          — contract first (methods, statuses, headers)
  app.py, models.py, store.py, errors.py, payment_client.py
  tests/test_orders5.py
  NOTES.md              — this file (method map, headers table, safe-retry plan, 8 answers)
  curl-transcript.txt   — curl -v transcript (201, replay, 304, 412, 400, 404, 401)
  validator-output.txt  — openapi-spec-validator: 0 errors
  pytest-output.txt     — pytest -v
```

---

## Part A — Methods & the message

### A1  Audit verbs → CampusEats method map (action → method + URL)

Every verb was checked: **GET reads, POST creates, PUT replaces, PATCH modifies, DELETE removes.** No verb leaks into a URL — non-CRUD actions become sub-resources (A2). The single endpoint that previously leaked (`POST /api/orders/:id/cancellation` already correct in A4) stays correct; the only addition is `DELETE` and explicit `PUT/PATCH` on the item.

| Action (what the user/staff wants) | Method | URL | Notes |
|---|---|---|---|
| Create order from cart | `POST` | `/api/orders` | collection create → `201 + Location` |
| Read one order | `GET` | `/api/orders/{orderId}` | single item read |
| List / search / filter orders | `GET` | `/api/orders?user_id=&status=&sort=&page=&limit=` | A4 — query-string only (see Q7) |
| Cancel order | `POST` | `/api/orders/{orderId}/cancellation` | **non-CRUD** → sub-resource (A2) |
| Advance order status (admin) | `PATCH` | `/api/orders/{orderId}` | partial modification |
| Replace order status (idempotent) | `PUT` | `/api/orders/{orderId}` | full replacement |
| Delete / soft-cancel order | `DELETE` | `/api/orders/{orderId}` | soft — marks `CANCELLED` |
| Legacy status alias (Assignment 4 compat) | `PATCH` | `/api/orders/{orderId}/status` | kept for transcript compat |
| Health | `GET` | `/api/health` | public, no auth |
| Preflight / Allow discovery | `OPTIONS` | each resource | see A5 |

### A2  Non-CRUD as sub-resource

`cancel`, `checkout`, `setAvailability` are not CRUD. They are modelled as **`POST` to a sub-resource**: `POST /orders/42/cancellation` (not `POST /cancelOrder`), `POST /orders/42/checkout`, `POST /products/7/availability`. The URL contains only nouns; the verb is the HTTP method.

### A3  Safe & idempotent

| Endpoint | Safe (changes nothing) | Idempotent (repeat = same effect) | Notes |
|---|---|---|---|
| `GET /api/orders/{id}` | ✓ | ✓ | never changes state |
| `GET /api/orders?...` | ✓ | ✓ | pure read — paginated/filtered |
| `GET /api/health` | ✓ | ✓ | |
| `OPTIONS *` | ✓ | ✓ | read of allowed methods |
| `POST /api/orders` | ✗ | **✗** | not idempotent — duplicate does real damage (extra order, extra charge). Made retry-safe by `Idempotency-Key` (C3) |
| `POST /cancellation` | ✗ | **✗** | non-idempotent; second cancel would be a state conflict. Guarded by domain check + `202` |
| `PUT /api/orders/{id}` | ✗ | ✓ | replacing with same state is a no-op |
| `PATCH /api/orders/{id}` | ✗ | ✓* | advancing `PENDING→PAID` twice: second yields `409` — still safe to retry (no duplicate side-effect) |
| `DELETE /api/orders/{id}` | ✗ | ✓ | second delete is `204` again (soft) |

No `GET` ever changes state.

### A4  Reads take query params

`GET /api/orders?user_id=...&status=PENDING_PAYMENT&sort=created_at&page=1&limit=20` is a **pure read** that filters/sorts/paginates entirely through the query string. The server counts total matches, slices by `page/limit`, and returns `X-Total-Count`. Question 7 covers when `POST` would be justified instead.

### A5  OPTIONS + Allow, and override

Every resource responds to `OPTIONS` with `204 No Content` and an `Allow` header listing its methods:

```
OPTIONS /api/orders      → Allow: GET, POST, OPTIONS
OPTIONS /api/orders/{id} → Allow: GET, PATCH, PUT, DELETE, OPTIONS
OPTIONS /cancellation   → Allow: POST, OPTIONS
```

**`X-HTTP-Method-Override` fallback (documented, constrained-client only):** if a client cannot send `PUT/PATCH/DELETE` (e.g. legacy form or firewall), it may send `POST` with `X-HTTP-Method-Override: PATCH|PUT|DELETE` and the server rewrites `REQUEST_METHOD` before routing. This is a fallback, not the primary path — normal clients send the real method.

### A6  One full exchange (labelled, with HTTP version)

**Request** (`POST /api/orders` create):

```
POST /api/orders HTTP/1.1          ← request line: method, path, HTTP version
Host: localhost:5001
Authorization: Bearer tok_student_abc123
Content-Type: application/json
Accept: application/json
Idempotency-Key: 11111111-2222-3333-4444-555555555555
Content-Length: 178

{
  "user_id": "user_abhi_01",
  "address_id": "addr_01",
  "items": [
    {"product_id": "prod_001", "product_name": "Urban Daypack 25L", "unit_price": 899, "quantity": 2}
  ],
  "total_amount": 1798
}
```

**Response** (`201 Created`):

```
HTTP/1.1 201 CREATED                ← status line: HTTP version, code, reason phrase
Content-Type: application/json
Location: /api/orders/385e5c89-a248-460e-8f88-0ac8f6336f8d
ETag: W/"a1b2c3d4e5f67890"
Cache-Control: no-store
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 19
Access-Control-Allow-Origin: *
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Length: 340

{
  "id": "385e5c89-a248-460e-8f88-0ac8f6336f8d",
  "user_id": "user_abhi_01",
  "address_id": "addr_01",
  "items": [{"product_id": "prod_001", "product_name": "Urban Daypack 25L", "unit_price": 899, "quantity": 2}],
  "total_amount": 1798.0,
  "status": "PENDING_PAYMENT",
  "created_at": "2026-10-13T17:43:36.449763+00:00",
  "updated_at": "2026-10-13T17:43:36.449763+00:00"
}
```

Note: request line carries `HTTP/1.1`; responses use `HTTP/1.1` (status line).

---

## Part B + D2 — Headers table (endpoint × request headers × response headers)

| Endpoint | Request headers needed | Response headers set |
|---|---|---|
| `POST /api/orders` | `Authorization: Bearer …` *(req)*, `Content-Type: application/json`, `Accept: application/json` *(else 406)*, `Idempotency-Key: uuid` *(opt)*, `Accept-Encoding: gzip` *(opt)* | `201 Location`, `ETag`, `Cache-Control: no-store`, `Content-Type: application/json`, `Idempotency-Key` (echo), `Idempotency-Replayed: true` on replay, `X-RateLimit-*`, `Access-Control-Allow-Origin`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`, `Content-Encoding: gzip` (if large + client accepts) |
| `GET /api/orders/{id}` | `Authorization`, `Accept`, `If-None-Match: W/"…"` *(opt → 304)* | `200 ETag`, `Cache-Control: private, max-age=60`, `Content-Type: application/json`; or `304 Not Modified` (no body) with `ETag`; `Date`, `Server` (Flask defaults), `X-RateLimit-*`, CORS, HSTS |
| `GET /api/orders?...` | `Authorization`, `Accept` | `200 Content-Type: application/json`, `Cache-Control: no-store`, `X-Total-Count`, `X-RateLimit-*`, CORS, HSTS; `Content-Encoding: gzip` for large lists |
| `PATCH /api/orders/{id}` | `Authorization`, `Content-Type`, `Accept`, `If-Match: W/"…"` *(412 on mismatch)*, `X-HTTP-Method-Override` *(fallback)* | `200 ETag`, `Cache-Control: no-store`, `X-RateLimit-*`, CORS, HSTS |
| `PUT /api/orders/{id}` | same as PATCH | `200 ETag`, `Cache-Control: no-store`, HSTS |
| `DELETE /api/orders/{id}` | `Authorization`, `If-Match` *(opt → 412)*, `X-HTTP-Method-Override: DELETE` *(fallback)* | `204 No Content`, `Cache-Control: no-store`, HSTS |
| `POST /…/cancellation` | `Authorization`, `Content-Type`, `Accept` | `202 ETag`, `Cache-Control: no-store`, HSTS |
| `OPTIONS *` | `Origin` *(browser preflight)* | `204 Allow`, `Access-Control-Allow-Origin: *`, `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers` |
| `GET /api/health` | *(public)* | `200 Cache-Control: no-store`, `Access-Control-Allow-Origin: *` |

General headers on every response: `Date`, `Server: Werkzeug/...`, `Access-Control-Allow-Origin: *` (B6), `Access-Control-Allow-Methods/Headers`, `Access-Control-Expose-Headers`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security` (B7), `X-RateLimit-Limit/Remaining` (B5), `Content-Type: application/json` (B1).

---

## Part C — Caching & safe retries

### C1  Conditional GET → 304

Single-item `GET` returns `ETag: W/"…"` (hash of `id:status:updated_at`) and `Cache-Control: private, max-age=60`. A client that already holds an ETag may send `If-None-Match: W/"…"`. When it still matches, the server returns `304 Not Modified` with **no body**, saving bandwidth and client re-parse.

### C2  Conditional write → 412

Writers (`PATCH/PUT/DELETE`) accept `If-Match: W/"…"`. If the header is present but the ETag no longer matches (another editor changed the resource), the server returns `412 Precondition Failed` with the current `ETag` instead of overwriting — two editors cannot clobber each other.

### C3  Idempotency key (from Assignment 4 C7)

`POST /api/orders` (and any retried create to Payments with `Idempotency-Key`) stores the key with the record; a repeat with the same key returns the original `200` with `Idempotency-Replayed: true` and does **not** create a duplicate. A duplicate would do real damage here: an extra order and, when `CALL_PAYMENTS=1`, an extra charge via `payment_client.call_payments_create_order(..., idempotency_key=key)` which retries only with that key and never retries `4xx`.

### C4  Safe-retry plan (per risky endpoint, mechanism, why — built from A3 safe×idempotent split)

| Risky endpoint | Safe? / Idempotent? | Retry mechanism | Why this mechanism |
|---|---|---|---|
| `POST /api/orders` | neither | **`Idempotency-Key`** | create is not safe nor idempotent — duplicate would double-create + double-charge. Keyed de-dup is the only safe retry |
| `POST /api/orders/{id}/cancellation` | neither | **domain guard + `202` + `If-Match`** | second cancel is a domain refusal; idempotency key could also be added, but 202 + status guard suffices |
| `GET /api/orders/{id}` | safe, idempotent | **`If-None-Match → 304`** | safe reads never need idempotency keys; ETag validation saves transfer |
| `GET /api/orders?...` | safe, idempotent | **none** (naturally retry-safe) | pure read — retry is free; no conditional needed |
| `PATCH /api/orders/{id}` | not safe, idempotent* | **`If-Match → 412`** | retry must not silently overwrite a concurrent edit; If-Match gives lost-update protection |
| `PUT /api/orders/{id}` | not safe, idempotent | **`If-Match → 412`** | same — idempotent replacement is safe to retry but still needs precondition to avoid clobbering |
| `DELETE /api/orders/{id}` | not safe, idempotent | **`If-Match → 412`** | second delete is harmless, but concurrent PUT+DELETE needs the same guard |

---

## Eight answers (NOTES.md questions)

### 1. For three of your endpoints, give the method, the success status, and the single response header that matters most — and why.

1. **`POST /api/orders` → `201 Created` + `Location: /api/orders/{id}`** — without `Location` the client has no URI for the new resource and cannot `GET`/link it; `201` without `Location` is incomplete.
2. **`GET /api/orders/{id}` → `200 OK` + `ETag: W/"…"`** — the ETag is the resource version token that powers `If-None-Match` (304) and `If-Match` (412); without it, caching and lost-update protection are impossible.
3. **`DELETE /api/orders/{id}` → `204 No Content`** (with `Cache-Control: no-store`) — `204` signals success with intentionally no body; adding spurious JSON to a delete violates the uniform interface and misleads caches.

### 2. Which endpoints are safe, which are idempotent? Which one is neither, and how did you make it retry-safe?

See A3 table above. **Safe:** all `GET` and `OPTIONS` (read-only). **Idempotent:** `GET`, `OPTIONS`, `PUT`, `PATCH` (idempotent in HTTP sense — repeating the same payload yields the same state), `DELETE`. **Neither safe nor idempotent:** `POST /api/orders` (and `POST /cancellation`). The non-idempotent create was made retry-safe by **`Idempotency-Key`**: the server stores `internal_idempotency_key` with the `Order`, and any replay with the same key returns the original `200` without creating a duplicate order or calling Payments twice. The Payments outbound call itself carries the same key and `never retries 4xx` (per `payment_client.py`).

### 3. Show one ETag from your service, the request that returns 304, and the write that returns 412. What does each save or prevent?

```
# GET returns ETag
GET /api/orders/385e5c89-a248-460e-8f88-0ac8f6336f8d HTTP/1.1
Authorization: Bearer tok_student_abc123
Accept: application/json

HTTP/1.1 200 OK
ETag: W/"3f7a9e1c5b8d2046"
Cache-Control: private, max-age=60

{"id":"385e5c89-…","status":"PENDING_PAYMENT", …}
```

```
# 304 — client sends that ETag
GET /api/orders/385e5c89-a248-460e-8f88-0ac8f6336f8d HTTP/1.1
Authorization: Bearer tok_student_abc123
Accept: application/json
If-None-Match: W/"3f7a9e1c5b8d2046"

HTTP/1.1 304 Not Modified
ETag: W/"3f7a9e1c5b8d2046"
Cache-Control: private, max-age=60
(no body)
```

`304` **saves** re-transfer and re-parse of an unchanged resource (bandwidth + CPU).

```
# 412 — two editors race; second writer holds stale ETag
PATCH /api/orders/385e5c89-a248-460e-8f88-0ac8f6336f8d HTTP/1.1
Authorization: Bearer tok_student_abc123
Content-Type: application/json
If-Match: W/"old-etag-from-before-the-other-edit"

{"status":"PAID"}

HTTP/1.1 412 Precondition Failed
ETag: W/"new-etag-after-first-edit"
Content-Type: application/json

{"type":"…/problems/precondition-failed","title":"Precondition Failed","status":412,"detail":"ETag mismatch…"}
```

`412` **prevents** lost-update / clobbering — the second editor must re-read and merge.

### 4. You return 422 for one case and 400 for another. Give the exact request that triggers each, and explain the difference.

**`400 Bad Request` — malformed body (syntax/shape error, fails `validate_*`):**

```http
POST /api/orders HTTP/1.1
Authorization: Bearer tok_student_abc123
Content-Type: application/json

{"user_id":"user_abhi_01"}
```

→ `400 {"title":"Bad Request","detail":"missing required field: address_id"}` — the JSON shape itself is wrong; no domain rule is involved.

**`422 Unprocessable Entity` — semantically valid body that the domain refuses (assignment's distinction, after RFC 4918):**

```http
POST /api/orders/9ca48017-0e5f-4087-8b0d-5146241c0100/cancellation HTTP/1.1
Authorization: Bearer tok_student_abc123
Content-Type: application/json

{"reason":"Too late"}
```

where that order's `status` is `SHIPPED`.

→ `422 {"title":"Unprocessable Entity","detail":"order cannot be cancelled in status SHIPPED"}` — the body is well-formed JSON with required fields, but the domain state machine says "no."

### 5. A browser page on another origin calls your API and is blocked — yet your server logs show a 200. Who blocked it, and which response header fixes it?

The **browser** blocked it (same-origin policy / CORS enforcement), not the server. The server did return `200`, but before JavaScript can read the response the browser checks for `Access-Control-Allow-Origin`. If it is missing or does not match the requesting `Origin`, the browser discards the response and fires a CORS error. **Fix:** add `Access-Control-Allow-Origin: *` (or the specific origin) and, for preflighted requests, `Access-Control-Allow-Methods` + `Access-Control-Allow-Headers`. This service sets `Access-Control-Allow-Origin: *` on **every** response (see `after_request`), plus `204` `OPTIONS` preflight with `Access-Control-Allow-Methods: GET, POST, PATCH, PUT, DELETE, OPTIONS` and `Access-Control-Allow-Headers: Content-Type, Authorization, Accept, Idempotency-Key, If-Match, If-None-Match, X-HTTP-Method-Override`.

### 6. Name one response where you set Cache-Control to allow caching and one where you must use no-store. Why each?

- **Allow caching:** `GET /api/orders/{id}` → `Cache-Control: private, max-age=60`. A single order read is idempotent and personal; caching for 60s with ETag validation reduces origin hits without staleness risk (`private` so shared caches do not cross users).
- **no-store:** `POST /api/orders` (`201`), `PATCH/PUT/DELETE`, `POST /cancellation` (`202`), and `GET /api/orders?...` list. The create/delete/cancel responses reflect mutable state and, for the list, user-specific filtered results — storing them would risk serving stale order state or leaking one user's list to another. `no-store` guarantees intermediaries do not cache them.

### 7. Your search endpoint is a GET. When would POST be the right choice instead, and what do you give up by switching?

Use `POST` (e.g. `POST /api/orders/search` with a JSON body) when the **filter is too large or too structured for a URL**: complex multi-field bag filters, very long lists of `product_id`, rich JSON predicates, or a body that would exceed URL length limits (~2000 chars) or expose sensitive terms in `Referer`/logs. By switching to `POST` you **give up**: cacheability (POST responses are not cacheable by default and cannot be keyed by URL+query), bookmarkability/shareability, idempotency/safety semantics (POST is neither), and the ability to `304` via `If-None-Match` on the exact query string — intermediaries and browsers treat the two methods fundamentally differently.

### 8. Location appears on a 201 and on a 3xx. What does it point to in each case?

- **`201 Created`:** `Location: /api/orders/{id}` points to the **newly created resource itself** — the URI the client should `GET` to read it. Example: `Location: /api/orders/385e5c89-…`.
- **`3xx Redirect`** (e.g. `301`, `302`, `307`, `308`): `Location` points to the **redirect target** — where the client should retry the request (possibly with a different method per code). The two uses look identical but mean different things: creation announcement vs navigation instruction.

---

## Evidence

### OpenAPI validator

```
$ python -c "from openapi_spec_validator import validate_spec; import yaml; spec=yaml.safe_load(open('openapi.yaml')); validate_spec(spec); print('VALIDATOR: 0 errors')"
VALIDATOR: 0 errors
```

(see `validator-output.txt`)

### Pytest

```
$ python -m pytest tests -v
… 12 passed (method map, negotiation, auth, ETag/304/412, rate-limit, CORS, gzip, idempotency)
```

(see `pytest-output.txt`)

### Curl -v

```
$ python generate_transcript.py
→ curl-transcript.txt
```

contains (D1 required): `201 + Location`, same `Idempotency-Key` replay `200 + Idempotency-Replayed: true`, conditional `304`, conditional `412`, plus `400`, `404`, `401` failures — all with `curl -v` (request + response headers + `HTTP/1.1`).
