-- Get category wise product count in customer cart.

SELECT
    cart.cust_id,
    MAX(CASE WHEN cart.prod_id BETWEEN   1 AND 100 THEN cart.quantity ELSE 0 END) "Motherboard",
    MAX(CASE WHEN cart.prod_id BETWEEN 101 AND 200 THEN cart.quantity ELSE 0 END) "GPU",
    MAX(CASE WHEN cart.prod_id BETWEEN 201 AND 300 THEN cart.quantity ELSE 0 END) "Processor",
    MAX(CASE WHEN cart.prod_id BETWEEN 301 AND 400 THEN cart.quantity ELSE 0 END) "RAM",
    MAX(CASE WHEN cart.prod_id BETWEEN 401 AND 500 THEN cart.quantity ELSE 0 END) "PSU",
    MAX(CASE WHEN cart.prod_id BETWEEN 501 AND 600 THEN cart.quantity ELSE 0 END) "Cabinet",
    MAX(CASE WHEN cart.prod_id BETWEEN 601 AND 700 THEN cart.quantity ELSE 0 END) "Storage"
FROM cart
GROUP BY cart.cust_id
ORDER BY cart.cust_id;


-- Get date wise revenue.

SELECT
    DATE(invoice.purchase_time) as date,
    SUM(invoice.quantity) as products_sold,
    SUM(invoice.quantity * product.price) AS revenue
FROM invoice, product
WHERE invoice.prod_id = product.prod_id
GROUP BY date WITH ROLLUP;


-- Get date wise purchases by customers.

SELECT
    DATE(invoice.purchase_time) as purchase_date,
    invoice.cust_id,
    SUM(invoice.quantity) as purchase_qty
FROM invoice
GROUP BY purchase_date, invoice.cust_id WITH ROLLUP;


-- Get inventory information by product type.
SELECT 
    CASE
        WHEN prod_id BETWEEN   1 AND 100 THEN "Motherboard"
        WHEN prod_id BETWEEN 101 AND 200 THEN "GPU"
        WHEN prod_id BETWEEN 201 AND 300 THEN "Processor"
        WHEN prod_id BETWEEN 301 AND 400 THEN "RAM"
        WHEN prod_id BETWEEN 401 AND 500 THEN "PSU"
        WHEN prod_id BETWEEN 501 AND 600 THEN "Cabinet"
        WHEN prod_id BETWEEN 601 AND 700 THEN "Storage"
        ELSE "Misc"
    END AS product_type,
    SUM(quantity) as total_products,
    SUM(quantity * price) as total_value
FROM product
GROUP BY product_type WITH ROLLUP;
