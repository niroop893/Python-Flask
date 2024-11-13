from flask import Flask, render_template, request, redirect, url_for, session, jsonify
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

class Products(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(200), nullable=False)
    product = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.sno} - {self.product}"

# Create all tables
with app.app_context():
    db.create_all()
    print(Products.query.all())

# Routes
@app.route('/about', methods=['GET', 'POST'])
def About():
    return render_template('about.html')

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
            print("All fields are required!")
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
            print("An error occurred. Please try again.")
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
            print("All fields are required!")
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
            print("An error occurred. Please try again.")
            return redirect(url_for('signup'))

    # Retrieve all users to display on the page
    all_users = Users.query.all()
    return render_template('index.html', all_users=all_users)

@app.route('/products', methods=['GET', 'POST'])
def manage_products():
    if request.method == 'POST':
        type = request.form.get('type')
        product = request.form.get('product')
        price = request.form.get('price')

        if type and product and price:
            new_product = Products(type=type, product=product, price=float(price))
            try:
                db.session.add(new_product)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error adding product: {e}")
                return redirect(url_for('manage_products'))

    # Retrieve all products for display
    all_products = Products.query.all()
    return render_template('products.html', all_products=all_products, username=session.get('username'))

# Update user route
@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update_user(sno):
    user = Users.query.get_or_404(sno)

    if request.method == 'POST':
        # Get updated data from form
        user.username = request.form['username']
        user.email = request.form['email']
        user.password = request.form['password']

        try:
            db.session.commit()  # Save changes to the database
            print("User updated successfully!")
            return redirect(url_for('signup'))  # Redirect to main user list
        except Exception as e:
            db.session.rollback()
            print(f"Error updating user: {e}")
            return redirect(url_for('update_user', sno=sno))

    return render_template('update.html', user=user)

# Delete user route
@app.route('/delete/<int:sno>', methods=['POST'])
def delete_user(sno):
    user = Users.query.filter_by(sno=sno).first()

    try:
        db.session.delete(user)
        db.session.commit()
        print("User deleted successfully!")
        return redirect(url_for('signup'))  # Redirect to main user list
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user: {e}")
        return redirect(url_for('signup'))


# Update product route
# Update product route
@app.route('/product/update/<int:sno>', methods=['GET', 'POST'])
def update_product(sno):
    product = Products.query.get_or_404(sno)

    if request.method == 'POST':
        product.type = request.form['type']
        product.product = request.form['product']
        product.price = request.form['price']

        try:
            db.session.commit()
            print("Product updated successfully!")
            return redirect(url_for('manage_products'))
        except Exception as e:
            db.session.rollback()
            print(f"Error updating product: {e}")
            return redirect(url_for('update_product', sno=sno))

    return render_template('product_update.html', product=product)

# Delete product route
@app.route('/product/delete/<int:sno>', methods=['POST'])
def delete_product(sno):
    product = Products.query.filter_by(sno=sno).first()

    if product:
        try:
            db.session.delete(product)
            db.session.commit()
            print("Product deleted successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting product: {e}")

    return redirect(url_for('manage_products'))

@app.route('/product/<int:product_id>/quantity', methods=['POST'])
def update_quantity(product_id):
    product = Products.query.get_or_404(product_id)
    action = request.json.get('action')  # "add" or "subtract"

    if action == "add":
        product.quantity += 1
    elif action == "subtract" and product.quantity > 0:
        product.quantity -= 1

    db.session.commit()
    return jsonify({"quantity": product.quantity, "price": product.price})



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Query user with SQLAlchemy
        user = Users.query.filter_by(email=email, password=password).first()
        
        if user:
            session['username'] = user.username  # Set session
            return redirect(url_for('home'))  # Redirect to home page if login successful
        else:
            print("Login failed: Invalid email or password")
            return redirect(url_for('login'))  # Redirect back to login if authentication fails
    
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Fetch products from the database (assuming a Products model is defined)
    all_products = Products.query.all()  # Adjust this line to fit your ORM/database setup

    # Render the home template with products and username
    return render_template('home.html', username=username, all_products=all_products)



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
