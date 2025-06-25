from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import (
    StringField, IntegerField, SubmitField, TextAreaField,
    SelectField, DateTimeField, DecimalField
)
from wtforms.validators import DataRequired, Optional
from datetime import datetime
import os
from flask_mail import Message
from App import mail
from App.models.database import db, Oprema, Rented, User

# Define paths for templates and static files
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')
static_dir = os.path.join(current_dir, 'static')

# Define the Blueprint
rented_bp = Blueprint('rented_bp', __name__, template_folder=template_dir, static_folder=static_dir)

# Rental Form Definition
class RentedForm(FlaskForm):
    # --- Renters' user-related info ---
    issued_by_name = StringField("Issuer Name", default="")
    approver_name = SelectField("Approver Name", choices=[], validators=[DataRequired()])
    renter_name = StringField("Renter Name", default="")
    renter_telephone = StringField("Renter Phone", default="")
    renter_address = StringField("Renter Address", default="")

    # --- Oprema (equipment) related fields ---
    inventory_number = StringField("Inventory Number", validators=[DataRequired()])
    name = StringField("Equipment Name", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])
    serial_number = StringField("Serial Number", validators=[DataRequired()])
    model_number = StringField("Model Number", validators=[DataRequired()])
    supplier = StringField("Supplier", validators=[DataRequired()])
    date_of_acquisition = DateTimeField("Date of Acquisition", format="%Y-%m-%d", validators=[DataRequired()])
    warranty_until = DateTimeField("Warranty Until", format="%Y-%m-%d", validators=[DataRequired()])
    purchase_value = DecimalField("Purchase Value (BAM)", places=2, validators=[DataRequired()])
    service_period = StringField("Service Period", validators=[DataRequired()])
    next_service = DateTimeField("Next Service Date", format="%Y-%m-%d", validators=[DataRequired()])
    available = IntegerField("Available", validators=[Optional()])
    note = TextAreaField("Note Equipment", validators=[Optional()])

    # --- Other rental-related fields ---
    date_rent_start = DateTimeField("Rental Start Date", format="%Y-%m-%d %H:%M:%S", validators=[Optional()])
    date_rent_end = DateTimeField("Rental End Date", format="%Y-%m-%d %H:%M:%S", validators=[Optional()])

    project = StringField("Project", validators=[Optional()])
    subject = StringField("Subject", validators=[Optional()])
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
    note_rent = TextAreaField("Note Rent", validators=[Optional()])

    submit = SubmitField("Submit")


#WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING
#WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING
#placeholderi kao "professor" za roll i "Lab" za ime laboranta se moraju promjeniti u zavrsnoj aplikaciji
#WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING
#WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING
@rented_bp.route('/rent/<inv_num>', methods=['GET', 'POST'])
def rent(inv_num):
    if 'user' not in session:
        return redirect(url_for('login_bp.login'))

    form = RentedForm()

    # Only allow specific fields to be edited
    fields_to_unlock = ['approver_name', 'project', 'subject', 'note_rent', 'submit']
    for field_name, field in form._fields.items():
        if field_name not in fields_to_unlock:
            field.render_kw = field.render_kw or {}
            field.render_kw['readonly'] = True

    # Get all professors and use ID as value, name as label
    professors = User.query.filter(User.role.ilike('professor')).all()
    form.approver_name.choices = [(str(prof.id), f"{prof.name} {prof.surname}") for prof in professors]

    # Load equipment
    equipment = Oprema.query.filter_by(inventory_number=inv_num).first()
    if not equipment:
        flash(f"Equipment with inventory number {inv_num} not found.", "danger")
        return redirect(url_for('login_bp.dashboard'))

    # Get current user as renter
    current_user = db.session.query(User).filter_by(email=session['user']).first()


    # Get the one and only laborant as issuer
    issuer = User.query.filter(User.role.ilike('laborant')).first()

    if request.method == 'GET':
        # Equipment fields
        form.inventory_number.data = equipment.inventory_number
        form.name.data = equipment.name
        form.description.data = equipment.description
        form.serial_number.data = equipment.serial_number
        form.model_number.data = equipment.model_number
        form.supplier.data = equipment.supplier
        form.date_of_acquisition.data = equipment.date_of_acquisition
        form.warranty_until.data = equipment.warranty_until
        form.purchase_value.data = equipment.purchase_value
        form.service_period.data = equipment.service_period
        form.next_service.data = equipment.next_service
        form.available.data = equipment.available

        if current_user:
            form.renter_name.data = f"{current_user.name} {current_user.surname}"
            form.renter_telephone.data = current_user.phone_number
            form.renter_address.data = current_user.address

        # Show issuer's name for display only
        if issuer:
            form.issued_by_name.data = f"{issuer.name} {issuer.surname}"

    error_message = None

    if form.validate_on_submit():
        # Use IDs directly
        renter_id = current_user.id if current_user else None
        approver_id = int(form.approver_name.data)  # selected professor's ID
        issuer_id = issuer.id if issuer else None
        equipment_id = equipment.id if equipment else None

        approver = User.query.get(approver_id)

        # Validate roles
        if not current_user:
            error_message = 'Renter not found (session issue).'
        elif not approver:
            error_message = 'Approver not found.'
        elif approver.role.lower() != 'professor':
            error_message = 'Approver must have the role "professor".'
        elif not issuer:
            error_message = 'Issuer (laborant) not found.'
        elif issuer.role.lower() != 'laborant':
            error_message = 'Issuer must have the role "laborant".'
        elif not equipment:
            error_message = 'Equipment not found.'
        else:
            rented_item = Rented(
                renter_id=renter_id,
                approver_id=approver_id,
                issued_by_id=issuer_id,
                inventory_number_id=equipment_id,
                start_date=form.date_rent_start.data,
                end_date=form.date_rent_end.data,
                project=form.project.data,
                subject=form.subject.data,
                status=form.status.data,
                note=form.note_rent.data
            )
            db.session.add(rented_item)
            db.session.commit()

            student_name = f"{current_user.name} {current_user.surname}"
            equipment_name = equipment.name
            prof_email = approver.email

            project = form.project.data
            subject = form.subject.data
            note = form.note_rent.data

            msg = Message(
                subject="Zahtjev za odobrenje iznajmljivanja opreme",
                recipients=[prof_email]
            )

            msg.body = (
                f"Poštovani/na {approver.name} {approver.surname},\n\n"
                f"Student {student_name} je zatražio odobrenje za iznajmljivanje opreme: \"{equipment_name}\".\n\n"
                f"Detalji zahtjeva:\n"
                f"• Projekat: {project}\n"
                f"• Predmet: {subject}\n"
                f"• Napomena: {note}\n\n"
                f"Molimo Vas da pristupite sistemu kako biste odobrili ili odbili zahtjev.\n\n"
                "Hvala."
            )
            mail.send(msg)

            return redirect(url_for('login_bp.dashboard'))

    else:
        print("Form did NOT validate rent")
        print(form.errors)  

    return render_template('rent.html', form=form, error_message=error_message)




#shows all "requests" aka rents in the browser
@rented_bp.route('/request_browse', methods=['GET'])
def req_browse():
    if 'user' not in session:
        return redirect(url_for('login_bp.login'))

    current_user = User.query.filter_by(email=session['user']).first()

    # Dohvati filter iz URL-a (npr. ?status=pending) ili podesi na 'pending' ako nema
    status_filter = request.args.get('status', 'pending').lower()

    # Bazni query – svi zahtjevi u kojima učestvuje trenutni korisnik
    base_query = Rented.query.filter(
        (Rented.renter_id == current_user.id) |
        (Rented.approver_id == current_user.id) |
        (Rented.issued_by_id == current_user.id)
    )

    # Broj zahtjeva po statusima
    count_all = base_query.count()
    count_pending = base_query.filter(Rented.status.ilike('pending')).count()
    count_approved = base_query.filter(Rented.status.ilike('approved')).count()
    count_ended = base_query.filter(Rented.status.ilike('ended')).count()

    # Primijeni filtriranje po statusu ako je odabrano
    if status_filter in ['pending', 'approved', 'ended']:
        query = base_query.filter(Rented.status.ilike(status_filter))
    elif status_filter == 'all':
        query = base_query
    else:
        query = base_query.filter(Rented.status.ilike('pending'))  # fallback ako neko ručno upiše nepostojeći status

    rented_raw = query.all()

    # Priprema liste za prikaz u šablonu
    rented_list = []
    for rent in rented_raw:
        renter = User.query.get(rent.renter_id)
        approver = User.query.get(rent.approver_id)
        equipment = Oprema.query.get(rent.inventory_number_id)

        rented_list.append({
            'id': rent.id,
            'renter_name': renter.name if renter else 'Unknown',
            'approver_name': approver.name if approver else 'Unknown',
            'equipment_name': equipment.name if equipment else 'Unknown',
            'inventory_number': equipment.inventory_number if equipment else 'N/A',
            'status': rent.status
        })

    return render_template(
        'request_browse.html',
        rented_list=rented_list,
        current_filter=status_filter,
        count_all=count_all,
        count_pending=count_pending,
        count_approved=count_approved,
        count_ended=count_ended
    )


