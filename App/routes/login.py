from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email,Regexp
from App.models.database import db, User
from werkzeug.security import check_password_hash, generate_password_hash
import os

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

login_bp = Blueprint('login_bp', __name__, template_folder=template_dir, static_folder=static_dir)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=50)])

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Regexp(r'^[\w\.-]+@fet\.ba$', message="Email must be in @fet.ba domain.")
    ])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if (session.get('user')):
        return redirect(url_for('login_bp.logout'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user'] = user.username
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('login_bp.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.', 'danger')
            return redirect(url_for('login_bp.register'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already exists.', 'danger')
            return redirect(url_for('login_bp.register'))

        new_user = User(
            email=email,
            username=username,
            password=generate_password_hash(password),
            role="student"
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login_bp.login'))

    return render_template('register.html', form=form)



@login_bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("You must be logged in to view this page.", 'danger')
        return redirect(url_for('login_bp.login'))
    username = session['user']
    role = session.get('role')
    return render_template('dashboard.html',username=username, role=role)

@login_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", 'info')
    return redirect(url_for('login_bp.login'))

@login_bp.route('/')
def home():
    return redirect(url_for('login_bp.login'))
