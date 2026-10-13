# CampusEats — External SOAP Partner Integration (Assignment 3)

**TeamID:** MCA-CS543-G07  |  **Course:** CS543 Web Services  |  **Date:** 13 Oct 2026

| Roll / Name | Role in Assignment 2 | Responsibility in this integration |
|---|---|---|
| Abhishek | Auth + Payment | WSDL authoring, fault mapping |
| Binamra Rana | Auth + Payment | SOAP envelopes, HTTP binding |
| Navendu | Auth + Order | Discovery / registry entry |
| Shruti | Catalogue + Order | Documentation (integration.pdf) |
| Yatindra | Catalogue + Order + Payment | Verification & packaging |

> Note: This project is the **Ecommerce-1 bags store** (backpacks / laptop bags / sling bags) built with the MERN stack. The repository name is `Ecommerce-1`; the assignment brief still refers to it as `CampusEats` (bags for college students). Behaviour and services are identical.

---

## 1. Context — Partner edge and why SOAP

**Chosen partner:** **SecurePay Gateway** — external payment gateway.  
**Operation integrated:** `charge(orderRef, amount, currency, cardToken, studentEmail) → ChargeResponse(transactionId, status, amountCharged, authCode, gatewayRef)` with `PaymentFault(code, reason, retryable)`.

**Why this edge is SOAP while the rest of CampusEats is REST (3–4 sentences):**

The payment edge needs a **strong contract** — the WSDL fixes types, required fields and faults before any code runs, so CampusEats and the bank cannot drift. It needs **message-level security** (credentials in the SOAP Header, `mustUnderstand`, and an XML Signature point) rather than only transport TLS, because the charge traverses intermediaries. It needs **transactional guarantees** — the charge is atomic and idempotent with a `gatewayRef`/`authCode` that CampusEats stores exactly as the Assignment 2 `payments` table expects. The rest of CampusEats stays REST because product search, cart and catalogue are resource-oriented, cacheable and human-driven; payment is the only partner edge where ACID-style assurance and a frozen contract outweigh REST's flexibility.

The REST surface from Assignment 2 remains unchanged (`GET /api/products`, `GET /api/products/:id`, `POST /api/payment/order`, `POST /api/payment/verify`). The SOAP partner is consumed only by the Payment Service at checkout and never exposed to the student.

---

## 4. HTTP Binding — the POST that carries the SOAP envelope

The WSDL's `<soap:binding>` declares `style="document"` and `transport="http://schemas.xmlsoap.org/soap/http"` over HTTP. The consumer (CampusEats Payment Service) therefore sends a single `POST` to the service/port endpoint:

```
POST /soap/PaymentGateway HTTP/1.1
Host: api.securepay.example.com
Content-Type: text/xml; charset=utf-8
Content-Length: 892
SOAPAction: "http://securepay.example.com/payment/charge"
Connection: keep-alive

<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:pay="http://securepay.example.com/payment">
  <soap:Header>
    <pay:AuthHeader soap:mustUnderstand="1">
      <pay:merchantId>CAMPUSEATS_MERCH_8421</pay:merchantId>
      <pay:apiKey>sp_test_9f3k2pLq8xW1vT4yZ</pay:apiKey>
      <pay:timestamp>2026-10-13T17:30:00Z</pay:timestamp>
      <pay:nonce>6f8a9c1e-4b2d-4f0a-9c3e-1a2b3c4d5e6f</pay:nonce>
    </pay:AuthHeader>
  </soap:Header>
  <soap:Body>
    <pay:Charge>
      <pay:orderRef>ORD_20261013_001</pay:orderRef>
      <pay:amount>2698.00</pay:amount>
      <pay:currency>INR</pay:currency>
      <pay:cardToken>tok_visa_4242_securepay</pay:cardToken>
      <pay:studentEmail>abhishek.student@campuseats.example.com</pay:studentEmail>
    </pay:Charge>
  </soap:Body>
</soap:Envelope>
```

* `SOAPAction` is taken verbatim from `binding/operation/soap:operation/@soapAction` in `partner.wsdl`.
* `Content-Type: text/xml; charset=utf-8` is the SOAP 1.1 binding required by the WSDL (SOAP 1.2 would use `application/soap+xml`).
* The endpoint `https://api.securepay.example.com/soap/PaymentGateway` is taken from `service/port/soap:address/@location`.
* A successful HTTP status is `200 OK` with a SOAP envelope in the body (`soap-response.xml`); a fault still returns `500 Internal Server Error` with a `soap:Fault` (`soap-fault.xml`).

---

## 5. Discovery (modern form) — how CampusEats obtains the WSDL

