from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from App.models.database import db, User
from werkzeug.security import generate_password_hash
from flask_login import LoginManager

login_manager = LoginManager()

migrate = Migrate()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '4f6sb28f0sb9q83khs'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:1234@localhost:5432/rentalab'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)  

    with app.app_context():
        db.create_all()

        users = [
            {'email': 'admin@example.com', 'username': 'admin', 'password': 'admin123', 'role': 'admin'},
            {'email': 'laborant@example.com', 'username': 'laborant', 'password': 'laborant123', 'role': 'laborant'},
            {'email': 'student@example.com', 'username': 'student', 'password': 'student123', 'role': 'student'}
        ]
        
        add_users(users)

    from .routes.login import login_bp
    app.register_blueprint(login_bp)

    from .routes.equipment import equipment_bp
    app.register_blueprint(equipment_bp)

    return app


def add_users(users):
    for user in users:
        existing_user = User.query.filter_by(username=user['username']).first()
        if not existing_user:
            new_user = User(
                email=user['email'],
                username=user['username'],
                password=generate_password_hash(user['password']),
                role=user['role']
            )
            db.session.add(new_user)
    db.session.commit()
    print("Users successfully added (if they didn't already exist).")
