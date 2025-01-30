from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# Configure SQLite Database (SQLite file path is 'users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite file path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = TRUE
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Define User Model (This model should match the existing table structure)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    bank_account = db.Column(db.String(20), unique=True, nullable=False)
    credit_card = db.Column(db.String(20), unique=True, nullable=False)

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        bank_account = request.form['bank_account']
        credit_card = request.form['credit_card']

        # Check if user already exists by username, email, bank_account, or credit_card
        existing_user = User.query.filter_by(username=username).first() or \
                        User.query.filter_by(email=email).first() or \
                        User.query.filter_by(bank_account=bank_account).first() or \
                        User.query.filter_by(credit_card=credit_card).first()

        if existing_user:
            flash("Username, email, bank account, or credit card already exists!", "error")
            return redirect(url_for('register'))

        try:
            # Create new user and save to database
            new_user = User(username=username, email=email, password=password, bank_account=bank_account, credit_card=credit_card)
            db.session.add(new_user)
            db.session.commit()
            flash("User registered successfully!", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            db.session.rollback()  # In case of error, rollback the transaction

    return render_template('register.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user'] = user.username  # Store user session
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

# Dashboard (Displays User Info After Login)
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        user = User.query.filter_by(username=session['user']).first()
        if user:
            return f"""
                <h2>Welcome, {user.username}!</h2>
                <p>Email: {user.email}</p>
                <p>Bank Account: {user.bank_account}</p>
                <p>Credit Card: {user.credit_card}</p>
                <br>
                <a href='/logout'>Logout</a>
            """
        else:
            flash("User not found!", "error")
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

