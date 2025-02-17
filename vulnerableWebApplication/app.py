import pymysql
import socket
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# MySQL Database Configuration
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "----" # enter your password
DB_NAME = "----" #enter the table name

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

# 🔴 Registration Page (Vulnerable to SQL Injection)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')  # Storing password in plaintext (INSECURE)
        bank_account = request.form.get('bank_account', '')
        credit_card = request.form.get('credit_card', '')

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # 🔴 VULNERABLE: Directly concatenating user input
            query = f"""
            INSERT INTO user (username, email, password, bank_account, credit_card)
            VALUES ('{username}', '{email}', '{password}', '{bank_account}', '{credit_card}')
            """
            cursor.execute(query)
            connection.commit()
            flash("User registered successfully!", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    return render_template('register.html')

# 🔴 Login Page (Vulnerable to SQL Injection)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("Raw Request Data:", request.data)
        print("Form Data:", request.form)
        
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if not username or not password:
            flash("Missing username or password!", "error")
            return redirect(url_for('login'))

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # 🔴 VULNERABLE: Directly inserting user input into SQL query
            query = f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
            print("Executing query:", query)  # Debugging
            cursor.execute(query)
            user = cursor.fetchone()
            print("Query result:", user)  # Debugging Output

            if user:
                session['user'] = user['username']
                print("Login Successful. Redirecting to dashboard...")  # Debugging
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials!", "error")
                return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
        finally:
            cursor.close()
            connection.close()

    return render_template('login.html')

# 🔴 Dashboard (Fetching User Data Insecurely)
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = f"SELECT * FROM user WHERE username = '{session['user']}'"
        print("Executing query:", query)  # Debugging
        cursor.execute(query)
        user = cursor.fetchone()
        print("Query result:", user)  # Debugging Output

        cursor.close()
        connection.close()

        if user:
            return f"""
                <h2>Welcome, {user['username']}!</h2>
                <p>Email: {user['email']}</p>
                <p>Bank Account: {user['bank_account']}</p>
                <p>Credit Card: {user['credit_card']}</p>
                <br>
                <a href='/logout'>Logout</a>
            """
        else:
            flash("User not found!", "error")
            return redirect(url_for('login'))
    else:
        flash("Session not found. Please login.", "error")
        return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)

    #updated code
    #newbranch