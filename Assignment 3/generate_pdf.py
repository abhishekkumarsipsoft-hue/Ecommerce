#!/usr/bin/env python3
import pathlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted, PageBreak, HRFlowable
from reportlab.lib import colors

OUT = pathlib.Path(__file__).with_name("integration.pdf")

styles = getSampleStyleSheet()

COLORS = {
    "primary": HexColor("#1a365d"),
    "accent": HexColor("#2b6cb0"),
    "muted": HexColor("#4a5568"),
    "light": HexColor("#edf2f7"),
    "border": HexColor("#cbd5e0"),
    "code_bg": HexColor("#1a202c"),
    "code_fg": HexColor("#e2e8f0"),
}

sTitle = ParagraphStyle("Title2", parent=styles["Title"], fontSize=18, textColor=COLORS["primary"], spaceAfter=4, alignment=TA_CENTER)
sSubtitle = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=9, textColor=COLORS["muted"], alignment=TA_CENTER, spaceAfter=6)
sH1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=13, textColor=COLORS["primary"], spaceBefore=14, spaceAfter=6, borderPadding=(0,0,4,0))
sH2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=11, textColor=COLORS["accent"], spaceBefore=10, spaceAfter=4)
sBody = ParagraphStyle("Body2", parent=styles["Normal"], fontSize=8.5, leading=12, alignment=TA_JUSTIFY, spaceAfter=4, textColor=HexColor("#1a202c"))
sBullet = ParagraphStyle("Bullet2", parent=sBody, leftIndent=14, bulletIndent=6, spaceAfter=2)
sCell = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=7.5, leading=10, textColor=HexColor("#1a202c"))
sCellHead = ParagraphStyle("CellHead", parent=sCell, textColor=white, fontName="Helvetica-Bold", alignment=TA_CENTER)
sCaption = ParagraphStyle("Caption", parent=styles["Normal"], fontSize=7, textColor=COLORS["muted"], alignment=TA_CENTER, spaceBefore=2, spaceAfter=6)
sCode = ParagraphStyle("Code", parent=styles["Code"], fontSize=6.5, leading=8.5, textColor=COLORS["code_fg"], fontName="Courier")

def P(text, style=sBody):
    return Paragraph(text, style)

def code_block(text, width=170*mm):
    # Use Preformatted inside a table to get dark background
    pf = Preformatted(text, sCode)
    t = Table([[pf]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), COLORS["code_bg"]),
        ("BOX", (0,0), (-1,-1), 0.5, COLORS["border"]),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("ROUNDEDCORNERS", [4,4,4,4]),
    ]))
    return t

def styled_table(headers, rows, col_widths):
    header_cells = [Paragraph(h, sCellHead) for h in headers]
    data = [header_cells]
    for r in rows:
        data.append([Paragraph(c, sCell) for c in r])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0,0), (-1,0), COLORS["primary"]),
        ("TEXTCOLOR", (0,0), (-1,0), white),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, COLORS["light"]]),
        ("GRID", (0,0), (-1,-1), 0.4, COLORS["border"]),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]
    t.setStyle(TableStyle(style))
    return t

def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(COLORS["primary"])
    canvas.setFont("Helvetica-Bold", 7)
    canvas.drawString(15*mm, 282*mm, "CampusEats  |  CS543 Web Services  |  Assignment 3 — External SOAP Partner Integration")
    canvas.setFont("Helvetica", 6)
    canvas.setFillColor(COLORS["muted"])
    canvas.drawString(15*mm, 10*mm, "Design-time only — no running server and no live gateway.   Ecommerce-1 bags store (backpacks / laptop bags / sling bags) — MERN + Razorpay → SecurePay SOAP edge.")
    canvas.drawRightString(195*mm, 10*mm, f"Page {doc.page}")
    canvas.restoreState()

story = []
W = 170*mm

