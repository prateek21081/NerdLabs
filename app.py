from flask import (
    Flask,
    request,
    render_template,
    session,
    redirect,
    url_for
)
import mysql.connector
import json

app = Flask(__name__)
app.secret_key = b's3cr3t_k3y'
db = mysql.connector.connect(
    host = "localhost",
    database = "nerdlabs",
    user = "admin",
    password = "pass"
)
db.autocommit = True
cur = db.cursor()

@app.route('/')
def root():
    return "Welcome to NerdLabs!"

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
            return error
        else:
            session.clear()
            session['user_id'] = user[0]
            return f'username: {username}, password: {password}'
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        if not password:
            error = 'Password is required.'
        if not username:
            error = 'Username is required.'
        if error is None:
            cur.execute("INSERT INTO test VALUES (%s, %s)", [username, password])
            return 'User registered successfully'
        else:
            return error
    else:
        return render_template('auth/register.html')
    

# <---------------------------------------PRODUCTS-------------------------------------------------------------->

# Searching for a product using PID
@app.route('/product/id/<prod_id>')
def get_product(prod_id):
    cur.execute("SELECT * FROM product WHERE prod_id = %s", [prod_id])
    keys = cur.column_names
    values = cur.fetchone()
    res = dict(zip(keys, values))
    return render_template('product/product.html', product=res)

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
    cur.execute(f"SELECT * FROM {category}")
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
