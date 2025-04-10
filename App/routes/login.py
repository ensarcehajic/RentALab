from flask import Flask, render_template, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length

app = Flask(__name__, template_folder="../templates")
app.secret_key = "4f6sb28f0sb9q83khs"

class LoginForm(FlaskForm):
      username = StringField('Username', validators=[DataRequired(),Length(min=4, max= 20)])
      password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=50)])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username == 'admin' and password == 'admin':
            session['user']=username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)



@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
         flash("You must be logged in to view this page.",'danger')
         return redirect(url_for('login'))
    return "<h1>Welcome to the Dashboard!</h1>"

@app.route('/logout')
def logout():
     session.pop('user', None)
     flash("You have been logged out.",'info')
     return redirect(url_for('login')) 


if __name__ == "__main__":
        app.run(debug = True);