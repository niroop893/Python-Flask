from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
import sqlite3


app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

import os
print("Template Folder Path:", os.path.join(os.getcwd(), 'templates'))
app.secret_key = "python-flask"  # Change this to a random secret key

class Users(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.sno} -{self.username}"

with app.app_context():
    db.create_all()
    

    


# Function to connect to the SQLite database
def connect_db():
    conn = sqlite3.connect('database.db')
    conn.execute('CREATE TABLE USERS IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, email TEXT, password TEXT)')
    conn.commit()
    return conn

@app.route('/about', methods=['GET', 'POST'])
def About():
    return render_template('about.html')

@app.route('/home', methods=['GET', 'POST'])
def Home():
    return render_template('home.html')

@app.route('/index', methods=['GET', 'POST'])
def Index():
    return render_template('index.html')

@app.route('/profile', methods=['GET', 'POST'])
def Profile():
    return render_template('profile.html')

@app.route('/', methods=['GET', 'POST'])
def hello_world():
    details = Users(username="Jolly",email="Jian@test.com",password="pass123")
    db.session.add(details)
    db.session.commit()
    all_users = details.query.all()
    print(all_users)
    return render_template('index.html', all_users=all_users)
# Route for signing up
# Route for signing up
@app.route('/register', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']  # Add email field
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO USERS (username, email, password) VALUES (?, ?, ?)', (username, password, email))  # Include email in INSERT statement
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

# Route for logging in
# Route for logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM USERS WHERE username = ? AND email = ? AND password = ?', (username, email, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('user_profile'))  # Redirect to user profile page
    return render_template('login.html')

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Route for user profile
@app.route('/profile')
def profile():
    if 'username' in session:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM USERS')
        users = cursor.fetchall()
        conn.close()
        print(users)
        return render_template('profile.html', users=users)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=3000)
