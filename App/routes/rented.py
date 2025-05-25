from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import (
    StringField, IntegerField, SubmitField, TextAreaField,
    SelectField, DateTimeField, DecimalField
)
from wtforms.validators import DataRequired, Optional
from datetime import datetime
import os

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
    issued_by_name = StringField("Issuer Name", default="Lab")
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
    available = IntegerField("Available", validators=[DataRequired()])
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

#Route for renting equipment that will be put in the database
@rented_bp.route('/rent/<inv_num>', methods=['GET', 'POST'])
def rent(inv_num):
    if 'user' not in session:
        return redirect(url_for('login_bp.login'))

    form = RentedForm()

    #ensuring only specific fileds can be changed and not everything
    fields_to_unlock = ['approver_name', 'project', 'subject', 'note_rent', 'submit']
    
    for field_name, field in form._fields.items():
        if field_name not in fields_to_unlock:
            field.render_kw = field.render_kw or {}
            field.render_kw['readonly'] = True

    # Populate approver_name choices with professors
    professors = User.query.filter(User.role.ilike('professor')).all()
    form.approver_name.choices = [(prof.name, prof.name) for prof in professors]

    # Load equipment by inventory number from URL param
    equipment = Oprema.query.filter_by(inventory_number=inv_num).first()

    if not equipment:
        # If equipment not found, redirect or show error
        flash(f"Equipment with inventory number {inv_num} not found.", "danger")
        return redirect(url_for('login_bp.dashboard'))  # Replace with actual browsing route

    # Autofill equipment fields on GET
    if request.method == 'GET':
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

        # Autofill renter info from session user
        current_user = User.query.filter(User.name.ilike(session['user'])).first()
        if current_user:
            form.renter_name.data = current_user.name
            form.renter_telephone.data = current_user.phone_number  # Adjust field names if needed
            form.renter_address.data = current_user.address

    error_message = None

    #validate and test every posibility then if everything is correct add it to the DB
    if form.validate_on_submit():
        renter = User.query.filter(User.name.ilike(form.renter_name.data.strip())).first()
        approver = User.query.filter(User.name.ilike(form.approver_name.data.strip())).first()
        issuer = User.query.filter(User.name.ilike(form.issued_by_name.data.strip())).first()

        # Confirm equipment again from inventory_number in form (security check)
        equipment = Oprema.query.filter_by(inventory_number=form.inventory_number.data).first()

        if not renter:
            error_message = 'Renter name does not exist.'
        elif not approver:
            error_message = 'Approver name does not exist.'
        elif approver.role.lower() != 'professor':
            error_message = 'Approver must have the role "professor".'
        elif not issuer:
            error_message = 'Issuer name does not exist.'
        elif issuer.role.lower() != 'laborant':
            error_message = 'Issuer must have the role "laborant".'
        elif not equipment:
            error_message = 'Equipment inventory number does not exist.'
        else:
            rented_item = Rented(
                renter_id=renter.id,
                approver_id=approver.id,
                issued_by_id=issuer.id,
                inventory_number_id=equipment.id,
                start_date=form.date_rent_start.data,
                end_date=form.date_rent_end.data,
                project=form.project.data,
                subject=form.subject.data,
                status=form.status.data,
                note=form.note_rent.data
            )
            db.session.add(rented_item)
            db.session.commit()
            return redirect(url_for('login_bp.dashboard'))
    else:
        #for testing and just in case it breaks in the future
        print("Form did NOT validate rent")
        print(form.errors)  # This will show which fields caused validation errors
    return render_template('rent.html', form=form, error_message=error_message)


#shows all "requests" aka rents in the browser
@rented_bp.route('/request_browse', methods=['GET', 'POST'])
def req_browse():
    rented_raw = Rented.query.all()

    #creating the fileds for renting
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

    return render_template('request_browse.html', rented_list=rented_list)


#and finaly it takes the rent_id (primary key) after you selected a "request" in the above section and shows it in detail
@rented_bp.route('/request/<rented_id>', methods=['GET', 'POST'])
def request_view(rented_id):
    if 'user' not in session:
        return redirect(url_for('login_bp.login'))

    form = RentedForm()

    # Fetch the rented row by id, or 404 if not found
    rented = Rented.query.get_or_404(rented_id)

    # Fetch related equipment using the foreign key
    equipment = Oprema.query.get(rented.inventory_number_id)

    # Fetch users related to this rental (issuer, approver, renter)
    issuer = User.query.get(rented.issued_by_id)
    approver = User.query.get(rented.approver_id)
    renter = User.query.get(rented.renter_id)

    current_user = User.query.filter_by(name=session['user']).first()

    # By default, lock all fields except status and submit
    fields_to_unlock = ['status', 'submit']

    # If current user is NOT the approver or an admin, lock everything including status and disable submit button
    if not current_user or (current_user.id != approver.id and current_user.role.lower() != 'admin'):
        # Lock all fields
        for field_name, field in form._fields.items():
            field.render_kw = field.render_kw or {}
            field.render_kw['readonly'] = True
            # Disable submit button (if it exists)
            if field_name == 'submit':
                field.render_kw['disabled'] = True
    else:
        # User is approver or admin — unlock status and submit only
        for field_name, field in form._fields.items():
            if field_name not in fields_to_unlock:
                field.render_kw = field.render_kw or {}
                field.render_kw['readonly'] = True
    
    #had a POST bug for the approver_name so had to do it here otherwise takes the data and fills out everything
    form.approver_name.choices = [(approver.name, approver.name)]
    
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
    
        form.issued_by_name.data = issuer.name or 'Lab'
        #form.approver_name.choices = [(approver.name, approver.name)] DONE ABOVE CUZ POST ERROR
        form.renter_name.data = renter.name or ''
        form.renter_telephone.data = renter.phone_number or ''
        form.renter_address.data = renter.address or ''
 
    #validate and logic for the status button in order to ensure things run smothly
    if form.validate_on_submit():
        prev_status = rented.status.strip().lower()
        new_status = form.status.data.strip().lower()
        
        # Status logic:
        if prev_status == 'pending' and new_status == 'approved':
            rented.status = 'Approved'
            rented.start_date = datetime.utcnow()
        
        elif prev_status == 'pending' and new_status == 'rejected':
            db.session.delete(rented)
            db.session.commit()
            return redirect(url_for('login_bp.dashboard'))
        
        elif prev_status == 'approved' and new_status == 'ended':
            rented.status = 'Ended'
            rented.end_date = datetime.utcnow()

    
        db.session.commit()
        return redirect(url_for('rented_bp.req_browse'))
    else:
        print("Form did NOT validate request")
        print(form.errors)  # This will show which fields caused validation errors
    return render_template('request.html', form=form)


