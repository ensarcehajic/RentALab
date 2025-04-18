from flask import Flask
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '4f6sb28f0sb9q83khs'

    from .routes.login import login_bp
    app.register_blueprint(login_bp)

    csrf.init_app(app)
    return app
