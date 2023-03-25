-- Adding zero amount of products in cart
INSERT INTO cart
VALUES(123, 321, 0);
-- Adding a non-existing product in cart
INSERT INTO cart
VALUES(123, 9999, 2);

-- Adding new customer with an existing username and/or email and/or phone
INSERT INTO customer
VALUES(7331, 'gimlaw0', 'pass1234', '9876543210', 'email@somewhere.com', 'John', 'Doe', 'xyz', 'xyz', 110000);
-- Similarly for managers
INSERT INTO manager
VALUES(1234, 'New Manager', 'dosgar0', 'pass1234', '9876543210', 'email@somewhere.com');


-- Updating customer details
UPDATE customer
SET addr_loc = "H2 Boys Hostel, IIIT Delhi",
    addr_city = "New Delhi",
    phone = "9876543210"
WHERE cust_id = 1;

-- Adding new attribute for product
ALTER TABLE product
ADD GST SMALLINT UNSIGNED DEFAULT 15;

-- Select compatible processors of a particular motherboard
SELECT *
FROM product, processor
WHERE product.prod_id = processor.prod_id
AND processor.prod_id IN (
    SELECT processor.prod_id
    FROM motherboard
    INNER JOIN processor
    ON motherboard.socket_type = processor.socket_type
    AND motherboard.memory_type = processor.memory_type
    AND motherboard.prod_id = 100
);

-- View inventory information
SELECT 
    prod_id,
    prod_name,
    price AS unit_price,
    quantity,
    (price*quantity) AS stock_price,
    (
        SELECT SUM(quantity)
        FROM invoice
        WHERE product.prod_id = invoice.prod_id
    ) AS total_sale,
    (price*quantity)*100/(SELECT SUM(price*quantity) FROM product) AS inventory_share
FROM product
ORDER BY total_sale DESC;

-- View cart information
SELECT
    cust_id,
    prod_info.prod_name,
    prod_info.brand,
    prod_info.price AS unit_price,
    cart.quantity,
    (cart.quantity * prod_info.price) AS price
FROM cart
INNER JOIN (
    SELECT prod_id, prod_name, brand, price
    FROM product
) as prod_info
ON cart.prod_id = prod_info.prod_id AND cart.cust_id = 10;

-- Select customers that live in a particular PIN range and have purchased at least 1 product in last 15 days
SELECT *
FROM customer
JOIN invoice 
ON customer.cust_id = invoice.cust_id
WHERE purchase_time < DATE_SUB(NOW(), INTERVAL 15 DAY)
AND customer.addr_pin > 110045 AND customer.addr_pin < 110055;

-- Select top 100 products thare are purchased in last 10 days
SELECT product.prod_name, COUNT(*) AS num_purchases
FROM product
JOIN invoice ON product.prod_id = invoice.prod_id
WHERE invoice.purchase_time >= DATE_SUB(NOW(), INTERVAL 10 DAY)
GROUP BY product.prod_name
ORDER BY num_purchases DESC
LIMIT 100;

-- Increases prices of High end Laptop RAMs
UPDATE product
SET mrp = mrp + 200, price = mrp * discount / 100
WHERE prod_id IN (
    SELECT prod_id
    FROM ram
    WHERE memory_type = 'DDR4'
    AND device_type = 'Laptop'
    AND speed IN ('2666 MHz', '3200 MHz')
);

-- Show all products that have been sold in a given time period
SELECT
    product.prod_id,
    product.prod_name,
    customer.first_name,
    product.brand,
    product.mrp,
    TIMESTAMPDIFF(day, invoice.delivery_time, invoice.purchase_time) as delivery_time
FROM product, customer, invoice 
WHERE invoice.purchase_time >= '2023-02-01'
    AND invoice.purchase_time <= '2023-02-05'
    AND product.prod_id = invoice.prod_id
    AND customer.cust_id = invoice.cust_id
ORDER BY invoice.purchase_time DESC;

