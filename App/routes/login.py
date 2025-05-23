from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from App.models.database import db, User
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message
from App.token_utils import generate_confirmation_token, confirm_token
from App import mail

login_bp = Blueprint('login_bp', __name__, template_folder='../templates', static_folder='../static')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Regexp(r'^[\w\.-]+@fet\.ba$', message="Email must be in @fet.ba domain.")
    ])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=50)])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    surname = StringField('Surname', validators=[DataRequired()])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Regexp(r'^[\w\.-]+@fet\.ba$', message="Email must be in @fet.ba domain.")
    ])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

# --- Routes ---

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user'):
        flash('You are already logged in.', 'info')
        return redirect(url_for('login_bp.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if not user.verified:
                flash('Please verify your email before logging in.', 'warning')
                return redirect(url_for('login_bp.login'))
            session['user'] = user.email
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('login_bp.dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html', form=form)

@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        name = form.name.data
        surname = form.surname.data
        address = form.address.data
        city = form.city.data
        phone_number = form.phone_number.data
        password = form.password.data

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists.', 'danger')
            return redirect(url_for('login_bp.register'))

        new_user = User(
            name=name,
            surname=surname,
            email=email,
            address=address,
            city=city,
            phone_number=phone_number,
            password=generate_password_hash(password),
            role="student",
            verified=False
        )
        db.session.add(new_user)
        db.session.commit()

        # Send verification email
        token = generate_confirmation_token(email)
        verify_link = url_for('login_bp.verify_email', token=token, _external=True)
        msg = Message("Confirm your email", recipients=[email])
        msg.html = render_template("verification.html", verify_link=verify_link)
        mail.send(msg)

        flash('Registration successful. Please check your email to verify your account.', 'info')
        return redirect(url_for('login_bp.login'))

    return render_template('register.html', form=form)

@login_bp.route('/verify/<token>')
def verify_email(token):
    email = confirm_token(token)
    if not email:
        flash("Invalid or expired verification link.", 'danger')
        return redirect(url_for('login_bp.login'))

    user = User.query.filter_by(email=email).first()
    if user:
        user.verified = True
        db.session.commit()
        flash("Your email has been verified. You can now log in.", "success")
    else:
        flash("User not found.", "danger")

    return redirect(url_for('login_bp.login'))

@login_bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("You must be logged in to view this page.", 'danger')
        return redirect(url_for('login_bp.login'))
    username = session['user']
    role = session.get('role')
    return render_template('dashboard.html', username=username, role=role)

@login_bp.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    flash("You have been logged out.", 'info')
    return redirect(url_for('login_bp.login'))

@login_bp.route('/')
def home():
    return redirect(url_for('login_bp.login'))