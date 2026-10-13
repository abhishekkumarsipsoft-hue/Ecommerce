# CampusEats — Assignment 4 NOTES.md

**TeamID:** MCA-CS543-G07  |  **Course:** CS543 Web Services  |  **Due before Lecture 6**
**Dr. Pramit Mazumdar — pramit.mazumdar@iiitvadodara.ac.in**

| Roll / Name | Assignment 2 role |
|---|---|
| Abhishek | Auth + Payment |
| Binamra Rana | Auth + Payment |
| Navendu | Auth + Order |
| Shruti | Catalogue + Order |
| Yatindra | Catalogue + Order + Payment |

> Repository: `Ecommerce-1` (bags store — backpack / laptop bag / sling bag / duffel). Brief still calls it CampusEats; behaviour identical.

---

## Part A — Model the service

### A1  Pick your service

**Orders** (Order Service from Assignment 2, `Assignment 2/schema.sql`: `cart_items`, `addresses`, `orders`, `order_items`; owned by Navendu/Yatindra/Shruti). It is **not Payments** (Payments was the Tutorial 4 and Assignment 3 subject). Boundaries and data ownership are reused verbatim from Assignment 2; nothing is redesigned. Orders owns the lifecycle `PENDING_PAYMENT → PAID → PACKED → SHIPPED → DELIVERED` and the `CANCELLED` branch.

### A2  Operations you would have written as SOAP (WSDL style — starting point, not the answer)

```
placeOrder(userId, addressId, items[], totalAmount) -> orderId
getOrder(orderId) -> Order
listOrders(userId?, status?) -> Order[]
cancelOrder(orderId, reason) -> Order
updateOrderStatus(orderId, newStatus) -> Order
```

In Assignment 3 the single SOAP operation was `charge(orderRef, amount, currency, cardToken, studentEmail)`. The table above is the Orders analogue — five RPC verbs that would each have been a `<portType><operation>` with its own `<message>` and `<fault>`.

### A3  Find the nouns

Every verb creates or mutates the same durable thing: an **order**. The cancellation is not a verb endpoint — it is a **sub-resource** of an order. No verb survives into the URL:

- `placeOrder` → `POST /api/orders` creates an **orders** collection member
- `getOrder` → `GET /api/orders/{orderId}` reads one **order**
- `listOrders` → `GET /api/orders?user_id=&status=` reads the filtered **orders** collection
- `cancelOrder` → `POST /api/orders/{orderId}/cancellation` creates a **cancellation** sub-resource of an order
- `updateOrderStatus` → `PATCH /api/orders/{orderId}/status` mutates the **order**'s state (used to demonstrate 409)

### A4  Resource table (5 columns, 5 rows — minimum was 4, one must be a sub-resource)

| Method | URL | What it does | Success code | Failure codes |
|---|---|---|---|---|
| `POST` | `/api/orders` | Create a new order (PENDING_PAYMENT) from cart items; validates body, enforces idempotency, optionally calls Payments | `201 Created` + `Location: /api/orders/{id}` | `400` malformed body / total mismatch, `422` domain refuses, `502` payments unreachable |
| `GET` | `/api/orders/{orderId}` | Read a single order | `200 OK` | `404` not found |
| `GET` | `/api/orders?user_id=&status=` | Filtered list of orders (query-string filters, not path segments) | `200 OK` | `400` invalid status filter |
| `POST` | `/api/orders/{orderId}/cancellation` | **Sub-resource** — cancel an order; state-changing, returns 202 because refund continues async | `202 Accepted` | `400` bad reason, `404` not found, `409` already cancelled, `422` domain refuses (SHIPPED/DELIVERED) |
| `PATCH` | `/api/orders/{orderId}/status` | Advance order status (admin drive); used to exercise 409 conflicts | `200 OK` | `400` invalid status, `404` not found, `409` illegal transition / already in that status |

### A5  Justify one hard choice

The operation that mapped least comfortably was **`cancelOrder`**. As a verb it wants `POST /cancelOrder` or `DELETE /orders/{id}`, but `DELETE` implies the resource disappears, while a cancelled order must remain queryable (Assignment 2 `orders.status=CANCELLED` with `cancellation.reason`). Treating cancellation as a **sub-resource** `POST /api/orders/{orderId}/cancellation` resolved it: the order persists, the cancellation is a creation event with its own reason and timestamp, and the `202` correctly signals that refund work continues after the reply. Rejected alternatives were `DELETE /api/orders/{id}` (lossy — no reason stored), `PUT /api/orders/{id}` with `status=CANCELLED` (leaks state-machine into a generic update), and `POST /api/orders/{id}/cancel` (verb in URL, violates A3).

