from App.models.database import db, Oprema
from flask import Blueprint,Flask, render_template, render_template_string, request, redirect, url_for,session,make_response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange,InputRequired
from sqlalchemy import func
import os
import csv
from io import StringIO

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

equipment_bp = Blueprint('equipment_bp', __name__, template_folder=template_dir, static_folder=static_dir)

class OpremaForm(FlaskForm):
    naziv = StringField("Naziv opreme", validators=[DataRequired()])
    kolicina = IntegerField("Kolicina", validators=[InputRequired(), NumberRange(min=0)])
    kategorija = StringField("Kategorija", validators=[DataRequired()])
    submit = SubmitField("Dodaj opremu")

@equipment_bp.route('/download-csv')
def download_csv():
    if session.get('role') not in ['admin', 'laborant']:
        return redirect(url_for('login_bp.dashboard'))

    oprema = Oprema.query.all()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Naziv', 'Količina', 'Kategorija'])
    for item in oprema:
        writer.writerow([item.naziv, item.kolicina, item.kategorija])

    response = make_response(si.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=oprema.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

@equipment_bp.route('/browse')
def pregledaj_opremu():
    if 'user' not in session:
        return redirect(url_for('login_bp.login'))

    kategorije = [k[0] for k in db.session.query(Oprema.kategorija).distinct().all()]
    odabrana_kategorija = request.args.get('kategorija')
    search = request.args.get('search', '').strip().lower()

    query = Oprema.query

    if odabrana_kategorija:
        query = query.filter_by(kategorija=odabrana_kategorija)

    if search:
        query = query.filter(func.lower(Oprema.naziv).like(f'%{search}%'))

    sva_oprema = query.all()
    role = session.get('role')

    return render_template(
        'browse_equipment.html',
        sva_oprema=sva_oprema,
        role=role,
        kategorije=kategorije,
        odabrana_kategorija=odabrana_kategorija,
        search=search
    )

@equipment_bp.route("/dodaj", methods=['GET', 'POST'])
def dodaj_opremu():
    if 'user' not in session:
        return redirect(url_for('login_bp.login'))
    if (session.get('role') not in ['admin','laborant']):
        return redirect(url_for('login_bp.dashboard'))
    form = OpremaForm()
    if form.validate_on_submit():
        postojeca_oprema = Oprema.query.filter(func.lower(Oprema.naziv) == form.naziv.data.lower()).first()
        if postojeca_oprema:
            postojeca_oprema.kolicina += form.kolicina.data
        else:
            novi_unos = Oprema(naziv=form.naziv.data, kolicina=form.kolicina.data, kategorija=form.kategorija.data)
            db.session.add(novi_unos)
        db.session.commit()
        return redirect(url_for('login_bp.dashboard'))
    return render_template("dodavanje_opreme.html", form=form)
