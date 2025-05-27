from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from App.models.database import db, User
from werkzeug.security import generate_password_hash
from flask_login import LoginManager
from flask_mail import Mail

mail = Mail()
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

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'faris.alic@fet.ba'
    app.config['MAIL_PASSWORD'] = 'pvjagewgyzefbhag'
    app.config['MAIL_DEFAULT_SENDER'] = 'faris.alic@fet.ba'

    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)  

    with app.app_context():
        db.create_all()

        users = [
    {
        'email': 'admin@fet.ba',
        'name': 'Admin',
        'surname': 'User',
        'address': 'Admin Street 1',
        'city': 'AdminCity',
        'phone_number': '111-111',
        'password': 'admin123',
        'role': 'admin',
        'verified': True
    },
    {
        'email': 'laborant@fet.ba',
        'name': 'Lab',
        'surname': 'Tech',
        'address': 'Lab Street 2',
        'city': 'LabCity',
        'phone_number': '222-222',
        'password': 'laborant123',
        'role': 'laborant',
        'verified': True
    },
    {
        'email': 'student@fet.ba',
        'name': 'Student',
        'surname': 'One',
        'address': 'Student Ave 3',
        'city': 'StudentCity',
        'phone_number': '333-333',
        'password': 'student123',
        'role': 'student',
        'verified': True
    }
]
        add_users(users)
        
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from App.models.database import db, User
from werkzeug.security import generate_password_hash
from flask_login import LoginManager
from flask_mail import Mail

mail = Mail()
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

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'faris.alic@fet.ba'
    app.config['MAIL_PASSWORD'] = 'pvjagewgyzefbhag'
    app.config['MAIL_DEFAULT_SENDER'] = 'faris.alic@fet.ba'

    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)  

    with app.app_context():
        db.create_all()

        users = [
    {
        'email': 'admin@fet.ba',
        'name': 'Admin',
        'surname': 'User',
        'address': 'Admin Street 1',
        'city': 'AdminCity',
        'phone_number': '111-111',
        'password': 'admin123',
        'role': 'admin',
        'verified': True
    },
    {
        'email': 'laborant@fet.ba',
        'name': 'Lab',
        'surname': 'Tech',
        'address': 'Lab Street 2',
        'city': 'LabCity',
        'phone_number': '222-222',
        'password': 'laborant123',
        'role': 'laborant',
        'verified': True
    },
    {
        'email': 'student@fet.ba',
        'name': 'Student',
        'surname': 'One',
        'address': 'Student Ave 3',
        'city': 'StudentCity',
        'phone_number': '333-333',
        'password': 'student123',
        'role': 'student',
        'verified': True
    }
]
        add_users(users)

    from .routes.login import login_bp
    app.register_blueprint(login_bp)

    from .routes.equipment import equipment_bp
    app.register_blueprint(equipment_bp)

    from .routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from .routes.profile import profile_bp
    app.register_blueprint(profile_bp)
    
    return app


def add_users(users):
    for user in users:
        existing_user = User.query.filter_by(email=user['email']).first()
        if not existing_user:
            new_user = User(
                name=user['name'],
                surname=user['surname'],
                email=user['email'],
                address=user['address'],
                city=user['city'],
                phone_number=user['phone_number'],
                password=generate_password_hash(user['password']),
                role=user['role'],
                verified=user['verified']
            )
            db.session.add(new_user)
    db.session.commit()
    print("Users successfully added (if they didn't already exist).")