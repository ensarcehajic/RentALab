from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length
from App.models.database import db, Korisnik
from werkzeug.security import check_password_hash
import os

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

login_bp = Blueprint('login_bp', __name__, template_folder=template_dir, static_folder=static_dir)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=50)])

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
      
        korisnik = Korisnik.query.filter_by(username=username).first()
        
        if korisnik and check_password_hash(korisnik.password, password):
            session['user'] = korisnik.username
            flash('Login successful!', 'success')
            return redirect(url_for('login_bp.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@login_bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("You must be logged in to view this page.", 'danger')
        return redirect(url_for('login_bp.login'))
    username = session['user']
    return f"<h1>Welcome to the Dashboard, {username}!</h1>"

@login_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", 'info')
    return redirect(url_for('login_bp.login'))

@login_bp.route('/')
def home():
    return redirect(url_for('login_bp.login'))
