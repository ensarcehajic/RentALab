from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from App.models.database import db, User

profile_bp = Blueprint('profile_bp', __name__, template_folder='../templates', static_folder='../static')

class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=50)])
    surname = StringField('Surname', validators=[Length(max=50)])
    address = StringField('Address', validators=[Length(max=100)])
    city = StringField('City', validators=[Length(max=50)])
    phone_number = StringField('Phone Number', validators=[Length(max=20)])
    submit = SubmitField('Save Changes')

@profile_bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_email = session.get('user')
    if not user_email:
        flash('Please log in first.', 'danger')
        return redirect(url_for('login_bp.login'))

    user = User.query.filter_by(email=user_email).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login_bp.login'))

    form = EditProfileForm(obj=user)

    can_edit_name = (user.name == 'None')
    can_edit_surname = (user.surname == 'None')

    if form.validate_on_submit():
        # Update only if allowed
        if can_edit_name:
            user.name = form.name.data
        if can_edit_surname:
            user.surname = form.surname.data

        user.address = form.address.data
        user.city = form.city.data
        user.phone_number = form.phone_number.data

        db.session.commit()
        flash('Profile successfully updated.', 'success')
        return redirect(url_for('profile_bp.edit_profile'))

    return render_template('edit_profile.html', form=form, email=user.email,
                           can_edit_name=can_edit_name, can_edit_surname=can_edit_surname)
