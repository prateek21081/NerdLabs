DROP DATABASE IF EXISTS nerdlabs;
CREATE DATABASE nerdlabs;
USE nerdlabs;

CREATE TABLE manager (
    man_id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,
    man_name VARCHAR(30) NOT NULL,
    username VARCHAR(20) NOT NULL,
    password VARCHAR(20) NOT NULL,
    phone VARCHAR(10) NOT NULL,
    email VARCHAR(50) NOT NULL,
    PRIMARY KEY (man_id),
    UNIQUE (username),
    UNIQUE (phone),
    UNIQUE (email),
    INDEX (man_id, username)
);

CREATE TABLE customer (
    cust_id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,
    username VARCHAR(20) NOT NULL,
    password VARCHAR(20) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(50) NOT NULL,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    addr_loc VARCHAR(50) NOT NULL,
    addr_city VARCHAR(30) NOT NULL,
    addr_pin VARCHAR(8) NOT NULL,
    PRIMARY KEY (cust_id),
    UNIQUE (username),
    UNIQUE (phone),
    UNIQUE (email),
    INDEX (cust_id, username)
);

CREATE TABLE product (
    prod_id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,
    prod_name VARCHAR(50) NOT NULL,
    quantity INTEGER UNSIGNED NOT NULL,
    brand VARCHAR(20) NOT NULL,
    mrp INTEGER UNSIGNED NOT NULL,
    discount INTEGER UNSIGNED NOT NULL,
    price INTEGER UNSIGNED NOT NULL, 
    model VARCHAR(20) NOT NULL,
    image BLOB DEFAULT NULL,
    PRIMARY KEY (prod_id),
    CHECK (quantity >= 0),
    CHECK (mrp >= 0),
    CHECK (discount >= 0 AND discount <= 100),
    INDEX (prod_id)
);

CREATE TABLE invoice (
    inv_id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,
    purchase_time DATETIME NOT NULL,
    cust_id INTEGER UNSIGNED NOT NULL,
    prod_id INTEGER UNSIGNED NOT NULL,
    quantity INTEGER UNSIGNED NOT NULL,
    delivery_time DATETIME,
    PRIMARY KEY (inv_id),
    FOREIGN KEY (cust_id) REFERENCES customer (cust_id),
    FOREIGN KEY (prod_id) REFERENCES product (prod_id),
    CHECK (quantity > 0),
    INDEX (inv_id)
);

CREATE TABLE cart (
    cust_id INTEGER UNSIGNED NOT NULL,
    prod_id INTEGER UNSIGNED NOT NULL,
    quantity INTEGER UNSIGNED NOT NULL,
    PRIMARY KEY (cust_id, prod_id),
    FOREIGN KEY (cust_id) REFERENCES customer (cust_id),
    FOREIGN KEY (prod_id) REFERENCES product (prod_id),
    CHECK (quantity != 0),
    INDEX (cust_id, prod_id)
);

CREATE TABLE review (
    cust_id INTEGER UNSIGNED NOT NULL,
    prod_id INTEGER UNSIGNED NOT NULL,
    star INTEGER UNSIGNED NOT NULL,
    review VARCHAR(300) NULL,
    PRIMARY KEY (cust_id, prod_id),
    FOREIGN KEY (cust_id) REFERENCES customer (cust_id),
    FOREIGN KEY (prod_id) REFERENCES product (prod_id),
    CHECK (star >=0 AND star <= 5),
    INDEX (cust_id, prod_id)
);

CREATE TABLE motherboard (
    prod_id INTEGER UNSIGNED NOT NULL,
    memory_type VARCHAR(20) NOT NULL,
    processor_type VARCHAR(20) NOT NULL,
    memory_capacity INTEGER UNSIGNED NOT NULL,
    chipset_type VARCHAR(20) NOT NULL,
    io_ports INTEGER UNSIGNED NOT NULL,
    socket_type VARCHAR(20) NOT NULL,
    PRIMARY KEY (prod_id),
    FOREIGN KEY (prod_id) REFERENCES product (prod_id) ON DELETE CASCADE,
    INDEX (prod_id)
);

CREATE TABLE gpu (
    prod_id INTEGER UNSIGNED NOT NULL,
    memory_type VARCHAR(20) NOT NULL,
    memory_capacity INTEGER UNSIGNED NOT NULL,
    memory_clock INTEGER UNSIGNED NOT NULL,
    processor VARCHAR(20) NOT NULL,
    interface VARCHAR(20) NOT NULL,
    PRIMARY KEY (prod_id),
    FOREIGN KEY (prod_id) REFERENCES product (prod_id) ON DELETE CASCADE,
    INDEX (prod_id)
);

CREATE TABLE processor (
    prod_id INTEGER UNSIGNED NOT NULL,
    core_count INTEGER UNSIGNED NOT NULL,
    thread_count INTEGER UNSIGNED NOT NULL,
    memory_type VARCHAR(20) NOT NULL,
    tdp INTEGER UNSIGNED NOT NULL,
    socket_type VARCHAR(20) NOT NULL,
    PRIMARY KEY (prod_id),
    FOREIGN KEY (prod_id) REFERENCES product (prod_id) ON DELETE CASCADE,
    INDEX (prod_id)
);

CREATE TABLE storage (
    prod_id INTEGER UNSIGNED NOT NULL,
    capacity INTEGER UNSIGNED NOT NULL,
    connector_type VARCHAR(20) NOT NULL,
    type VARCHAR(20) NOT NULL,
    form_factor VARCHAR(20) NOT NULL,
    PRIMARY KEY (prod_id),
    FOREIGN KEY (prod_id) REFERENCES product (prod_id) ON DELETE CASCADE,
    INDEX (prod_id)
);

CREATE TABLE ram (
    prod_id INTEGER UNSIGNED NOT NULL,
    memory_type VARCHAR(20) NOT NULL,
    capacity INTEGER UNSIGNED NOT NULL,
    speed VARCHAR(20) NOT NULL,
    device_type VARCHAR(20) NOT NULL,
    PRIMARY KEY (prod_id),
    FOREIGN KEY (prod_id) REFERENCES product (prod_id) ON DELETE CASCADE,
    INDEX (prod_id)
);

CREATE TABLE psu (
    prod_id INTEGER UNSIGNED NOT NULL,
    wattage INTEGER UNSIGNED NOT NULL,
    form_factor VARCHAR(20) NOT NULL,
    certification VARCHAR(20) NULL,
    PRIMARY KEY (prod_id),
    FOREIGN KEY (prod_id) REFERENCES product (prod_id) ON DELETE CASCADE,
    INDEX (prod_id)
);

CREATE TABLE cabinet (
    prod_id INTEGER UNSIGNED NOT NULL,
    colour VARCHAR(20) NOT NULL, 
    form_factor VARCHAR(20) NOT NULL,
    material VARCHAR(30) NOT NULL,
    PRIMARY KEY (prod_id),
    FOREIGN KEY (prod_id) REFERENCES product (prod_id) ON DELETE CASCADE,
    INDEX (prod_id)
);