---

## Part D — D3 Fallback reasoning

When the Payments dependency is unreachable (`timeout` or `5xx` after all retries), **Orders does not fail the create**. It persists the order as `PENDING_PAYMENT` and returns `201` anyway, leaving payment reconciliation to an async retry/reconciliation job. Failing the create (returning `502` and discarding the order) would have been wrong here because the student's cart and chosen address are already validated and durable; losing them on a transient gateway blip destroys user work and forces a full cart rebuild. The order is the source of truth, payments is a side-effect — degrading to `PENDING_PAYMENT` keeps the invariants of Assignment 2 intact (`orders.status` tracks reality, `payments.status` may stay `CREATED` until retried). The client is told payment is pending, not that the order vanished.

The hardened call that would have triggered this path is in `payment_client.py`: resolved from `PAYMENTS_SERVICE_URL` (never hard-coded), `timeout=2.0s`, up to 3 retries with exponential backoff (`0.2·2^attempt`) plus jitter, **never retrying `4xx`** and always carrying `Idempotency-Key` on the retried `POST /api/payment/order`.

---

## Answers to the five NOTES.md questions

### 1. Count the lines in your Assignment 3 WSDL and in your openapi.yaml. What is the difference actually made of? Name two things the WSDL declared that the OpenAPI file does not need to.

- `Assignment 3/partner.wsdl` — **127 lines**
- `Assignment 4/openapi.yaml` — **375 lines**

The OpenAPI file is longer because it documents **five resources, query/header parameters, five success codes (200/201/202), headers (`Location`, `Idempotency-Key`), and a shared `Problem` schema reused via `$ref`** — all things the single-operation WSDL compressed into one `<portType><operation>`. Two things the WSDL declared that OpenAPI does not need:

1. **`message` and `portType` wrappers** — WSDL must declare an abstract `message` for each header/body part and a `portType` that binds them into an operation; OpenAPI maps HTTP methods and paths directly to requestBody/response without this indirection.
2. **`binding` with `soap:binding`, `soap:operation/@soapAction`, `soap:address/@location`** — the SOAP envelope framing, transport, and SOAPAction header that WSDL must spell out. OpenAPI assumes `HTTP + JSON` and needs no envelope/binding descriptor (Content-Type is just `application/json`).

### 2. Quote one soap:Fault from your Assignment 3 work and show the status code and problem body that replaced it. Why is returning that error inside a 200 OK a problem for the network in between?

Assignment 3 `soap-fault.xml`:

```xml
<soap:Fault>
  <faultcode>soap:Server</faultcode>
  <faultstring>Payment declined by issuer</faultstring>
  <detail>
    <pay:PaymentFault>
      <pay:code>card_declined</pay:code>
      <pay:reason>Insufficient funds / card limit exceeded for order ORD_20261013_001</pay:reason>
      <pay:retryable>false</pay:retryable>
      <pay:orderRef>ORD_20261013_001</pay:orderRef>
    </pay:PaymentFault>
  </detail>
</soap:Fault>
```

HTTP on the wire for that fault was `500 Internal Server Error` with the Fault as the body (per SOAP convention).

