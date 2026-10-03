-- reports.sql
-- Part 1 Task 3 — each query's expected output is recorded in the comment above it.

-- ---------------------------------------------------------------------------
-- (a) Order totals — total_orders=180, total_revenue=99860.20, avg_order_value=554.78
-- ---------------------------------------------------------------------------
SELECT
    COUNT(*) AS total_orders,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_revenue,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)) / COUNT(*), 2) AS avg_order_value
FROM orders o
JOIN products p ON o.product_id = p.product_id;

-- ---------------------------------------------------------------------------
-- (b) COUNT(*) vs COUNT(rating) — (180, 165, 15)
-- ---------------------------------------------------------------------------
SELECT
    COUNT(*) AS cnt_star,
    COUNT(rating) AS cnt_rating,
    COUNT(*) - COUNT(rating) AS difference
FROM orders;

-- ---------------------------------------------------------------------------
-- (c1) LEFT JOIN — customers with zero orders → C045 Vihaan
-- ---------------------------------------------------------------------------
SELECT c.customer_id, c.name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) = 0;

-- ---------------------------------------------------------------------------
-- (c2) NOT IN confirmation — same row C045 Vihaan
-- ---------------------------------------------------------------------------
SELECT customer_id, name
FROM customers
WHERE customer_id NOT IN (SELECT DISTINCT customer_id FROM orders);

-- ---------------------------------------------------------------------------
-- (d) GROUP BY city + HAVING return_rate_pct > 20
--     Jaipur (19, 8, 42.1), Lucknow (49, 15, 30.6), Bangalore (33, 8, 24.2)
-- ---------------------------------------------------------------------------
SELECT
    c.city,
    COUNT(*) AS total_orders,
    SUM(o.returned) AS returned_orders,
    ROUND(100.0 * SUM(o.returned) / COUNT(*), 1) AS return_rate_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.city
HAVING ROUND(100.0 * SUM(o.returned) / COUNT(*), 1) > 20
ORDER BY return_rate_pct DESC;

-- ---------------------------------------------------------------------------
-- (e) Top 5 by total_spend — tie-break on customer_id ASC for stable ranking
--     C043 12920.00, C026 8371.60, C008 4564.60, C011 4111.00, C042 3785.00
-- ---------------------------------------------------------------------------
SELECT
    c.customer_id,
    c.name,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 5;

-- ranks 3–5 via OFFSET (same order as above)
SELECT
    c.customer_id,
    c.name,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 3 OFFSET 2;

-- ---------------------------------------------------------------------------
-- (f) Category revenue — Haircare 44956.10, Skincare 27346.00,
--     Babycare 16805.00, PersonalCare 10753.10
-- ---------------------------------------------------------------------------
SELECT
    p.category,
    COUNT(*) AS order_count,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS category_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY p.category
ORDER BY category_revenue DESC;

-- ---------------------------------------------------------------------------
-- (g) LIKE 'A%' — exactly 10 customers
-- ---------------------------------------------------------------------------
SELECT customer_id, name
FROM customers
WHERE name LIKE 'A%';

-- ---------------------------------------------------------------------------
-- (h) DISTINCT acquisition_source — Ad, Organic, Referral, Social
-- ---------------------------------------------------------------------------
SELECT DISTINCT acquisition_source
FROM customers
ORDER BY acquisition_source;

-- ---------------------------------------------------------------------------
-- (i) ALTER + CASE loyalty_tier — Gold 28, Silver 17
-- ---------------------------------------------------------------------------
ALTER TABLE customers ADD COLUMN loyalty_tier VARCHAR(10);

UPDATE customers
SET loyalty_tier = CASE WHEN city_tier = 1 THEN 'Gold' ELSE 'Silver' END;

SELECT loyalty_tier, COUNT(*) AS n
FROM customers
GROUP BY loyalty_tier;