story.append(Paragraph("CampusEats — External SOAP Partner<br/>Integration at the Contract Level", sTitle))
story.append(Paragraph("CS543 Web Services  •  Assignment 3  •  13 Oct 2026  •  Tutorial 3 method", sSubtitle))
story.append(HRFlowable(width="100%", thickness=0.6, color=COLORS["accent"], spaceAfter=6))
story.append(P("<b>TeamID:</b> MCA-CS543-G07 &nbsp;|&nbsp; <b>Repository:</b> campuseats / Ecommerce-1 (bags store) &nbsp;|&nbsp; <b>Stack:</b> MongoDB • Express • React • Node • Razorpay → <b>SecurePay SOAP</b>", ParagraphStyle("meta", parent=sBody, fontSize=7.5, textColor=COLORS["muted"], alignment=TA_CENTER, spaceAfter=4)))

# Team table
story.append(styled_table(
    ["Roll / Name", "Assignment 2 role", "Assignment 3 responsibility"],
    [
        ["Abhishek", "Auth + Payment", "WSDL authoring, fault mapping"],
        ["Binamra Rana", "Auth + Payment", "SOAP envelopes, HTTP binding"],
        ["Navendu", "Auth + Order", "Discovery / registry entry"],
        ["Shruti", "Catalogue + Order", "Documentation (integration.pdf)"],
        ["Yatindra", "Catalogue + Order + Payment", "Verification &amp; packaging"],
    ],
    [42*mm, 48*mm, 80*mm]
))
story.append(Paragraph("Figure 1 — Team composition. Repo name is <i>Ecommerce-1</i>; brief still refers to it as <i>CampusEats</i> (bags for college students). Behaviour and services are identical.", sCaption))
story.append(P("Note on naming: the deployed folder is <b>Ecommerce-1</b> (bags store). The assignment sheet still calls it <b>CampusEats</b> — the brief text even notes: <i>'Naam CampusEats hai kyunki pehle idea canteen ka tha, ab ye campus ke liye bags bechta hai'</i>. All references below use the assignment name CampusEats for compliance; the artefact on disk is Ecommerce-1.", sBody))
story.append(Spacer(1, 2*mm))

# 1 Context
story.append(Paragraph("1 &nbsp; Context — Partner edge and why SOAP", sH1))
story.append(P("<b>Chosen partner:</b> <b>SecurePay Gateway</b> — external payment gateway (alternative: logistics/SMS; payment chosen because it is the only edge with money at risk). &nbsp;<b>Operation integrated:</b> <font face='Courier' size=7>charge(orderRef, amount, currency, cardToken, studentEmail) → ChargeResponse(transactionId, status, amountCharged, authCode, gatewayRef)</font> with <font face='Courier' size=7>PaymentFault(code, reason, retryable)</font>. WSDL service is <font face='Courier' size=7>PaymentGatewayService</font> at <font face='Courier' size=7>https://api.securepay.example.com/soap/PaymentGateway</font>.", sBody))
story.append(Paragraph("Why this edge is SOAP while the rest of CampusEats is REST", sH2))
story.append(P("1. <b>Strong contract.</b> The WSDL freezes types, required fields and the fault schema before any code runs — CampusEats and the bank cannot drift. REST with JSON would need out-of-band coordination.", sBullet))
story.append(P("2. <b>Message-level security.</b> Credentials travel in the SOAP <font face='Courier'>Header</font> with <font face='Courier'>mustUnderstand</font> and a signature point, so they survive intermediaries. The catalogue/cart REST surface needs only transport TLS.", sBullet))
story.append(P("3. <b>Transactions.</b> The <font face='Courier'>charge</font> is atomic and idempotent via <font face='Courier'>gatewayRef / authCode</font> stored exactly as Assignment 2's <font face='Courier'>payments</font> table expects (razorpay_order_id / payment_id / status). ACID-style assurance outweighs REST's cacheability only on this money edge.", sBullet))
story.append(P("4. <b>Rest stays REST</b> because product search, cart and catalogue are resource-oriented, cacheable and human-driven; payment is the sole partner edge where a frozen contract and WS-* guarantees justify SOAP.", sBullet))
story.append(P("The REST surface from Assignment 2 is unchanged: <font face='Courier' size=7>GET /api/products, GET /api/products/:id, POST /api/payment/order, POST /api/payment/verify</font>. The SOAP partner is consumed only by the Payment Service at checkout and never exposed to the student.", ParagraphStyle("small", parent=sBody, fontSize=7, textColor=COLORS["muted"])))

