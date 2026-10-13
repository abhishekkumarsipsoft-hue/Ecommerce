# Ecommerce

An online store for bags (backpacks, laptop bags, sling bags) built with the MERN stack: MongoDB, Express, React and Node. Payments will go through Razorpay (test mode).

## What it will do
- show bags with category and price
- search and filter bags
- cart and checkout
- pay online with Razorpay
- admin can add, edit and remove bags

## Folder structure
```
Ecommerce/
├── backend/      Express + MongoDB API
│   ├── config/   db connection
│   ├── models/   mongoose schemas
│   └── routes/   product and payment routes
├── frontend/     React app (to be created)
├── docs/         notes and screenshots
├── brief.md
├── http-log.md
└── network-analysis.md
```

## Run the backend
```
cd backend
npm install
```
Make a `.env` file (copy `.env.example`) and fill `MONGO_URI` and the Razorpay keys. Then:
```
npm run seed     (adds 8 sample bags)
npm run dev
```
Check: http://localhost:5000/api/health

## Status
- [x] repo and folders
- [x] backend: products API, seed data, razorpay order + verify routes
- [ ] frontend
- [ ] auth, cart, admin panel

## Assignment files (CS543 Assignment 1)
`http-log.md`, `network-analysis.md`, `brief.md`