import pymysql
import socket
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# MySQL Database Configuration
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "Siddharth1"
DB_NAME = "users"

# Function to establish a MySQL connection
def get_db_connection():
    return pymysql.connect(host=DB_HOST,
                           user=DB_USER,
                           password=DB_PASSWORD,
                           database=DB_NAME,
                           cursorclass=pymysql.cursors.DictCursor)

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# 🔴 Registration Page (More Vulnerable to SQL Injection)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        bank_account = request.form['bank_account']
        credit_card = request.form['credit_card']

        connection = get_db_connection()
        cursor = connection.cursor()

        # 🔴 VULNERABLE: Directly concatenating user input (No exception handling)
        query = f"""
        INSERT INTO user (username, email, password, bank_account, credit_card)
        VALUES ('{username}', '{email}', '{password}', '{bank_account}', '{credit_card}')
        """
        cursor.execute(query)
        connection.commit()
        
        return "User registered successfully!"

    return render_template('register.html')

# 🔴 Login Page (Fully Vulnerable to SQL Injection)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor()

        # 🔴 VULNERABLE: Allowing UNION-based SQL Injection with correct column count
        query = f"SELECT id, username, email, password, bank_account, credit_card FROM user WHERE username = '{username}' AND password = '{password}'"
        try:
            print("Executing query:", query)
            cursor.execute(query)
            user = cursor.fetchone()
            if user:
                session['user'] = user['username']
                return redirect(url_for('dashboard'))
            else:
                return "Invalid credentials!"
        except Exception as e:
            return f"SQL Error: {str(e)}"
    
    return render_template('login.html')

# 🔴 Dashboard (Fetching User Data Insecurely, Allowing UNION Injection)
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        connection = get_db_connection()
        cursor = connection.cursor()

        # 🔴 VULNERABLE: Making UNION Injection work by ensuring 6-column count
        query = f"""
        SELECT id, username, email, password, bank_account, credit_card FROM user WHERE username = '{session['user']}'
        UNION SELECT NULL, database(), user(), 'dummy', 'dummy', 'dummy' FROM dual
        """
        try:
            cursor.execute(query)
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if user:
                return f"""
                    <h2>Welcome, {user['username']}!</h2>
                    <p>Email: {user['email']}</p>
                    <p>Password: {user['password']}</p>
                    <p>Bank Account: {user['bank_account']}</p>
                    <p>Credit Card: {user['credit_card']}</p>
                    <br>
                    <a href='/logout'>Logout</a>
                """
            else:
                return "User not found!"
        except Exception as e:
            return f"SQL Error: {str(e)}"
    else:
        return "Unauthorized access!"

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return "Logged out successfully!"

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)

