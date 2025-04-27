from App.models.database import db, Oprema
from flask import Blueprint,Flask, render_template, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import os

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

equipment_bp = Blueprint('equipment_bp', __name__, template_folder=template_dir, static_folder=static_dir)

class OpremaForm(FlaskForm):
    naziv = StringField("Naziv opreme", validators=[DataRequired()])
    kolicina = IntegerField("Kolicina", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Dodaj opremu")

@equipment_bp.route("/dodaj", methods=['GET', 'POST'])
def dodaj_opremu():
    form = OpremaForm()
    if form.validate_on_submit():
        novi_unos = Oprema(naziv=form.naziv.data, kolicina=form.kolicina.data)
        db.session.add(novi_unos)
        db.session.commit()
        return redirect(url_for('login_bp.dashboard'))
    return render_template("dodavanje_opreme.html", form=form)