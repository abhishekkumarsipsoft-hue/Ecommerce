# Ecommerce Brief

## What
Ecommerce is a web store where college students can buy bags like backpacks, laptop bags and sling bags. A student opens the site, looks at the bags, picks what he likes, pays online and can check his order later. The shop owner uses a separate admin side to add new bags and to change the status of orders (like packed, shipped, delivered).

I am building it with the MERN stack: MongoDB for data, Express and Node for the backend API, React for the website. Payments go through Razorpay.

## Who uses it
- **Student (customer):** searches bags, buys them, tracks orders.
- **Shop owner (admin):** manages the bags list and the orders.
- **Razorpay:** outside payment service. My backend only calls its API, I never touch the card details.

## Nouns (things / services)
- **User:** name, email, password, role (customer or admin)
- **Product:** one bag, with name, price, category, image, stock
- **Category:** group of bags, e.g. backpack, laptop bag, sling bag
- **Cart:** the bags a user has picked but not bought yet
- **Order:** a placed purchase with items, total amount and status
- **Payment:** the Razorpay record for an order (order id, payment id, signature)
- **Address:** where the order should be delivered

Services in the backend: Auth service, Product service, Order service, Payment service (talks to Razorpay).

## Verbs (actions / tasks)
- **User:** register, login, logout
- **Product:** list, search, filter by category, view one product
- **Cart:** add item, remove item, change quantity
- **Order:** place order, view my orders, cancel order
- **Payment:** create Razorpay order, verify payment
- **Admin:** add product, edit product, delete product, update order status

## Main flow in one line
Student finds a bag -> adds it to cart -> places order -> backend creates a Razorpay order -> student pays -> backend verifies the payment signature -> order is marked paid.