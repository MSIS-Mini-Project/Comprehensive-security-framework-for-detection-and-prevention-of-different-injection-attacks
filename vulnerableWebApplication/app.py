import pymysql
import socket
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# MySQL Database Configuration
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "anujna2634@2002"
DB_NAME = "flask_users"

# Establish a persistent database connection
connection = pymysql.connect(host=DB_HOST,
                             user=DB_USER,
                             password=DB_PASSWORD,
                             database=DB_NAME,
                             cursorclass=pymysql.cursors.DictCursor)

def get_db_cursor():
    return connection.cursor()

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# Registration Page (Vulnerable to SQL Injection)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']  # Storing password in plaintext (INSECURE)
        bank_account = request.form['bank_account']
        credit_card = request.form['credit_card']

        cursor = get_db_cursor()
        try:
            query = f"INSERT INTO user (username, email, password, bank_account, credit_card) VALUES ('{username}', '{email}', '{password}', '{bank_account}', '{credit_card}')"
            cursor.execute(query)
            connection.commit()
            flash("User registered successfully!", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            connection.rollback()
        return redirect(url_for('home'))

    return render_template('register.html')

# Login Page (Vulnerable to SQL Injection)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = get_db_cursor()
        query = f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
        cursor.execute(query)
        user = cursor.fetchone()

        if user:
            session['user'] = user['username']
        else:
            flash("Invalid credentials!", "error")
        return redirect(url_for('home'))

    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        cursor = get_db_cursor()
        query = f"SELECT * FROM user WHERE username = '{session['user']}'"
        cursor.execute(query)
        user = cursor.fetchone()

        if user:
            flash(f"Welcome, {user['username']}! Email: {user['email']} Bank Account: {user['bank_account']} Credit Card: {user['credit_card']}", "info")
        else:
            flash("User not found!", "error")
    return redirect(url_for('home'))

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)  # Running Flask on port 5000
#modified code