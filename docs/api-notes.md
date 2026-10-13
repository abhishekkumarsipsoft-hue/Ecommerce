# API notes (planned)

| Method | URL | Use |
|--------|-----|-----|
| GET | /api/health | check server is up |
| GET | /api/products | list products (?category=, ?search=) |
| GET | /api/products/:id | one product |
| POST | /api/products | add product (admin) |
| POST | /api/payment/order | create Razorpay order |
| POST | /api/payment/verify | verify payment signature |
