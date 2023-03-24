from flask import Flask, request, render_template
import mysql.connector

app = Flask(__name__)
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
    return "root"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
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
            cur.execute("INSERT INTO test VALUES (%s, %s)", (username, password))
            return 'User registered successfully'
        else:
            return error
    else:
        return render_template('auth/register.html')

def valid_login(username, password):
    if username == 'admin' and password == 'pass':
        return True
    return False
