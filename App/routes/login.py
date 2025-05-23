from flask import Blueprint, render_template, redirect, url_for, flash, session, get_flashed_messages,request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from App.models.database import db, User
from werkzeug.security import check_password_hash, generate_password_hash
import os
#import hashlib  #part of a code for user image

#def get_gravatar_url(email, size=40):
#    email = email.strip().lower().encode('utf-8')
#    gravatar_hash = hashlib.md5(email).hexdigest()
#    return f"https://www.gravatar.com/avatar/{gravatar_hash}?s={size}&d=identicon"
#______part of a code for user image______

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

login_bp = Blueprint('login_bp', __name__, template_folder=template_dir, static_folder=static_dir)

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
    phone_number = StringField('Phone Number', validators=[
    DataRequired(),
    Regexp(r'^\+?[0-9\s\-]{6,15}$', message="Phone number must contain only digits and may include +, spaces or dashes.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')


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
            session['user'] = user.email
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('login_bp.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
            return render_template('login.html', form=form)


    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'danger')

    return render_template('login.html', form=form)

@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user'):
        flash('You are already logged in.', 'info')
        return redirect(url_for('login_bp.dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        phone_number = form.phone_number.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('login_bp.register'))

        if User.query.filter_by(phone_number=phone_number).first():
            flash('Phone number already exists.', 'danger')
            return redirect(url_for('login_bp.register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('login_bp.register'))

        new_user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=email,
            address=form.address.data,
            city=form.city.data,
            phone_number=phone_number,
            password=generate_password_hash(password),
            role="student"
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login_bp.login'))

    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, 'danger')

    return render_template('register.html', form=form)


@login_bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("You must be logged in to view this page.", 'danger')
        return redirect(url_for('login_bp.login'))
    username = session['user']
    role = session.get('role')
    return render_template('dashboard.html',username=username, role=role)
    #gravatar_url = get_gravatar_url(session.get('user'))
    #return render_template("dashboard.html", gravatar_url=gravatar_url)
    #____part of a code for user image____

@login_bp.route('/logout')
def logout():
    session.pop('user', None)
    get_flashed_messages()
    flash("You have been logged out.", 'info')
    return redirect(url_for('login_bp.login'))

@login_bp.route('/')
def home():
    return redirect(url_for('login_bp.login'))
