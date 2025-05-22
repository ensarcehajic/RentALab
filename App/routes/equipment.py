from App.models.database import db, Oprema, Rented, User
from flask import Blueprint,Flask, render_template, render_template_string, request, redirect, url_for,session,make_response, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, SelectField, DateTimeField, DecimalField
from wtforms.validators import DataRequired, NumberRange, InputRequired, Optional

from sqlalchemy import func
import os
from datetime import datetime
import csv,psycopg2
from io import StringIO
from datetime import datetime

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

equipment_bp = Blueprint('equipment_bp', __name__, template_folder=template_dir, static_folder=static_dir)

class OpremaForm(FlaskForm):
    naziv = StringField("Naziv opreme", validators=[DataRequired()])
    kolicina = IntegerField("Kolicina", validators=[InputRequired(), NumberRange(min=0)])
    kategorija = StringField("Kategorija", validators=[DataRequired()])
    submit = SubmitField("Dodaj opremu")

class RentedForm(FlaskForm):
    # Role-based IDs and Names
    issued_by_id = IntegerField("Issuer ID", default=0)  
    issued_by_name = StringField("Issuer Name", default="")

    approver_id = IntegerField("Approver ID", default=0)  
    approver_name = StringField("Approver Name", default="")

    renter_id = IntegerField("Renter ID", default=0)  
    renter_name = StringField("Renter Name", default="")
    renter_telephone = StringField("Renter Phone", default="")
    renter_address = StringField("Renter Address", default="")

    inventory_number = StringField("Inventory Number", default="", validators=[DataRequired()])
    equipment_name = StringField("Equipment Name", default="", validators=[DataRequired()])
    description = TextAreaField("Equipment Description", default="", validators=[Optional()])
    serial_number = StringField("Serial Number", default="", validators=[Optional()])
    model_number = StringField("Model Number", default="", validators=[Optional()])
    provider = StringField("Manufacturer / Supplier", default="", validators=[Optional()])
    
    equipment_value = DecimalField("Equipment Value (BAM)", places=2, default=None, validators=[Optional()])
    project = StringField("Project", default="", validators=[Optional()])
    serves_period = StringField("Service Period", default="", validators=[Optional()])
    next_servis = DateTimeField("Next Service Date", format="%Y-%m-%d", default=None, validators=[Optional()])
    date_buy = DateTimeField("Purchase Date", format="%Y-%m-%d", default=None, validators=[Optional()])
    warranty_date = DateTimeField("Warranty Expiry", format="%Y-%m-%d", default=None, validators=[Optional()])

    date_rent_start = DateTimeField("Rental Start Date", format="%Y-%m-%d %H:%M:%S", default=None, validators=[Optional()])
    date_rent_end = DateTimeField("Rental End Date", format="%Y-%m-%d %H:%M:%S", default=None, validators=[Optional()])
    
    status = SelectField(
        "Status",
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("ended", "Ended"),
            ("rejected", "Rejected")
        ],
        default="pending",
        validators=[DataRequired()]
    )
    
    note = TextAreaField("Note", default="", validators=[Optional()])
    submit = SubmitField("Submit")


@equipment_bp.route('/rent', methods=['GET', 'POST'])
def rent():
    if 'user' not in session:
        return redirect(url_for('login_bp.login'))

    form = RentedForm()
    error_message = None

    if form.validate_on_submit():
        renter = User.query.get(form.renter_id.data)
        approver = User.query.get(form.approver_id.data)
        issuer = User.query.get(form.issued_by_id.data)
        equipment = Oprema.query.get(int(form.inventory_number.data))

        if not renter:
            error_message = 'Renter ID does not exist.'
        elif not approver:
            error_message = 'Approver ID does not exist.'
        elif approver.role.lower() != 'profesor':
            error_message = 'Approver must have the role "profesor".'
        elif not issuer:
            error_message = 'Issuer ID does not exist.'
        elif issuer.role.lower() != 'laborant':
            error_message = 'Issuer must have the role "laborant".'
        elif not equipment:
            error_message = 'Equipment inventory number does not exist.'
        else:
            rented_item = Rented(
                renter_id=form.renter_id.data,
                approver_id=form.approver_id.data,
                issued_by_id=form.issued_by_id.data,
                inventory_number_id=int(form.inventory_number.data),
                start_date=form.date_rent_start.data or datetime.utcnow(),
                end_date=form.date_rent_end.data,
                project=form.project.data,
                subject=form.equipment_name.data,
                status=form.status.data,
                note=form.note.data
            )
            db.session.add(rented_item)
            db.session.commit()
            return redirect(url_for('login_bp.dashboard'))

    return render_template('rent.html', form=form, error_message=error_message)




