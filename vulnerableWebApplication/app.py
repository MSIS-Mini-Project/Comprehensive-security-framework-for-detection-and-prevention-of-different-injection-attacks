import pymysql
import subprocess
from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# MySQL Database Configuration
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "Siddharth1"  # Replace with your actual password
DB_NAME = "users"  # Database name

# Function to establish a MySQL connection
def get_db_connection():
    return pymysql.connect(host=DB_HOST,
                           user=DB_USER,
                           password=DB_PASSWORD,
                           database=DB_NAME,
                           cursorclass=pymysql.cursors.DictCursor)

# 🔴 Function to Log User Activity (Vulnerable to Code Injection)
def log_activity(username, action):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = f"INSERT INTO activity_log (username, action) VALUES ('{username}', '{action}')"
        cursor.execute(query)
        connection.commit()
    except Exception as e:
        print(f"Activity Log Error: {e}")
    finally:
        cursor.close()
        connection.close()

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

# 🔴 Login Page (Vulnerable to SQL Injection + HTTP Header Injection)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            # 🔴 VULNERABLE: Directly inserting user input into SQL query
            query = f"SELECT * FROM user WHERE username = '{username}' AND password = '{password}'"
            cursor.execute(query)
            user = cursor.fetchone()

            if user:
                session['user'] = user['username']
                log_activity(user['username'], "Logged in")  # Logging activity

                # 🔴 HTTP Header Injection (No Template Change)
                custom_header = username  # User input injected into response headers

                response = make_response(redirect(url_for('dashboard')))
                response.headers['X-Custom-Header'] = custom_header  # Vulnerable to HTTP Header Injection
                return response
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
        cursor.execute(query)
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user:
            return render_template('dashboard.html', user=user)
        else:
            flash("User not found!", "error")
            return redirect(url_for('login'))
    else:
        flash("Session not found. Please login.", "error")
        return redirect(url_for('login'))

# 🔴 Activity Log Viewer (Fixed Filtering Issue, Still Vulnerable to Code Injection)
@app.route('/activity_log', methods=['GET', 'POST'])
def activity_log():
    if 'user' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor()

    query = f"SELECT * FROM activity_log WHERE username = '{session['user']}'"
    cursor.execute(query)
    logs = cursor.fetchall()  # Ensure this returns a valid list of logs
    cursor.close()
    connection.close()

    filtered_logs = logs  # Default is the full log list
    system_output = ""  # Variable to hold system command output

    if request.method == 'POST':
        filter_expression = request.form.get('filter', '')

        try:
            print(f"Evaluating filter expression: {filter_expression}")  # Debugging
            
            # If user input contains a system command, execute it correctly
            if "subprocess" in filter_expression:
                system_output = eval(filter_expression)  # Executes subprocess calls
            elif "os.system" in filter_expression:
                command = filter_expression.replace("os.system(", "").replace(")", "").strip("'\"")
                system_output = subprocess.getoutput(command)  # Captures and returns system command output
            else:
                # Evaluate the filter expression normally for logs
                filtered_logs = eval(filter_expression)

            # Ensure filtered_logs is a list, else fallback to default
            if not isinstance(filtered_logs, list):
                filtered_logs = logs[:5]  # Show the first 5 logs if the expression is invalid

        except Exception as e:
            # If there's an error evaluating, show the error message
            filtered_logs = [f"Error: {e}"]
            system_output = f"Error: {e}"
            print(f"Error in eval(): {e}")  # Debugging

    return render_template('activity_log.html', logs=filtered_logs, system_output=system_output)

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)