-- Show all the products delivered in PIN codes >= 110050 that had lowest delivery time
SELECT
    product.prod_id,
    product.prod_name,
    product.brand,
    customer.addr_pin,
    TIMESTAMPDIFF(day, invoice.delivery_time, invoice.purchase_time) as delivery_time
FROM product, customer, invoice
WHERE product.prod_id = invoice.prod_id
    AND customer.cust_id = invoice.cust_id
    AND customer.addr_pin >= 110050
ORDER BY delivery_time ASC;

-- Show all the products of a specific brand having more than 4 stars
SELECT
    product.prod_name,
    product.brand,
    product.model,
    product.mrp,
    review.star
FROM product, invoice, review 
WHERE product.prod_id = invoice.inv_id
    AND product.prod_id = review.prod_id
    AND review.star >= 4
    AND product.brand = 'Dell'
ORDER BY review.star DESC;

-- Show date wise daily revenue of last month
SELECT
    DATE(invoice.purchase_time) as date,
    SUM(invoice.quantity) as products_sold,
    SUM(invoice.quantity * product.price) AS revenue
FROM invoice
INNER JOIN product
ON invoice.prod_id = product.prod_id
GROUP BY date
HAVING date > DATE_SUB(NOW(), INTERVAL 30 DAY);


-- Triggers

-- Trigger to update the quantity of a product when it is added to cart
drop trigger if exists update_quantity_on_add;
DELIMITER $$
CREATE TRIGGER update_quantity_on_add
AFTER INSERT ON cart FOR EACH ROW
BEGIN
    update product
    set quantity = quantity - NEW.quantity
    where prod_id = NEW.prod_id;
END;
$$
DELIMITER ;

-- Trigger to update the quantity of a product in product table when it is removed from cart
drop trigger if exists update_quantity_on_remove;
DELIMITER $$
CREATE TRIGGER update_quantity_on_remove
AFTER DELETE ON cart FOR EACH ROW
BEGIN
    update product
    set quantity = quantity + OLD.quantity
    where prod_id = OLD.prod_id;
END;
$$
DELIMITER ;
-- select * from cart where cart.prod_id = 299; // 0
-- select product.quantity from product where product.prod_id = 299; // 2245
-- insert into cart values (1, 299, 1);
-- delete from cart where cart.prod_id = 299;

-- Trigger to update the quantity of a product when it is added to invoice (item has been brought)
drop trigger if exists update_quantity_on_invoice;
DELIMITER $$
CREATE TRIGGER update_quantity_on_invoice
AFTER INSERT ON invoice FOR EACH ROW
BEGIN
    update product
    set quantity = quantity - NEW.quantity
    where prod_id = NEW.prod_id;
END;
$$
DELIMITER ;
-- select * from invoice where invoice.prod_id = 299; // 0
-- select product.quantity from product where product.prod_id = 299; // 2245
-- insert into invoice values ('501', '2021-01-01', '1', '299', '1', '2021-02-01');
-- select * from invoice where invoice.prod_id = 299; // 1
-- select product.quantity from product where product.prod_id = 299; // 2244

-- Trigger to decrease the discount of a product using a formula which is uses the current quantity to decrease the discount accordingly when it is added to invoice
drop trigger if exists update_discount_on_invoice;
DELIMITER $$
CREATE TRIGGER update_discount_on_invoice
AFTER INSERT ON invoice FOR EACH ROW
BEGIN
    update product
    set discount = discount - (quantity * 0.1)
    where prod_id = NEW.prod_id;
END;
$$
DELIMITER ;
-- select * from invoice where invoice.prod_id = 299; // 1
-- select product.quantity from product where product.prod_id = 299; // 2244
-- select product.discount from product where product.prod_id = 299; // 10
-- insert into invoice values ('502', '2021-01-01', '1', '299', '1', '2021-02-01');
-- select * from invoice where invoice.prod_id = 299; // 2
-- select product.quantity from product where product.prod_id = 299; // 2243
-- select product.discount from product where product.prod_id = 299; // 9.9
 