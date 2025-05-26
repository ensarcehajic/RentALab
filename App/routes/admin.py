from flask import Blueprint, render_template, redirect, url_for, flash, session, request,get_flashed_messages
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from werkzeug.security import generate_password_hash
from App.models.database import db, User
from App.token_utils import generate_confirmation_token, confirm_token
from App import mail
from flask_mail import Message
admin_bp = Blueprint('admin_bp',__name__, template_folder='../templates', static_folder='../static')


class AddStaffForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Temporary Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', choices=[('professor', 'Professor'), ('laborant', 'Lab Assistant')], validators=[DataRequired()])
    submit = SubmitField('Add User')

    def validate_email(self, field):
        if not field.data.endswith('@fet.ba'):
            raise ValidationError('Email must be under the @fet.ba domain.')


@admin_bp.route('/add_staff', methods=['GET', 'POST'])
def add_staff():
    if session.get('user') != 'admin@fet.ba':
        flash('Access denied.', 'danger')
        return redirect(url_for('login_bp.dashboard'))

    form = AddStaffForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        role = form.role.data

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('A user with this email already exists.', 'warning')
            return render_template('add_staff.html', form=form)

        hashed_password = generate_password_hash(password)

        new_user = User(
            email=email,
            password=hashed_password,
            name='None',
            surname='None',
            address='None',
            city='None',
            phone_number='None',
            role=role,
            verified=False
        )

        db.session.add(new_user)
        db.session.commit()

        # Slanje verifikacionog emaila
        token = generate_confirmation_token(email)
        verify_link = url_for('login_bp.verify_email', token=token, _external=True)
        msg = Message("Confirm your email", recipients=[email])
        msg.html = render_template("verification.html", verify_link=verify_link)
        mail.send(msg)

        # Slanje emaila za reset lozinke
        token = generate_confirmation_token(email)
        reset_link = url_for('login_bp.reset_password', token=token, _external=True)
        msg = Message("Reset your password", recipients=[email])
        msg.html = render_template("reset_email.html", reset_link=reset_link)
        mail.send(msg)


        flash('User successfully added. Emails for verification and password reset have been sent.', 'success')
        return redirect(url_for('admin_bp.add_staff'))
    
   
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'danger')

    return render_template('add_staff.html', form=form)