No live UDDI server is run (per the brief). Discovery is at **design-time** in two equivalent modern forms:

**a) Direct URL (contract-first download):** The gateway publishes its WSDL at a stable URL that CampusEats binds to at build time:

```
WSDL URL: https://api.securepay.example.com/soap/PaymentGateway?wsdl
Endpoint: https://api.securepay.example.com/soap/PaymentGateway
```

**b) Catalogue / registry lookup (tModel-style pointer):** In production CampusEats would not hard-code the WSDL; an internal **Service Catalogue** (e.g. Backstage / API gateway registry / WSO2 Goverance Registry) holds one record that points to that WSDL as a `tModel`. The developer searches the catalogue for "SecurePay" and the catalogue returns the WSDL location plus the `SOAPAction`. This satisfies the "modern UDDI" requirement without running a UDDI node.

### One-record catalogue / registry entry (JSON — tModel-style)

```json
{
  "businessEntity": {
    "name": "SecurePay Technologies Pvt. Ltd.",
    "description": "PCI-DSS certified payment gateway partner for CampusEats",
    "contact": "partner-support@securepay.example.com"
  },
  "businessService": {
    "serviceKey": "uddi:securepay.example.com:service:payment-gateway",
    "name": "SecurePay PaymentGatewayService",
    "description": "SOAP service for charging student card tokens (CampusEats edge)"
  },
  "bindingTemplate": {
    "bindingKey": "uddi:securepay.example.com:binding:payment-soap-http",
    "accessPoint": "https://api.securepay.example.com/soap/PaymentGateway",
    "accessPointType": "https",
    "bindingDetail": "SOAP 1.1 over HTTP, document/literal"
  },
  "tModel": {
    "tModelKey": "uddi:securepay.example.com:tmodel:payment-wsdl",
    "name": "SecurePay Payment WSDL",
    "overviewURL": "https://api.securepay.example.com/soap/PaymentGateway?wsdl",
    "overviewDoc": "WSDL defining portType PaymentPortType with operation charge; binding PaymentBinding (SOAP/HTTP); service PaymentGatewayService",
    "categoryBag": ["uddi:types:wsdl", "protocol:soap-http", "domain:payment"]
  }
}
```

This single record lets CampusEats discover: *who* (business), *what* (service + operation `charge`), *where* (endpoint), and *how* (WSDL/tModel). The WSDL itself is the contract bound at compile time.

---

## 6. Fault Mapping — partner vocabulary does not leak

CampusEats' Assignment 2 contract (`schema.sql` — `orders.status = PENDING_PAYMENT | PAID | … | CANCELLED`, `payments.status = CREATED | PAID | FAILED`) promises a **single student-facing error** for checkout. The SOAP partner's fine-grained fault must be **translated** at the Payment Service boundary:

| SecurePay `PaymentFault.code` | `reason` / `retryable` | CampusEats Assignment 2 mapping |
|---|---|---|
| `card_declined` | Insufficient funds / limit exceeded, `retryable=false` | `POST /api/payment/verify` → `400 { success:false, message:"payment declined" }`; `payments.status=FAILED`, `orders.status=CANCELLED` |
| `invalid_token` | Token expired / malformed, `retryable=false` | `400 { success:false, message:"payment declined" }`; do not retry, ask student to re-enter card |
| `gateway_timeout` | Upstream timeout, `retryable=true` | `503 { success:false, message:"payment unavailable, try again" }`; keep `orders.status=PENDING_PAYMENT`, allow one idempotent retry with same `orderRef` + `nonce` |
| `duplicate_charge` | `orderRef` already charged | `409 { success:false, message:"payment already processed" }`; return existing `transactionId` idempotently |

**Rule:** The strings `card_declined`, `gateway_timeout`, `PaymentFault` and the SOAP `faultcode` never reach the frontend. The student sees only Assignment 2's vocabulary: **"payment declined"** (do not retry) or **"payment unavailable, try again"** (may retry). Internally the Payment Service logs `transactionId`, `gatewayRef`, `authCode` on success, and `code+reason` on fault, then updates the local `payments` row — preserving the Assignment 2 invariant that every table belongs to one service and cross-service refs are plain IDs.

---

## Submission checklist

- `integration.pdf` (this document) — Tasks 1, 4, 5, 6 + TeamID/Roll/Name
- `partner.wsdl` — Task 2 (six elements present)
- `soap-request.xml`, `soap-response.xml`, `soap-fault.xml` — Task 3 (element-for-element match)
- `Assignment-3.zip` — one Zip containing the above five files, uploaded by Team Leader

All artefacts are **design-time only** — no running SOAP server or live gateway is required.