# 2 WSDL summary
story.append(Paragraph("2 &nbsp; Partner WSDL — six elements (partner.wsdl)", sH1))
story.append(P("File <font face='Courier'>partner.wsdl</font> is a complete, valid WSDL 1.1 (document/literal) — the contract CampusEats binds to. It is <b>authored</b>, not generated, per Tutorial 3.", sBody))
story.append(styled_table(
    ["#", "WSDL element", "What it contains in this contract"],
    [
        ["1", "types", "XSD schema tns: AuthHeader (merchantId, apiKey, timestamp, nonce) + Charge + ChargeResponse + PaymentFault"],
        ["2", "message", "AuthHeaderMsg, ChargeRequestMsg, ChargeResponseMsg, PaymentFaultMsg (each wraps one element)"],
        ["3", "portType", "PaymentPortType with one operation <b>charge</b> (input → output, fault PaymentFault)"],
        ["4", "binding", "PaymentBinding — <font face='Courier'>soap:binding style=document transport=soap/http</font>; soapAction <font face='Courier'>http://securepay.example.com/payment/charge</font>"],
        ["5", "service", "PaymentGatewayService (documentation: SecurePay SOAP Payment Gateway)"],
        ["6", "port + address", "PaymentGatewayPort → <font face='Courier'>https://api.securepay.example.com/soap/PaymentGateway</font>"],
    ],
    [8*mm, 30*mm, 132*mm]
))
story.append(Paragraph("Table 1 — Six WSDL elements and their content.", sCaption))
story.append(P("<b>WSDL excerpt — portType + binding (for viva):</b>", sBody))
story.append(code_block("""<portType name="PaymentPortType">
  <operation name="charge">
    <input message="tns:ChargeRequestMsg"/>
    <output message="tns:ChargeResponseMsg"/>
    <fault name="PaymentFault" message="tns:PaymentFaultMsg"/>
  </operation>
</portType>
<binding name="PaymentBinding" type="tns:PaymentPortType">
  <soap:binding style="document" transport="http://schemas.xmlsoap.org/soap/http"/>
  <operation name="charge">
    <soap:operation soapAction="http://securepay.example.com/payment/charge"/>
    <input>
      <soap:header message="tns:AuthHeaderMsg" part="auth" use="literal"/>
      <soap:body parts="parameters" use="literal"/>
    </input>
    <output><soap:body use="literal"/></output>
    <fault name="PaymentFault"><soap:fault name="PaymentFault" use="literal"/></fault>
  </operation>
</binding>
<service name="PaymentGatewayService">
  <port name="PaymentGatewayPort" binding="tns:PaymentBinding">
    <soap:address location="https://api.securepay.example.com/soap/PaymentGateway"/>
  </port>
</service>""", W))
story.append(Spacer(1, 2*mm))

