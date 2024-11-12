from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "python-flask"  # Change this to a random secret key

db = SQLAlchemy(app)

# Define the Users model
class Users(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.sno} - {self.username}"

# Create all tables
with app.app_context():
    db.create_all()
    print(Users.query.all())

# Routes
@app.route('/about', methods=['GET', 'POST'])
def About():
    return render_template('about.html')

@app.route('/home', methods=['GET', 'POST'])
def Home():
    return render_template('home.html')

@app.route('/index', methods=['GET', 'POST'])
def Index():
    return render_template('index.html')

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Debugging output to verify data
        print(f"Form submitted: username={username}, email={email}, password={password}")

        # Check that all fields are provided
        if not username or not email or not password:
            flash("All fields are required!")
            return redirect(url_for('signup'))

        # Create and add the new user to the database
        new_user = Users(username=username, email=email, password=password)

        try:
            db.session.add(new_user)
            db.session.commit()
            print("User added to the database.")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to the database: {e}")
            flash("An error occurred. Please try again.")
            return redirect(url_for('signup'))

    # Retrieve all users to display on the page
    all_users = Users.query.all()

    return render_template('index.html', all_users=all_users)

@app.route('/register', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        # Debugging output to verify data
        print(f"Form submitted: username={username}, email={email}, password={password}")

        # Check that all fields are provided
        if not username or not email or not password:
            flash("All fields are required!")
            return redirect(url_for('signup'))

        # Create and add the new user to the database
        new_user = Users(username=username, email=email, password=password)

        try:
            db.session.add(new_user)
            db.session.commit()
            print("User added to the database.")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to the database: {e}")
            flash("An error occurred. Please try again.")
            return redirect(url_for('signup'))

    # Retrieve all users to display on the page
    all_users = Users.query.all()
    return render_template('index.html', all_users=all_users)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Query user with SQLAlchemy instead of direct SQLite connection
        user = Users.query.filter_by(username=username, email=email, password=password).first()
        
        if user:
            session['username'] = username
            return redirect(url_for('profile'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    # Query all users and render profile template
    all_users = Users.query.all()
    return render_template('profile.html', all_users=all_users)

if __name__ == '__main__':
    app.run(debug=True, port=3000)
