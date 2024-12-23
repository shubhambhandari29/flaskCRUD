import os
from flask import flash, make_response, redirect, render_template, request, session, url_for
from models import User, Gift
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def register_routes(app,db):
    @app.route("/")
    def home():
        user_id = session.get("user_id")
        if user_id:
        # Exclude gifts of the logged-in user
            gifts = db.session.query(Gift, User).join(User, Gift.seller_id == User.id).filter(
            Gift.seller_id != user_id, Gift.sold == False
        ).all()
        else:
        # Show all unsold gifts for anonymous users
            gifts = db.session.query(Gift, User).join(User, Gift.seller_id == User.id).filter(
            Gift.sold == False
        ).all()

        return render_template('home.html', gifts=gifts,logged_in="user_id" in session)
    

    @app.route("/login", methods=["GET", "POST"])
    def login():
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
        
        response = make_response(render_template('login.html'))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        return render_template('login.html')
    
    @app.route("/logout")
    def logout():
        """Logout the user by clearing the session."""
        session.clear()
        flash("Logged out successfully!", "info")
        return redirect(url_for('home'))
    
    @app.route("/add_gift", methods=["GET", "POST"])
    def add_gift():
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
        print("HEREESS")
        """Register a new user."""
        if request.method == "POST":
            print("REQ MADE")
            username = request.form['username']
            email = request.form['email']
            password = generate_password_hash(request.form['password'])
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                print("EXISTR")
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
        return render_template('my_gifts.html', my_gifts=gifts)
    
    @app.route('/delete_gift/<int:id>', methods=['GET','POST'])
    def delete_gift(id):
        gift = Gift.query.get_or_404(id)
        db.session.delete(gift)
        db.session.commit()
        flash('Gift deleted successfully!', 'danger')
        return redirect(url_for('my_gifts'))
    
    @app.route('/edit_gift/<int:id>', methods=['GET', 'POST'])
    def edit_gift(id):
        gift = Gift.query.get_or_404(id)
        if request.method == 'POST':
            # Update gift details
            gift.name = request.form['name']
            gift.description = request.form['description']
            gift.price = float(request.form['price'])
            
            # Handle image update if provided
            image = request.files.get('image')
            if image:
                filename = image.filename
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                gift.image_url = f'/static/uploads/{filename}'
            
            db.session.commit()
            flash('Gift updated successfully!', 'success')
            return redirect(url_for('my_gifts'))
        
        return render_template('edit_gift.html', gift=gift)