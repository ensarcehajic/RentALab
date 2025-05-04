from App.models.database import db, Oprema
from flask import Blueprint,Flask, render_template, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import os, csv, psycopg2

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

equipment_bp = Blueprint('equipment_bp', __name__, template_folder=template_dir, static_folder=static_dir)

class OpremaForm(FlaskForm):
    naziv = StringField("Naziv opreme", validators=[DataRequired()])
    kolicina = IntegerField("Kolicina", validators=[DataRequired(), NumberRange(min=1)])
    kategorija = StringField("Kategorija", validators=[DataRequired()])
    submit = SubmitField("Dodaj")

@equipment_bp.route("/dodaj", methods=['GET', 'POST'])
def dodaj_opremu():
    form = OpremaForm()
    if form.validate_on_submit():
        novi_unos = Oprema(
            naziv=form.naziv.data, 
            kolicina=form.kolicina.data, 
            kategorija=form.kategorija.data
        )
        db.session.add(novi_unos)
        db.session.commit()
    elif 'file' in request.files:
        file = request.files['file']
        if file.filename.endswith('.csv'):
            file.stream.seek(0)
            csv_file = csv.reader(file.stream.read().decode('utf-8').splitlines())
            next(csv_file)

            conn = psycopg2.connect(dbname="rentalab", user="admin", password="1234", host="localhost")
            cur = conn.cursor()

            for row in csv_file:    
                naziv, kolicina, kategorija = row
                cur.execute(
                    "INSERT INTO oprema(naziv, kolicina, kategorija) VALUES (%s, %s, %s)",
                    (naziv, kolicina, kategorija)
            )
            conn.commit()
            cur.close()
            conn.close()

    return render_template("dodavanje_opreme.html", form=form)
@equipment_bp.route('/dashboard')
def back_to_dashboard():
    return render_template("dashboard.html")