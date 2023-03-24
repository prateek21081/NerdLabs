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

@app.route('/product/<prod_id>')
def get_product(prod_id):
    cur.execute("SELECT * FROM product WHERE prod_id = %s", [prod_id])
    keys = cur.column_names
    values = cur.fetchone()
    res = dict(zip(keys, values))
    return json.dumps(res)
