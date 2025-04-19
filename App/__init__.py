from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from App.models.database import db, Korisnik
from werkzeug.security import generate_password_hash

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '4f6sb28f0sb9q83khs'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:1234@localhost:5432/rentalab'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)


    with app.app_context():
        db.create_all()

      
        korisnici = [
            {'email': 'admin@example.com', 'username': 'admin', 'password': 'admin123', 'uloga': 'admin'},
            {'email': 'laborant@example.com', 'username': 'laborant', 'password': 'lab123', 'uloga': 'laborant'},
            {'email': 'student@example.com', 'username': 'student', 'password': 'student123', 'uloga': 'student'}
        ]
        
       
        dodaj_korisnike(korisnici)

    from .routes.login import login_bp
    app.register_blueprint(login_bp)

    return app


def dodaj_korisnike(korisnici):
    for korisnik in korisnici:
        postojeci = Korisnik.query.filter_by(username=korisnik['username']).first()
        if not postojeci:
            novi_korisnik = Korisnik(
                email=korisnik['email'],
                username=korisnik['username'],
                password=generate_password_hash(korisnik['password']),
                uloga=korisnik['uloga']
            )
            db.session.add(novi_korisnik)

    db.session.commit()
    print("Korisnici uspješno ubačeni (ako već nisu postojali).")
