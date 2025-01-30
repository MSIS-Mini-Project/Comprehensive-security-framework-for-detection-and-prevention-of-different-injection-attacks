from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from models.user import User  # Import User from models/user.py

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite file path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Create database tables (if they don't already exist)
with app.app_context():
    db.create_all()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        bank_account = request.form['bank_account']
        credit_card = request.form['credit_card']

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists!"

        # Create new user and save to database
        new_user = User(username=username, email=email, password=password, bank_account=bank_account, credit_card=credit_card)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

# Other routes here...

if __name__ == '__main__':
    app.run(debug=True)