Replacement in Assignment 4 (Orders cancellation refusal when trying to cancel a SHIPPED order):

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "type": "https://campuseats.example.com/problems/unprocessable",
  "title": "Unprocessable Entity",
  "status": 422,
  "detail": "order cannot be cancelled in status SHIPPED"
}
```

(Other mappings: `card_declined`/`invalid_token` → `400` or `422` with `Problem`; `gateway_timeout` → `502` — see NOTES.md fault mapping in Assignment 3.)

**Why a `200 OK` with an error inside the body is harmful:** intermediaries (CDNs, proxies, browser caches, load balancers) treat `200` as cacheable success. They may cache the "error-as-success" response and serve it to other clients, retry logic and circuit breakers will not trigger (they key on status codes), and monitoring/alerting that counts `4xx/5xx` will miss the failure entirely. The network can no longer tell success from failure without parsing every body, violating the uniform interface.

### 3. Which of UDDI's three moves — publish, find, bind — still exist in your new setup, and which disappeared? Explain what took over the job.

- **Publish** — still exists. In Assignment 3 it was a `businessEntity/businessService/tModel` record published to a UDDI-style catalogue pointing at `https://api.securepay.example.com/soap/PaymentGateway?wsdl`. In Assignment 4 it is `openapi.yaml` published to a service registry / API gateway / Backstage catalogue (and the `PAYMENTS_SERVICE_URL` in config). The artefact published changed from WSDL+tModel to OpenAPI+env discovery, but the act of publishing does.
- **Find** — still exists but is now **human + DNS/env**, not a UDDI inquiry. Assignment 3 found the WSDL via catalogue lookup; Assignment 4 finds the Orders/Payments addresses via the registry UI or, at runtime, `PAYMENTS_SERVICE_URL` from the environment (or Kubernetes DNS / Consul). No UDDI `find_business`/`find_service` call — the gateway or container orchestrator does the finding.
- **Bind** — **disappeared as a runtime UDDI step**. WSDL binding required generating a SOAP stub from the WSDL's `binding` and `soap:address` at compile time. REST binding is just `fetch(openapi.servers[0] + path, {method, headers})` with `Content-Type: application/json` — no code generation, no SOAP envelope or SOAPAction. The OpenAPI file is documentation and validation input, not a compiled stub.

### 4. Your XML Schema was enforced before your code ran; your OpenAPI schema is not. Name the specific function in your code that now carries that responsibility, and one failure that would get through if you had not written it.

The responsibility is carried by **`validate_create_order(body)`** (and `validate_cancellation(body)`) in `app.py`. It is called at the top of `POST /api/orders` and `POST /api/orders/{id}/cancellation` **before** any `store.*` access — exactly the spot where Assignment 3's XSD validator would have rejected the message before the handler saw it.

One failure that would get through without it: a client sending

```json
{"user_id":"u1","address_id":"a1","items":[{"product_id":"p1","product_name":"Bag","unit_price":"cheap","quantity":1}],"total_amount":899}
```

`unit_price` is the string `"cheap"` instead of a number. The OpenAPI schema declares `unit_price: type: number` but Flask does **not** enforce it — without `validate_create_order` the code would reach `float(it["unit_price"])` and raise an unhandled `ValueError` (500), or worse, persist a broken `total_amount` that does not equal the sum of items. With the validator it returns a clean `400 Problem { detail: "items[0].unit_price must be a number" }`.

### 5. Name one part of your service where you would still choose the SOAP stack over REST, and state exactly what guarantee you would be buying. Answering “nowhere” needs a stronger argument than answering “somewhere”.

**Somewhere — the payment side-effect inside `POST /api/orders` when it calls Payments.**

If Orders had to **atomically** charge the card and create the order so that neither can succeed without the other, I would still choose SOAP (WS-AtomicTransaction / two-phase commit with the SecurePay gateway) over REST. The guarantee bought is **distributed atomicity**: the `charge` and the order write either both commit or both roll back, with a coordinator that can recover after a crash. REST with `Idempotency-Key` + retry + `PENDING_PAYMENT` fallback (what this assignment implements) gives **at-least-once with idempotent de-duplication** but not atomicity — a crash between persisting `PENDING_PAYMENT` and hearing `APPROVED` leaves a dangling order that needs an out-of-band reconciler. For the bag store the reconciler is acceptable; for a funds-at-risk ledger it is not — there I would pay for SOAP's WS-AT.

---

## Validator and test evidence

OpenAPI validation:

```
$ python -c "from openapi_spec_validator import validate_spec; import yaml; spec=yaml.safe_load(open('openapi.yaml')); validate_spec(spec); print('VALIDATOR: 0 errors')"
VALIDATOR: 0 errors
```

Pytest (4 tests):

```
$ python -m pytest tests -v
tests/test_orders.py::test_create_succeeds_with_201_and_location PASSED
tests/test_orders.py::test_idempotent_repeat_returns_original PASSED
tests/test_orders.py::test_failure_path_returns_4xx_problem PASSED
tests/test_orders.py::test_unknown_id_returns_404 PASSED
4 passed
```

See `curl-transcript.txt` (with `curl -i`) for the six required interactions.
