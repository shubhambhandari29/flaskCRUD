from datetime import datetime
from app import db

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