# 3 SOAP messages
story.append(Paragraph("3 &nbsp; SOAP messages by hand (Tasks 3) — element-for-element match", sH1))
story.append(P("All three envelopes use <font face='Courier'>http://securepay.example.com/payment</font> as targetNamespace, match the XSD element names, and validate against the WSDL types. Only design-time — no server.", sBody))
story.append(Paragraph("3.1 &nbsp; Request — credentials in Header, call in Body (soap-request.xml)", sH2))
story.append(code_block("""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
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
</soap:Envelope>""", W))
story.append(Paragraph("3.2 &nbsp; Success response (soap-response.xml)", sH2))
story.append(code_block("""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:pay="http://securepay.example.com/payment">
  <soap:Body>
    <pay:ChargeResponse>
      <pay:transactionId>txn_sp_8a7f3c9d21e44b9a8c1d0e2f</pay:transactionId>
      <pay:status>APPROVED</pay:status>
      <pay:amountCharged>2698.00</pay:amountCharged>
      <pay:authCode>AUTH_482917</pay:authCode>
      <pay:gatewayRef>gw_ref_20261013_001</pay:gatewayRef>
    </pay:ChargeResponse>
  </soap:Body>
</soap:Envelope>""", W))
story.append(Paragraph("3.3 &nbsp; Fault — realistic failure (soap-fault.xml)", sH2))
story.append(code_block("""<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:pay="http://securepay.example.com/payment">
  <soap:Body>
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
  </soap:Body>
</soap:Envelope>""", W))
story.append(P("<b>Matching note:</b> <font face='Courier'>AuthHeader</font> is declared as <font face='Courier'>soap:header</font> in the binding, so it appears in <font face='Courier'>soap:Header</font> (not in the Body). The fault <font face='Courier'>detail</font> carries the typed <font face='Courier'>PaymentFault</font> element exactly as defined in <font face='Courier'>types</font> — not a plain string.", ParagraphStyle("small", parent=sBody, fontSize=7)))

# 4 HTTP binding
story.append(Paragraph("4 &nbsp; HTTP binding — POST that carries the request (Task 4)", sH1))
story.append(P("The WSDL declares <font face='Courier'>soap:binding style='document' transport='http://schemas.xmlsoap.org/soap/http'</font> (SOAP over HTTP). The consumer therefore sends one <b>HTTP POST</b> to the service/port endpoint:", sBody))
story.append(code_block("""POST /soap/PaymentGateway HTTP/1.1
Host: api.securepay.example.com
Content-Type: text/xml; charset=utf-8
Content-Length: 892
SOAPAction: "http://securepay.example.com/payment/charge"
Connection: keep-alive

<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope ...> ... as in soap-request.xml ... </soap:Envelope>""", W))
story.append(P("<b>Key:</b> <font face='Courier'>SOAPAction</font> is taken verbatim from <font face='Courier'>binding/operation/soap:operation/@soapAction</font> in partner.wsdl. <font face='Courier'>Content-Type: text/xml; charset=utf-8</font> is SOAP 1.1 (SOAP 1.2 would be <font face='Courier'>application/soap+xml</font>). Endpoint is <font face='Courier'>service/port/soap:address/@location</font>. Success: <font face='Courier'>200 OK</font> + SOAP envelope; Fault: <font face='Courier'>500 Internal Server Error</font> + <font face='Courier'>soap:Fault</font>.", sBody))

# 5 Discovery
story.append(Paragraph("5 &nbsp; Discovery — modern form (Task 5)", sH1))
story.append(P("<b>No live UDDI server is run</b> (per brief). Discovery is design-time in two equivalent modern forms:", sBody))
story.append(P("<b>(a) Direct URL (contract-first download):</b> the gateway publishes its WSDL at a stable URL that CampusEats binds to at build time:", sBullet))
story.append(code_block("WSDL URL:  https://api.securepay.example.com/soap/PaymentGateway?wsdl\nEndpoint:  https://api.securepay.example.com/soap/PaymentGateway", W))
story.append(P("<b>(b) Catalogue / registry lookup (tModel-style pointer):</b> in production CampusEats does not hard-code the WSDL. An internal <b>Service Catalogue</b> (e.g. Backstage / API gateway registry / WSO2 Governance Registry) holds one record that points to that WSDL as a <font face='Courier'>tModel</font>. The developer searches the catalogue for 'SecurePay' and receives the WSDL location plus the <font face='Courier'>SOAPAction</font>. This satisfies the 'modern UDDI' requirement without running a UDDI node.", sBody))
story.append(Paragraph("One-record catalogue / registry entry (JSON — tModel style)", sH2))
story.append(code_block("""{
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
}""", W))
story.append(P("This single record lets CampusEats discover: <b>who</b> (business), <b>what</b> (service + operation <font face='Courier'>charge</font>), <b>where</b> (endpoint), and <b>how</b> (WSDL / tModel). The WSDL is the contract bound at compile time.", sBody))

