from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def root():
    return "root"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if valid_login(request.form['username'], request.form['password']):
            return 'Authenticated'
        else:
            return 'Try again!'
    else:
        return render_template('login.html')

def valid_login(username, password):
    if username == 'admin' and password == 'pass':
        return True
    return False
