'''
Manager:
    dosgar0
    53LLHBxrP9
'''

from flask import (
    Flask,
    request,
    render_template,
    session,
    redirect,
    url_for,
    jsonify,
    make_response
)
import mysql.connector
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = b's3cr3t_k3y'
cnx = mysql.connector.connect(
    host = "localhost",
    database = "nerdlabs",
    user = "admin",
    password = "pass"
)
cnx.autocommit = True
cur = cnx.cursor()

def admin_token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        try:
            token = request.cookies['ajwt']
            data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
            man_id = data['man_id']
        except:
            return make_response(jsonify({
                'message': 'Admin Token invalid or missing!'
            }), 401)
        return func(man_id, *args, **kwargs)
    return decorated

def customer_token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        try:
            token = request.cookies['jwt']
            data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
            cust_id = data['cust_id']
        except:
            return make_response(jsonify({
                'message': 'Token invalid or missing. Login or Register to continue!'
            }), 401)
        return func(cust_id, *args, **kwargs)
    return decorated

def prod_category_by_id(prod_id):
    prod_type = ['motherboard', 'gpu', 'processor', 'ram', 'storage', 'psu', 'cabinet']
    category = prod_type[int(prod_id)//100]
    return category

@app.route('/userid')
@customer_token_required
def get_custid(cust_id):
    return make_response(jsonify({'cust_id': cust_id}), 200)

@app.route('/', methods=['GET'])
def root():
    cur.execute('SELECT * FROM product WHERE product.prod_id >= 40 limit 10')
    keys = cur.column_names
    values = cur.fetchall()
    res = list()
    for val in values:
        res.append(dict(zip(keys, val)))
    return render_template('homepage.html', context=res)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        cur.execute("SELECT cust_id, password FROM customer WHERE username = %s", [username])
        user = cur.fetchone()
        if user is None:
            error = "Incorrect username."
        elif not password == user[1]:
            error = "Incorrect password."
        if error:
            return make_response(error, 401)
        else:
            token = jwt.encode({
                'cust_id': user[0],
                'expiry': str(datetime.utcnow()) + str(timedelta(minutes=30))
            }, app.secret_key, algorithm="HS256")
            resp = redirect('/')
            resp.set_cookie('jwt', token)
            return resp;
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    res = {
        "message": None,
    }
    if request.method == 'POST':
        try:
            cnx.start_transaction()
            cur.execute(f'SELECT * FROM customer LIMIT 1')
            cur.fetchone()
            values = [request.form[attr] for attr in cur.column_names]
            print(values)
            cur.execute('INSERT INTO customer VALUES (' + ','.join(['%s']*len(values)) + ')', values)
            cnx.commit()
        except mysql.connector.Error as err:
            res['message'] = err
    cur.execute(f'SELECT * FROM customer LIMIT 1')
    cur.fetchone()
    res['fields'] = cur.column_names
    return render_template('auth/register.html', context=res)

@app.route('/data', methods=['GET', 'POST'])
@admin_token_required
def get_data(man_id):
    if request.method == 'POST':
        try:
            cur.execute(f"SELECT * FROM {request.form['data']}")
            keys = cur.column_names
            values = cur.fetchall()
            res = {
                "message": None,
                "title": request.form['data'],
                "attributes": keys,
                "records": values
            }
        except mysql.connector.Error as err:
            res = {
                "message": err
            }
    else:
        res = None
    return render_template('data.html', context=res)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        try:
            cur.execute(f'SELECT * FROM product where prod_name like "%{request.form["keyword"]}%"')
            keys = cur.column_names
            values = cur.fetchall()
            res = {
                "message": None,
                "attributes": keys,
                "records": values
            }
        except mysql.connector.Error as err:
            res = {
                "message": err
            }
    else:
        res = None
    return render_template('product/search.html', context=res)

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        cur.execute("SELECT man_id, password FROM manager WHERE username = %s", [username])
        user = cur.fetchone()
        if user is None:
            error = "Incorrect username."
        elif not password == user[1]:
            error = "Incorrect password."
        if error:
            return make_response(error, 401)
        else:
            token = jwt.encode({
                'man_id': user[0],
                'expiry': str(datetime.utcnow()) + str(timedelta(minutes=30))
            }, app.secret_key, algorithm="HS256")
            resp = redirect('/')
            resp.set_cookie('ajwt', token)
            return resp;
    return render_template('auth/login.html')

@app.route('/admin/add/<category>', methods=['GET', 'POST'])
@admin_token_required
def admin_addproduct(man_id, category):
    res = {
        "message": None,
    }
    if request.method == 'POST':
        try:
            cnx.start_transaction()
            cur.execute(f'SELECT * FROM product LIMIT 1')
            cur.fetchone()
            values = [request.form[attr] for attr in cur.column_names]
            cur.execute('INSERT INTO product VALUES (' + ','.join(['%s']*len(values)) + ')', values)
            cur.execute(f'SELECT * FROM {category} LIMIT 1')
            cur.fetchone()
            values = [request.form[attr] for attr in cur.column_names]
            cur.execute(f'INSERT INTO {category} VALUES (' + ','.join(['%s']*len(values)) + ')', values)
            cnx.commit()
        except mysql.connector.Error as err:
            res['message'] = err
    cur.execute(f'SELECT * FROM product, {category} LIMIT 1')
    cur.fetchone()
    res['fields'] = cur.column_names
    return render_template('admin/addproduct.html', context=res)

@app.route('/admin/update/<prod_id>', methods=['GET', 'POST'])
@admin_token_required
def admin_updateproduct(man_id, prod_id):
    res = {
        "message": None,
    }
    category = prod_category_by_id(prod_id)
    if request.method == 'POST':
        try:
            cnx.start_transaction()
            cur.execute("SET FOREIGN_KEY_CHECKS=0")
            cur.execute(f"DELETE FROM {category} where prod_id=%s", [prod_id])
            cur.execute(f"DELETE FROM product where prod_id=%s", [prod_id])
            cur.execute("DELETE FROM review where prod_id=%s", [prod_id])
            cur.execute("SET FOREIGN_KEY_CHECKS=1")
            cur.execute(f'SELECT * FROM product LIMIT 1')
            cur.fetchone()
            values = [request.form[attr] for attr in cur.column_names]
            cur.execute('INSERT INTO product VALUES (' + ','.join(['%s']*len(values)) + ')', values)
            cur.execute(f'SELECT * FROM {category} LIMIT 1')
            cur.fetchone()
            values = [request.form[attr] for attr in cur.column_names]
            cur.execute(f'INSERT INTO {category} VALUES (' + ','.join(['%s']*len(values)) + ')', values)
            cnx.commit()
        except mysql.connector.Error as err:
            res['message'] = err
    cur.execute(f'SELECT * FROM product p, {category} c WHERE c.prod_id = p.prod_id and p.prod_id=%s', [prod_id])
    res['data'] = dict(zip(cur.column_names, cur.fetchone()))
    return render_template('admin/updateproduct.html', context=res)

@app.route('/admin/delete', methods=['GET', 'POST'])
@admin_token_required
def admin_deleteproduct(man_id):
    res = {
        "message": None,
    }
    if request.method == 'POST':
        prod_id = request.form['prod_id']
        category = prod_category_by_id(prod_id)
        try:
            cnx.start_transaction()
            cur.execute("SET FOREIGN_KEY_CHECKS=0")
            cur.execute(f"DELETE FROM {category} where prod_id=%s", [prod_id])
            cur.execute(f"DELETE FROM product where prod_id=%s", [prod_id])
            cur.execute("DELETE FROM review where prod_id=%s", [prod_id])
            cur.execute("SET FOREIGN_KEY_CHECKS=1")
            cnx.commit()
        except mysql.connector.Error as err:
            res['message'] = err
    return render_template('admin/deleteproduct.html', context=res)        

@app.route('/cart', methods=['GET', 'POST'])
@customer_token_required
def view_cart(cust_id):
    if request.method == 'POST':
        cur.execute('drop trigger if exists update_quantity_on_remove;')
        cur.execute('''CREATE TRIGGER update_quantity_on_remove
                        AFTER DELETE ON cart FOR EACH ROW
                        BEGIN
                            update product
                            set quantity = quantity + OLD.quantity
                            where prod_id = OLD.prod_id;
                        END;''')
        cur.execute('DELETE FROM cart WHERE cart.cust_id = %s AND cart.prod_id = %s', [cust_id, request.form['prod_id']])
    cur.execute('SELECT * FROM cart WHERE cart.cust_id = %s', [cust_id])
    keys = cur.column_names
    values = cur.fetchall()
    cart = list()
    for val in values:
        cart.append(dict(zip(keys, val)))
    for item in cart:
        cur.execute('SELECT price FROM product WHERE product.prod_id = %s', [item['prod_id']])
        item['price'] = cur.fetchone()[0]
    return render_template('customer/cart.html', context=cart)

@app.route('/invoice', methods=['GET', 'POST'])
@customer_token_required
def viewcart(cust_id):
    # Query the database for items in the cart for the customer
    try:
        cnx.start_transaction()
        cur.execute('SELECT * FROM cart WHERE cart.cust_id = %s', [cust_id])
        keys = cur.column_names
        values = cur.fetchall()
        if len(values) == 0:
            cnx.rollback()
            return "Cart empty!"
        amount = 0
        cart = list()
        for val in values:
            cart.append(dict(zip(keys, val)))
        for item in cart:
            cur.execute('SELECT price FROM product WHERE product.prod_id = %s', [item['prod_id']])
            item['price'] = cur.fetchone()[0]
            amount += int(item['price']) * int(item['quantity'])

        # Add invoice information in database
        cur.execute('SELECT MAX(inv_id) FROM invoice')
        inv_id = int(cur.fetchone()[0]) + 1
        for item in cart:
            cur.execute('INSERT INTO invoice VALUES (%s, now(), %s, %s, %s, now())', [inv_id, cust_id, item['prod_id'], item['quantity']])
            inv_id = inv_id + 1
 
        # for customer add customer details to the invoice
        cur.execute('SELECT * FROM customer WHERE customer.cust_id = %s', [cust_id])
        keys = cur.column_names
        values = cur.fetchone()
        customer = dict(zip(keys, values))
        cur.execute('DELETE FROM cart WHERE cust_id=%s', [cust_id])
        cnx.commit()
    except mysql.connector.Error as err:
        cnx.rollback()
        return err
    return render_template('customer/invoice.html', date=datetime.now(), cart=cart, customer=customer, total=amount)


@app.route('/data/query1', methods=['GET', 'POST'])
@customer_token_required
def query1(cust_id):
    if request.method == 'POST':
        # Execute query 1
        cur.execute('SELECT cart.cust_id, \
        MAX(CASE WHEN cart.prod_id BETWEEN 1 AND 100 THEN cart.quantity ELSE 0 END) AS Motherboard, \
        MAX(CASE WHEN cart.prod_id BETWEEN 101 AND 200 THEN cart.quantity ELSE 0 END) AS GPU, \
        MAX(CASE WHEN cart.prod_id BETWEEN 201 AND 300 THEN cart.quantity ELSE 0 END) AS Processor, \
        MAX(CASE WHEN cart.prod_id BETWEEN 301 AND 400 THEN cart.quantity ELSE 0 END) AS RAM, \
        MAX(CASE WHEN cart.prod_id BETWEEN 401 AND 500 THEN cart.quantity ELSE 0 END) AS PSU, \
        MAX(CASE WHEN cart.prod_id BETWEEN 501 AND 600 THEN cart.quantity ELSE 0 END) AS Cabinet, \
        MAX(CASE WHEN cart.prod_id BETWEEN 601 AND 700 THEN cart.quantity ELSE 0 END) AS Storage \
        FROM cart \
        WHERE cart.cust_id = %s \
        GROUP BY cart.cust_id \
        ORDER BY cart.cust_id', (cust_id,))
        keys = cur.column_names
        values = cur.fetchall()
        res = list()
        for val in values:
            res.append(dict(zip(keys, val)))
        # print(res)
        return render_template('data/query1.html', context=res)

@app.route('/data/query2', methods=['GET', 'POST'])
@admin_token_required
def query2(man_id):
    if request.method == 'POST':
        # Execute query 2
        cur.execute('SELECT DATE(invoice.purchase_time) as date, \
            SUM(invoice.quantity) as products_sold, \
            SUM(invoice.quantity * product.price) AS revenue \
            FROM invoice, product \
            WHERE invoice.prod_id = product.prod_id \
            GROUP BY date WITH ROLLUP')
        keys = cur.column_names
        values = cur.fetchall()
        res = list()
        for val in values:
            res.append(dict(zip(keys, val)))
        # print(res)
        return render_template('data/query2.html', context=res)

@app.route('/data/query3', methods=['GET', 'POST'])
@admin_token_required
def query3(man_id):
    if request.method == 'POST':
        cur.execute('SELECT COALESCE(DATE(invoice.purchase_time), "2023-02-10") as purchase_date, \
        COALESCE(invoice.cust_id, "2") as cust_id, \
        COALESCE(SUM(invoice.quantity), 0) as purchase_qty \
        FROM invoice \
        GROUP BY purchase_date, cust_id WITH ROLLUP;')
        keys = cur.column_names
        values = cur.fetchall()
        res = list()
        for val in values:
            res.append(dict(zip(keys, val)))
        # print(res)
        return render_template('data/query3.html', context=res)
    
@app.route('/data/query4', methods=['GET', 'POST'])
@admin_token_required
def query4(man_id):
    if request.method == 'POST':
        cur.execute('SELECT \
            CASE \
                WHEN prod_id BETWEEN   1 AND 100 THEN "Motherboard" \
                WHEN prod_id BETWEEN 101 AND 200 THEN "GPU" \
                WHEN prod_id BETWEEN 201 AND 300 THEN "Processor" \
                WHEN prod_id BETWEEN 301 AND 400 THEN "RAM" \
                WHEN prod_id BETWEEN 401 AND 500 THEN "PSU" \
                WHEN prod_id BETWEEN 501 AND 600 THEN "Cabinet" \
                WHEN prod_id BETWEEN 601 AND 700 THEN "Storage" \
            ELSE "Misc" \
            END AS product_type, \
            SUM(quantity) as total_products, \
            SUM(quantity * price) as total_value \
            FROM product \
            GROUP BY product_type WITH ROLLUP;')
        
        keys = cur.column_names
        values = cur.fetchall()
        res = list()
        for val in values:
            res.append(dict(zip(keys, val)))
        # print(res)
        return render_template('data/query4.html', context=res)

# <---------------------------------------PRODUCTS-------------------------------------------------------------->

# Searching for a product using PID
@app.route('/product/id/<prod_id>', methods=['GET'])
def get_product(prod_id):
    if request.method == 'GET':
        category = prod_category_by_id(prod_id)
        res = dict()
        try:
            cnx.start_transaction()
            cur.execute(f'SELECT * FROM product WHERE product.prod_id = %s', [prod_id])
            keys = cur.column_names
            values = cur.fetchone()
            res['product'] = dict(zip(keys, values))
            cur.execute(f'SELECT * FROM {category} WHERE {category}.prod_id = %s', [prod_id])
            keys = cur.column_names
            values = cur.fetchone()
            res['meta'] = dict(zip(keys, values))
            cur.execute('SELECT * FROM review WHERE review.prod_id = %s', [prod_id])
            keys = cur.column_names
            values = cur.fetchall()
            cnx.commit()
        except mysql.connector.Error as err:
            cnx.rollback()
            res['message'] = err
        review = list()
        for val in values:
            review.append(dict(zip(keys, val)))
        res['review'] = review
        res['category'] = category
        return render_template('product/product.html', context=res)
    
@app.route('/product/id/<prod_id>', methods=['POST'])
@customer_token_required
def add_product_post(cust_id, prod_id):
    if request.method == 'POST':
        quantity = request.form['quantity']
        cur.execute('INSERT INTO cart VALUES (%s, %s, %s)', [cust_id, prod_id, quantity])
        cur.execute('SELECT * FROM cart WHERE cart.cust_id = %s', [cust_id])
        # get product price
        keys = cur.column_names
        values = cur.fetchall()
        cart = list()
        for val in values:
            cart.append(dict(zip(keys, val)))
        for item in cart:
            cur.execute('SELECT price FROM product WHERE product.prod_id = %s', [item['prod_id']])
            item['price'] = cur.fetchone()[0]
        # print(cust_id, prod_id, quantity)
        
        # Add trigger to update quantity on adding to cart
        cur.execute('DROP TRIGGER IF EXISTS update_quantity_on_add;')
        cur.execute('''CREATE TRIGGER update_quantity_on_add \
                        AFTER INSERT ON cart \
                        FOR EACH ROW \
                        BEGIN \
                            UPDATE product \
                            SET quantity = quantity - NEW.quantity \
                            WHERE prod_id = NEW.prod_id; \
                        END;''')

        return redirect(url_for('view_cart', cust_id=cust_id))


# Searching for a product using product brand
@app.route('/product/brand/<brand>')
def get_product_brand(brand):
    cur.execute("SELECT * FROM product WHERE brand = %s", [brand])
    keys = cur.column_names
    records = cur.fetchall()
    res = {
        "brand": brand,
        "attributes": keys,
        "products": records,
    }
    return render_template('product/brand.html', context=res)

# Get all products in a particular category
@app.route('/product/category/<category>')
def get_product_category(category):
    cur.execute(f"SELECT * FROM product, {category} WHERE product.prod_id={category}.prod_id")
    keys = cur.column_names
    records = cur.fetchall()
    res = {
        "category": category,
        "attributes": keys,
        "products": records
    }
    return render_template('product/category.html', context=res)

# <---------------------------------------CUSTOMER-------------------------------------------------------------->

# Get all customers in the database
@app.route('/customer')
def get_customers():
    cur.execute("SELECT * FROM customer")
    keys = cur.column_names
    records = cur.fetchall()
    res = {
        "attributes": keys,
        "customers": records
    }
    return render_template('customer/customer.html', context=res)

# Get customer details using customer ID
@app.route('/customer/id/<cust_id>')
def get_customer(cust_id):
    cur.execute("SELECT * FROM customer WHERE cust_id = %s", [cust_id])
    keys = cur.column_names
    records = cur.fetchall()
    res = {
        "attributes": keys,
        "customers": records
    }
    return render_template('customer/customer.html', context=res)

# Get customer details using customer username
@app.route('/customer/username/<username>')
def get_customer_username(username):
    cur.execute("SELECT * FROM customer WHERE username = %s", [username])
    keys = cur.column_names
    records = cur.fetchall()
    res = {
        "attributes": keys,
        "customers": records
    }
    return render_template('customer/customer.html', context=res)

# Get all customers in a particular pincode
@app.route('/customer/pincode/<addr_pin>')
def get_customer_pincode(addr_pin):
    cur.execute("SELECT * FROM customer WHERE addr_pin = %s", [addr_pin])
    keys = cur.column_names
    records = cur.fetchall()
    res = {
        "attributes": keys,
        "customers": records
    }
    return render_template('customer/customer.html', context=res)

# Get all customers in a particular city
@app.route('/customer/city/<city>')
def get_customer_city(city):
    cur.execute("SELECT * FROM customer WHERE addr_city = %s", [city])
    keys = cur.column_names
    records = cur.fetchall()
    res = {
        "attributes": keys,
        "customers": records
    }
    return render_template('customer/customer.html', context=res)

if __name__ == '__main__':
    app.run()