#and finaly it takes the rent_id (primary key) after you selected a "request" in the above section and shows it in detail
@rented_bp.route('/request/<rented_id>', methods=['GET', 'POST'])
def request_view(rented_id):
    if 'user' not in session:
        return redirect(url_for('login_bp.login'))

    form = RentedForm()
    rented = Rented.query.get_or_404(rented_id)
    equipment = Oprema.query.get(rented.inventory_number_id)
    issuer = User.query.get(rented.issued_by_id)
    approver = User.query.get(rented.approver_id)
    renter = User.query.get(rented.renter_id)

    current_user = User.query.filter_by(email=session['user']).first()
    professors = User.query.filter(User.role.ilike('professor')).all()
    form.approver_name.choices = [(str(prof.id), f"{prof.name} {prof.surname}") for prof in professors]

    fields_to_unlock = ['status', 'submit']
    for field_name, field in form._fields.items():
        if field_name not in fields_to_unlock:
            field.render_kw = field.render_kw or {}
            field.render_kw['readonly'] = True

    if request.method == 'GET':
        form.inventory_number.data = equipment.inventory_number or ''
        form.name.data = equipment.name or ''
        form.description.data = equipment.description or ''
        form.serial_number.data = equipment.serial_number or ''
        form.model_number.data = equipment.model_number or ''
        form.supplier.data = equipment.supplier or ''
        form.date_of_acquisition.data = equipment.date_of_acquisition
        form.warranty_until.data = equipment.warranty_until
        form.purchase_value.data = equipment.purchase_value
        form.service_period.data = equipment.service_period or ''
        form.next_service.data = equipment.next_service
        form.available.data = equipment.available if equipment.available is not None else 0
        form.note.data = equipment.note or ''

        form.date_rent_start.data = rented.start_date
        form.date_rent_end.data = rented.end_date
        form.project.data = rented.project or ''
        form.subject.data = rented.subject or ''
        form.status.data = rented.status or 'pending'
        form.note_rent.data = rented.note or ''

        form.issued_by_name.data = f"{issuer.name} {issuer.surname}" if issuer else 'Lab'
        form.renter_name.data = f"{renter.name} {renter.surname}" if renter else ''
        form.renter_telephone.data = renter.phone_number or ''
        form.renter_address.data = renter.address or ''
        form.approver_name.data = str(approver.id) if approver else ''

    if form.validate_on_submit():
        if current_user and (
            current_user.id == approver.id or 
            (current_user.role and current_user.role.lower() == 'admin')
        ):
            prev_status = (rented.status or '').strip().lower()
            new_status = (form.status.data or '').strip().lower()

            if prev_status == 'pending' and new_status == 'approved':
                rented.status = 'Approved'
                rented.start_date = datetime.utcnow()
                if equipment and equipment.available > 0:
                    equipment.available -= 1  # reduce available count by one
            
            elif prev_status == 'pending' and new_status == 'rejected':
                if equipment:
                    equipment.available += 1  # increment available count by one to return it
                db.session.delete(rented)
                db.session.commit()
                return redirect(url_for('login_bp.dashboard'))
            
            elif prev_status == 'approved' and new_status == 'ended':
                rented.status = 'Ended'
                rented.end_date = datetime.utcnow()
                if equipment:
                    equipment.available += 1  # increment available count by one to return it


            db.session.commit()
            return redirect(url_for('rented_bp.req_browse'))
        else:
            flash("Niste ovlašteni da izvršite ovu akciju.", "danger")
            return redirect(url_for('rented_bp.req_browse'))
    else:
        if request.method == 'POST':
            print("Form did NOT validate request")
            print(form.errors)

    return render_template('request.html', form=form, user_role=session.get('role'))