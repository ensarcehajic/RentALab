from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Oprema(db.Model):
    __tablename__ = 'oprema'
    id = db.Column(db.Integer, primary_key=True)
    inventory_number = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), nullable=False)
    model_number = db.Column(db.String(100), nullable=False)
    supplier = db.Column(db.String(100), nullable=False)
    date_of_acquisition = db.Column(db.Date, nullable=False)
    warranty_until = db.Column(db.Date, nullable=False)
    purchase_value = db.Column(db.Integer, nullable=False)
    project = db.Column(db.String(100), nullable=False)
    service_period = db.Column(db.String(100), nullable=False)
    next_service = db.Column(db.Date, nullable=False)
    labaratory_assistant = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    available = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(500), nullable=False)
    
    
