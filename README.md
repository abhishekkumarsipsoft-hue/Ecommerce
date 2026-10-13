# CampusEats

Online bags store for college students, built with the MERN stack (MongoDB, Express, React, Node) with Razorpay for payments.

> Naam "CampusEats" hai kyunki pehle idea canteen ka tha, ab ye campus ke liye bags bechta hai. (Naam change kar sakte hain baad me.)

## What it will do
- show bags with category and price
- search and filter bags
- cart and checkout
- pay online with Razorpay (test mode)
- admin can add / edit / remove bags

## Folder structure
```
campuseats/
├── backend/      Express + MongoDB API
│   ├── config/   db connection
│   ├── models/   mongoose schemas
│   └── routes/   product + payment routes
├── frontend/     React app (to be created with Vite)
├── docs/         notes and API list
├── brief.md
├── http-log.md
└── network-analysis.md
```

## Run the backend
```
cd backend
npm install
copy .env.example .env     (then fill values)
npm run dev
```
Check: http://localhost:5000/api/health

## Status
- [x] repo + folders
- [x] backend skeleton (products, razorpay order + verify)
- [ ] frontend
- [ ] auth, cart, admin panel

## Assignment files
`http-log.md`, `network-analysis.md`, `brief.md` are for CS543 Assignment 1.