@equipment_bp.route('/download-csv')
def download_csv():
    if 'user' not in session:
        return redirect(url_for('login_bp.login'))

    if session.get('role') not in ['admin', 'laborant']:
        return redirect(url_for('login_bp.dashboard'))

    oprema = Oprema.query.all()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Naziv', 'Količina', 'Kategorija'])
    for item in oprema:
        writer.writerow([item.naziv, item.kolicina, item.kategorija])

    
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') 
    filename = f'oprema_{now}.csv' 

    response = make_response(si.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
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

    if session.get('role') not in ['admin', 'laborant']:
        return redirect(url_for('login_bp.dashboard'))

    form = OpremaForm()

    if form.validate_on_submit():
        
        postojeca_oprema = Oprema.query.filter(
            func.lower(Oprema.naziv) == form.naziv.data.lower()
        ).first()

        if postojeca_oprema:
            postojeca_oprema.kolicina += form.kolicina.data
        else:
            novi_unos = Oprema(
                naziv=form.naziv.data,
                kolicina=form.kolicina.data,
                kategorija=form.kategorija.data
            )
            db.session.add(novi_unos)

        db.session.commit()
        return redirect(url_for('login_bp.dashboard'))

    
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            file.stream.seek(0)
            csv_file = csv.reader(file.stream.read().decode('utf-8').splitlines())
            next(csv_file)  

            conn = psycopg2.connect(
                dbname="rentalab", user="admin", password="1234", host="localhost"
            )
            cur = conn.cursor()

            for row in csv_file:
                try:
                    naziv, kolicina, kategorija = row
                except ValueError:
                    continue  

                cur.execute("SELECT id, kolicina FROM oprema WHERE LOWER(naziv) = LOWER(%s)", (naziv,))
                existing = cur.fetchone()

                if existing:
                    nova_kolicina = existing[1] + int(kolicina)
                    cur.execute("UPDATE oprema SET kolicina = %s WHERE id = %s", (nova_kolicina, existing[0]))
                else:
                    cur.execute(
                        "INSERT INTO oprema(naziv, kolicina, kategorija) VALUES (%s, %s, %s)",
                        (naziv, kolicina, kategorija)
                    )


            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('login_bp.dashboard'))

    return render_template("dodavanje_opreme.html", form=form)
@equipment_bp.route('/dashboard')
def back_to_dashboard():
    return render_template("dashboard.html")


@equipment_bp.route('/izmijeni/<int:oprema_id>', methods=['GET', 'POST'])
def izmijeni_opremu(oprema_id):
     if 'user' not in session:
        return redirect(url_for('login_bp.login'))
     
     if session.get('role') not in ['admin', 'laborant']:
        return redirect(url_for('login_bp.dashboard'))

     oprema = Oprema.query.get_or_404(oprema_id)
     form = OpremaForm(obj=oprema)

     if form.validate_on_submit():
        oprema.naziv = form.naziv.data
        oprema.kolicina = form.kolicina.data
        oprema.kategorija = form.kategorija.data
        db.session.commit()
        return redirect(url_for('equipment_bp.pregledaj_opremu'))

     return render_template('dodavanje_opreme.html', form=form, izmjena=True)

@equipment_bp.route('/izbrisi/<int:oprema_id>', methods=['POST'])
def izbrisi_opremu(oprema_id):
     if 'user' not in session:
        return redirect(url_for('login_bp.login'))

     if session.get('role') not in ['admin', 'laborant']:
        return redirect(url_for('login_bp.dashboard'))

     oprema = Oprema.query.get_or_404(oprema_id)
     db.session.delete(oprema)
     db.session.commit()
     return redirect(url_for('equipment_bp.pregledaj_opremu'))

