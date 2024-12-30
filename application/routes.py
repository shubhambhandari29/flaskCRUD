import os
from flask import flash, make_response, redirect, render_template, request, session, url_for
from application.models import User, Gift, Cart
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def register_routes(app,db):
    @app.route("/")
    def home():
        if "user_id" in session:
            # Redirect authenticated users to their dashboard
            return redirect(url_for('dashboard'))
        return render_template('home.html')  # Landing page for unauthenticated users
    
    @app.route("/dashboard")
    def dashboard():
        if "user_id" not in session:
            flash("Please log in to access the dashboard.", "warning")
            return redirect(url_for('login'))
        user = User.query.filter_by(id=session.get("user_id")).first()
        # Load gifts excluding user's own
        gifts = db.session.query(Gift, User).join(User, Gift.seller_id == User.id).filter(
    Gift.seller_id != session['user_id'], Gift.sold == False
).all()
        print("SESSSION", session)
        return render_template('dashboard.html', wallet = user.wallet,  gifts=gifts,user=session.get('username'), logged_in="user_id" in session)
    

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
    
    @app.route("/add_to_cart/<int:gift_id>", methods=["GET", "POST"])
    def add_to_cart(gift_id):
        if "user_id" not in session:
            flash("Please login to add items to your cart.", "warning")
            return redirect(url_for("login"))

        user_id = session["user_id"]
        existing_item = Cart.query.filter_by(user_id=user_id, gift_id=gift_id).first()

        if existing_item:
            flash("Item is already in your cart.", "info")
        else:
            cart_item = Cart(user_id=user_id, gift_id=gift_id)
            db.session.add(cart_item)
            db.session.commit()
            flash("Item added to cart!", "success")

        return redirect(url_for("dashboard"))
    
    @app.route("/cart", methods=["GET", "POST"])
    def view_cart():
        if "user_id" not in session:
            flash("Please login to view your cart.", "warning")
            return redirect(url_for("login"))

        user_id = session["user_id"]
        cart_items = db.session.query(Cart, Gift).join(Gift, Cart.gift_id == Gift.id).filter(Cart.user_id == user_id).all()
        user = User.query.get(user_id)
        if request.method == "POST":
            selected_items = request.form.getlist("selected_items")
            total_cost = sum(float(Gift.query.get(int(item_id)).price) for item_id in selected_items)
            if total_cost > user.wallet:
                flash("Insufficient funds in wallet!", "danger")
            else:
                for item_id in selected_items:
                    gift = Gift.query.get(int(item_id))
                    gift.sold = True
                    db.session.query(Cart).filter_by(user_id=user_id, gift_id=gift.id).delete()

                user.wallet -= total_cost
                db.session.commit()
                flash("Purchase successful!", "success")

            return redirect(url_for("view_cart"))

        return render_template("cart.html",user=session.get('username'), wallet = user.wallet, cart_items=cart_items)
    
    @app.route("/remove_from_cart/<int:cart_id>", methods=["POST"])
    def remove_from_cart(cart_id):
        if "user_id" not in session:
            flash("Please login to modify your cart.", "warning")
            return redirect(url_for("login"))

        cart_item = Cart.query.get_or_404(cart_id)
        db.session.delete(cart_item)
        db.session.commit()
        flash("Item removed from cart.", "success")
        return redirect(url_for("view_cart"))