from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
db =SQLAlchemy()
def create_app():
    app = Flask(__name__, template_folder='../templates',static_folder='../static')
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///gifties.db"
    app.secret_key = 'your_secret_key'
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    db.init_app(app=app)
    from application.models import User, Gift, Cart
    with app.app_context():
        print("HEEEE")
        db.create_all()
        print("VEEEE")
    from application.routes import register_routes
    register_routes(app,db)
    migrate = Migrate(app,db)

    return app