# 6 Fault mapping
story.append(Paragraph("6 &nbsp; Fault mapping — partner vocabulary does not leak (Task 6)", sH1))
story.append(P("CampusEats' Assignment 2 contract (<font face='Courier'>schema.sql</font> — <font face='Courier'>orders.status = PENDING_PAYMENT | PAID | … | CANCELLED</font>, <font face='Courier'>payments.status = CREATED | PAID | FAILED</font>) promises a <b>single student-facing error</b> for checkout. The SOAP partner's fine-grained fault is <b>translated at the Payment Service boundary</b>:", sBody))
story.append(styled_table(
    ["SecurePay PaymentFault.code", "reason / retryable", "CampusEats A2 mapping"],
    [
        ["card_declined", "Insufficient funds, retryable=false", '400 { success:false, message:"payment declined" }<br/>payments.status=FAILED, orders.status=CANCELLED'],
        ["invalid_token", "Token expired, retryable=false", '400 { success:false, message:"payment declined" }<br/>ask student to re-enter card'],
        ["gateway_timeout", "Upstream timeout, retryable=true", '503 { success:false, message:"payment unavailable, try again" }<br/>keep PENDING_PAYMENT, idempotent retry with orderRef+nonce'],
        ["duplicate_charge", "orderRef already charged", '409 { success:false, message:"payment already processed" }<br/>return existing transactionId idempotently'],
    ],
    [42*mm, 52*mm, 76*mm]
))
story.append(Paragraph("Table 2 — Fault translation. Partner strings never reach the frontend.", sCaption))
story.append(P("<b>Rule:</b> The strings <font face='Courier'>card_declined</font>, <font face='Courier'>gateway_timeout</font>, <font face='Courier'>PaymentFault</font> and the SOAP <font face='Courier'>faultcode</font> <b>never reach the frontend</b>. The student sees only Assignment 2's vocabulary: <b>'payment declined'</b> (do not retry) or <b>'payment unavailable, try again'</b> (may retry). Internally the Payment Service logs <font face='Courier'>transactionId / gatewayRef / authCode</font> on success and <font face='Courier'>code+reason</font> on fault, then updates the local <font face='Courier'>payments</font> row — preserving the A2 invariant that every table belongs to one service and cross-service refs are plain IDs.", sBody))

# Closing
story.append(Spacer(1, 4*mm))
story.append(HRFlowable(width="100%", thickness=0.6, color=COLORS["accent"], spaceAfter=4))
story.append(Paragraph("Submission checklist", ParagraphStyle("checkH", parent=sH2, fontSize=10, textColor=COLORS["primary"])))
story.append(P("✓ <font face='Courier'>integration.pdf</font> (this document) — Tasks 1, 4, 5, 6 + TeamID / Roll / Name &nbsp;&nbsp; ✓ <font face='Courier'>partner.wsdl</font> (Task 2, six elements) &nbsp;&nbsp; ✓ <font face='Courier'>soap-request.xml</font>, <font face='Courier'>soap-response.xml</font>, <font face='Courier'>soap-fault.xml</font> (Task 3) &nbsp;&nbsp; ✓ <font face='Courier'>Assignment-3.zip</font> (one Zip with the five files, uploaded by Team Leader). All artefacts are <b>design-time only</b> — no running SOAP server or live gateway.", ParagraphStyle("check", parent=sBody, fontSize=7.5, alignment=TA_CENTER)))

doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=18*mm, bottomMargin=14*mm, title="CampusEats — SOAP Partner Integration (Assignment 3)", author="MCA-CS543-G07")
doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
