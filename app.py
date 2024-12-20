from datetime import datetime
import os
from flask import Flask, flash, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
# Flask app setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///gifties.db"
db = SQLAlchemy(app)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Hashed password
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class Gift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(300))  # Added field for image URL
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_listed = db.Column(db.DateTime, default=datetime.utcnow)
    sold = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Gift {self.name}>'

# Routes
@app.route("/")
def home():
    """Home page showing all available gifts."""
    gifts = Gift.query.filter_by(sold=False).all()
    return render_template('home.html', gifts=gifts, logged_in="user_id" in session)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login a user."""
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password", "danger")
    return render_template('login.html')

@app.route("/logout")
def logout():
    """Logout the user by clearing the session."""
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('home'))

@app.route("/add_gift", methods=["GET", "POST"])
def add_gift():
    """Add a new gift to the marketplace."""
    if "user_id" not in session:
        flash("Please login to list a gift.", "warning")
        return redirect(url_for('login'))
    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        seller_id = session['user_id']
        price = request.form.get('price')
        image = request.files.get('image')
        
        # Validate image file
        if image and allowed_file(image.filename):
            # Secure the filename
            filename = secure_filename(image.filename)
            # Save the image to the upload folder
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Construct the image path for storage
            image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        else:
            flash('Invalid image file! Please upload a valid image (png, jpg, jpeg, gif).', 'danger')
            return redirect(request.url)
        new_gift = Gift(name=name, description=description, price=price, seller_id=seller_id, image_url=image_url)
        db.session.add(new_gift)
        db.session.commit()
        flash("Gift added successfully!", "success")
        return redirect(url_for('home'))
    return render_template('add_gift.html')

@app.route("/buy_gift/<int:gift_id>")
def buy_gift(gift_id):
    """Mark a gift as sold and remove it from the available listings."""
    if "user_id" not in session:
        flash("Please login to buy a gift.", "warning")
        return redirect(url_for('login'))
    gift = Gift.query.get_or_404(gift_id)
    gift.sold = True
    db.session.commit()
    flash("Gift purchased successfully!", "success")
    return redirect(url_for('home'))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user."""
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.", "danger")
        else:
            print("CAME BHERE")
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            print("@@@")
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/my_gifts")
def my_gifts():
    """View all gifts listed by the logged-in user."""
    if "user_id" not in session:
        flash("Please login to view your gifts.", "warning")
        return redirect(url_for('login'))
    seller_id = session['user_id']
    gifts = Gift.query.filter_by(seller_id=seller_id).all()
    return render_template('my_gifts.html', gifts=gifts)

# Initialize the database
with app.app_context():
    db.create_all()

# Run the Flask app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
