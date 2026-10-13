-- Ecommerce (bags store) - database schema sketch
-- CS543 Assignment 2 | Date: 11-10-26
-- Note: the real project uses MongoDB. This is a SQL sketch of the same data.
-- Rule: every table belongs to ONE service. Columns marked "ref" are plain
-- ids that point to another service's data. They are NOT foreign keys.

-- =====================================================
-- AUTH SERVICE  (Member: Abhishek,Binamra rana,Navendu)
-- =====================================================
CREATE TABLE users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(20)  NOT NULL DEFAULT 'customer',   -- customer / admin
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- CATALOGUE SERVICE  (Member: Shruti,Yatindra)
-- =====================================================
CREATE TABLE categories (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE          -- backpack, laptop bag, sling bag
);

CREATE TABLE products (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT           NOT NULL,
    name        VARCHAR(150)  NOT NULL,
    description TEXT,
    price       DECIMAL(10,2) NOT NULL,
    image_url   VARCHAR(255),
    stock       INT           NOT NULL DEFAULT 0,
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)   -- same service, so FK is fine
);

-- =====================================================
-- ORDER SERVICE  (Member: Navendu,Yatindra,Shruti)
-- =====================================================
CREATE TABLE cart_items (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,                  -- ref: Auth service (no FK)
    product_id INT NOT NULL,                  -- ref: Catalogue service (no FK)
    quantity   INT NOT NULL DEFAULT 1
);

CREATE TABLE addresses (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    user_id   INT NOT NULL,                   -- ref: Auth service (no FK)
    full_name VARCHAR(100) NOT NULL,
    phone     VARCHAR(15)  NOT NULL,
    line1     VARCHAR(255) NOT NULL,
    city      VARCHAR(50)  NOT NULL,
    state     VARCHAR(50)  NOT NULL,
    pincode   VARCHAR(10)  NOT NULL
);

CREATE TABLE orders (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT NOT NULL,                -- ref: Auth service (no FK)
    address_id   INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status       VARCHAR(20)   NOT NULL DEFAULT 'PENDING_PAYMENT',
                 -- PENDING_PAYMENT / PAID / PACKED / SHIPPED / DELIVERED / CANCELLED
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (address_id) REFERENCES addresses(id)
);

CREATE TABLE order_items (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    order_id     INT NOT NULL,
    product_id   INT NOT NULL,                -- ref: Catalogue service (no FK)
    product_name VARCHAR(150)  NOT NULL,      -- copy taken at order time
    unit_price   DECIMAL(10,2) NOT NULL,      -- copy taken at order time
    quantity     INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

-- =====================================================
-- PAYMENT SERVICE  (Member: Binamra rana, Abhishek,Yatindra)
-- =====================================================
CREATE TABLE payments (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    order_id            INT NOT NULL,         -- ref: Order service (no FK)
    razorpay_order_id   VARCHAR(50)  NOT NULL UNIQUE,
    razorpay_payment_id VARCHAR(50),
    razorpay_signature  VARCHAR(255),
    amount              DECIMAL(10,2) NOT NULL,
    status              VARCHAR(20)   NOT NULL DEFAULT 'CREATED',   -- CREATED / PAID / FAILED
    created_at          DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
);
