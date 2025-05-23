from App.models.database import db, Oprema, equipmentImage
from flask import Blueprint,Flask, render_template, render_template_string, request,flash,  redirect, url_for,session,make_response, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import login_required
from flask_login import current_user
from wtforms import StringField, IntegerField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, NumberRange,InputRequired
from sqlalchemy import func
import os
from datetime import datetime
import csv,psycopg2
from io import StringIO
from werkzeug.utils import secure_filename


template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

equipment_bp = Blueprint('equipment_bp', __name__, template_folder=template_dir, static_folder=static_dir)

class OpremaForm(FlaskForm):
    inventory_number = StringField("Inventurni broj", validators=[DataRequired()])
    name = StringField("Naziv", validators=[InputRequired()])
    description = StringField("Opis", validators=[DataRequired()])
    serial_number = StringField("Serijski broj", validators=[DataRequired()])
    model_number = StringField("Model broj", validators=[DataRequired()])
    supplier = StringField("Dobavljac", validators=[DataRequired()])
    date_of_acquisition = DateField("Datum nabavke", format='%Y-%m-%d',validators=[DataRequired()])
    warranty_until = DateField("Garancija do", validators=[DataRequired()])
    purchase_value = IntegerField("Nabavna vrijednost", validators=[DataRequired(), NumberRange(min=1)])
    project = StringField("Projekat", validators=[DataRequired()])
    service_period = StringField("Servisni period", validators=[DataRequired()])
    next_service = DateField("Naredni servis", validators=[DataRequired()])
    labaratory_assistant = StringField("Sredstvo duzi", validators=[DataRequired()])
    location = StringField("Lokacija", validators=[DataRequired()])
    available = SelectField("Dostupno", choices=[('1', 'Da'),('0', 'Ne')])
    note = StringField("Napomena", validators=[DataRequired()])
    image = FileField("Upload New Image", validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField("Dodaj opremu")


@equipment_bp.route('/download-csv')
def download_csv():
    if 'user' not in session:
        return redirect(url_for('login_bp.login'))

    if session.get('role') not in ['admin', 'laborant']:
        return redirect(url_for('login_bp.dashboard'))

    oprema = Oprema.query.all()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow([
        'inventory_number', 'name', 'description', 'serial_number', 'model_number', 'supplier', 'date_of_acquisition',
        'warranty_until', 'purchase_value', 'project', 'service_period', 'next_service', 'labaratory_assistant',
        'location', 'available', 'note'
        ])
    for item in oprema:
        writer.writerow([item.inventory_number, item.name, item.description, item.serial_number,
        item.model_number, item.supplier, item.date_of_acquisition, item.warranty_until, item.purchase_value,
        item.project, item.service_period, item.next_service, item.labaratory_assistant, item.location,
        item.available, item.note

        ])

    
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') 
    filename = f'oprema_{now}.csv' 

    response = make_response(si.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-type'] = 'text/csv'
    return response


@equipment_bp.route('/browse_equipment')
def browse_equipment():
    search_query = request.args.get('search', '').strip()

    query = Oprema.query

    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(Oprema.name.ilike(search_term))

    equipment_list = query.all()

    return render_template(
        'browse/browse_equipment.html',
        equipment_list=equipment_list,
        search=search_query
    )



@equipment_bp.route('/equipment/<int:equipment_id>')
def equipment_detail(equipment_id):
    equipment = Oprema.query.get_or_404(equipment_id)

    user_role = session.get('role')
    return render_template(
        'browse/equipment_info.html',
        equipment=equipment,
        user_role=user_role
    )


@equipment_bp.route("/dodaj", methods=['GET', 'POST'])
def dodaj_opremu():
    if 'user' not in session:
        return redirect(url_for('login_bp.login'))

    if session.get('role') not in ['admin', 'laborant']:
        return redirect(url_for('login_bp.dashboard'))

    form = OpremaForm()

    # --- RUKOVANJE CSV UPLOADOM ---
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            # Parsiranje CSV-a
            csv_file = csv.reader(file.stream.read().decode('utf-8').splitlines())
            next(csv_file)  # preskoči header

            for row in csv_file:
                if len(row) != 17:
                    continue  # preskoči redove koji nemaju točno 17 stupaca

                # raspakiraj sve vrijednosti
                (inventory_number, name, description, serial_number, model_number, supplier, date_of_acquisition,
                 warranty_until, purchase_value, project, service_period, next_service, labaratory_assistant,
                 location, available, note) = row + [None] * (18 - len(row))  # napomena: moraš uskladiti broj stupaca

                # provjeri postoji li oprema s istim inventory_number ili name (po želji)
                postoji = Oprema.query.filter_by(inventory_number=inventory_number).first()
                if postoji:
                    continue  # preskoči ako već postoji

                novi = Oprema(
                    inventory_number=inventory_number,
                    name=name,
                    description=description,
                    serial_number=serial_number,
                    model_number=model_number,
                    supplier=supplier,
                    date_of_acquisition=date_of_acquisition,
                    warranty_until=warranty_until,
                    purchase_value=purchase_value,
                    project=project,
                    service_period=service_period,
                    next_service=next_service,
                    labaratory_assistant=labaratory_assistant,
                    location=location,
                    available=int(available) if available.isdigit() else 0,
                    note=note
                )
                db.session.add(novi)
            db.session.commit()
            return redirect(url_for('login_bp.dashboard'))

    # --- RUKOVANJE FORMOM ---
    if form.validate_on_submit():
        novi_unos = Oprema(
            inventory_number=form.inventory_number.data,
            name=form.name.data,
            description=form.description.data,
            serial_number=form.serial_number.data,
            model_number=form.model_number.data,
            supplier=form.supplier.data,
            date_of_acquisition=form.date_of_acquisition.data,
            warranty_until=form.warranty_until.data,
            purchase_value=form.purchase_value.data,
            project=form.project.data,
            service_period=form.service_period.data,
            next_service=form.next_service.data,
            labaratory_assistant=form.labaratory_assistant.data,
            location=form.location.data,
            available=form.available.data,
            note=form.note.data,
        )
        db.session.add(novi_unos)

        images = request.files.getlist('images')
        upload_folder = os.path.join(current_app.root_path, 'static', 'equipment_images')
        os.makedirs(upload_folder, exist_ok=True)

        for image in images:
            if image.filename != '':
                filename = secure_filename(image.filename)
                save_path = os.path.join(upload_folder, filename)
                image.save(save_path)

                image_record = equipmentImage(filename=filename, oprema_id=novi_unos.id)
                novi_unos.images.append(image_record)

        db.session.commit()
        return redirect(url_for('login_bp.dashboard'))

    return render_template("dodavanje_opreme.html", form=form)


@equipment_bp.route('/dashboard')
def back_to_dashboard():
    return render_template("dashboard.html")



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@equipment_bp.route('/izmijeni/<int:oprema_id>', methods=['GET', 'POST'])
def izmijeni_opremu(oprema_id):
    if 'user' not in session:
        return redirect(url_for('login_bp.login'))

    if session.get('role') not in ['admin', 'laborant']:
        return redirect(url_for('login_bp.dashboard'))

    oprema = Oprema.query.get_or_404(oprema_id)
    form = OpremaForm(obj=oprema)

    if form.validate_on_submit():
        form.populate_obj(oprema)

        keep_image_ids = request.form.getlist('keep_image_ids')
        keep_image_ids = set(map(int, keep_image_ids)) if keep_image_ids else set()

        for image in list(oprema.images):
            if image.id not in keep_image_ids:
                file_path = os.path.join(current_app.root_path, 'static', 'equipment_images', image.filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                db.session.delete(image)

        images = request.files.getlist('images')
        upload_folder = os.path.join(current_app.root_path, 'static', 'equipment_images')
        os.makedirs(upload_folder, exist_ok=True)

        for image in images:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                save_path = os.path.join(upload_folder, filename)
                image.save(save_path)

                new_img = equipmentImage(filename=filename, oprema_id=oprema.id)
                db.session.add(new_img)

        db.session.commit()
        flash('Equipment updated successfully.', 'success')
        return redirect(url_for('equipment_bp.equipment_detail', equipment_id=oprema.id))

    return render_template("dodavanje_opreme.html", form=form, edit_mode=True, oprema=oprema, images=oprema.images)


@equipment_bp.route('/izbrisi/<int:oprema_id>', methods=['POST'])
def izbrisi_opremu(oprema_id):
    if session.get('role') not in ['admin', 'laborant']:
        return redirect(url_for('login_bp.dashboard'))

    oprema = Oprema.query.get_or_404(oprema_id)

    for image in oprema.images:
        image_path = os.path.join(current_app.root_path, 'static', 'equipment_images', image.filename)
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                print(f"Error deleting image file {image.filename}: {e}")

    db.session.delete(oprema)
    db.session.commit()

    flash('Equipment and associated images have been deleted.', 'success')
    return redirect(url_for('equipment_bp.back_to_dashboard'))
