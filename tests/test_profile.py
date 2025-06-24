import pytest
from App.routes.profile import profile_bp, EditProfileForm
from App.models.database import User, db
from flask import Flask, session, Blueprint
from werkzeug.security import generate_password_hash
from flask.testing import FlaskClient

@pytest.fixture
def app():
    """Create test app with all required blueprints and routes"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Create mock login blueprint
    login_bp = Blueprint('login_bp', __name__)
    
    @login_bp.route('/login')
    def login():
        return "Mock login page"
    
    @login_bp.route('/dashboard')
    def dashboard():
        return "Mock dashboard"
    
    @login_bp.route('/logout')  # Added this missing route
    def logout():
        return "Mock logout"

    
    # Register all blueprints
    app.register_blueprint(login_bp, url_prefix='/auth')
    app.register_blueprint(profile_bp)
    
    db.init_app(app)
    with app.app_context():
        db.create_all()
    
    yield app

@pytest.fixture 
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create test user"""
    with app.app_context():
        user = User(
            email='test@example.com',
            name='Test',
            surname='User',
            address='123 Test St',
            city='Testville',
            phone_number='123-456-7890',
            password=generate_password_hash('password'),
            role='student',
            verified=True
        )
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()

def test_edit_profile_form_validation(app):
    """Test form validation"""
    with app.app_context():
        form = EditProfileForm(
            name='Valid',
            surname='Valid',
            address='Valid',
            city='Valid',
            phone_number='123'
        )
        assert form.validate()
        
        form = EditProfileForm(
            address='a'*101,
            city='a'*51,
            phone_number='a'*21
        )
        assert not form.validate()

def test_edit_profile_unauthorized(client):
    """Test unauthorized access redirects"""
    response = client.get('/edit_profile', follow_redirects=False)
    assert response.status_code == 302
    # Check if redirecting to login
    assert '/auth/login' in response.location

def test_edit_profile_get(client, test_user):
    """Test profile page access"""
    with client:
        with client.session_transaction() as sess:
            sess['user'] = test_user.email
        
        response = client.get('/edit_profile')
        assert response.status_code == 200
        assert test_user.email.encode() in response.data

def test_edit_profile_post(client, test_user):
    """Test profile updates"""
    with client:
        with client.session_transaction() as sess:
            sess['user'] = test_user.email
        
        new_data = {
            'name': test_user.name,
            'surname': test_user.surname,
            'address': 'New Address',
            'city': 'New City',
            'phone_number': '987-654-3210',
            'submit': 'Save'
        }
        
        response = client.post('/edit_profile', data=new_data)
        assert response.status_code == 302
        
        # Verify updates
        with client.application.app_context():
            updated = db.session.get(User, test_user.id)
            assert updated.address == 'New Address'
            assert updated.city == 'New City'

def test_edit_profile_name_restrictions(client, test_user):
    """Test name/surname can't be changed"""
    with client:
        with client.session_transaction() as sess:
            sess['user'] = test_user.email
        
        original_name = test_user.name
        original_surname = test_user.surname
        
        response = client.post('/edit_profile', data={
            'name': 'Changed',
            'surname': 'Changed',
            'address': test_user.address,
            'city': test_user.city,
            'phone_number': test_user.phone_number,
            'submit': 'Save'
        })
        
        with client.application.app_context():
            updated = db.session.get(User, test_user.id)
            assert updated.name == original_name
            assert updated.surname == original_surname

def test_edit_profile_with_none_values(client, app):
    """Test name/surname can be changed when None"""
    with app.app_context():
        user = User(
            email='none@example.com',
            name='None',
            surname='None',
            address='123 Test',
            city='Testville',
            phone_number='123',
            password=generate_password_hash('pass'),
            role='student',
            verified=True
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    
    with client:
        with client.session_transaction() as sess:
            sess['user'] = 'none@example.com'
        
        response = client.post('/edit_profile', data={
            'name': 'NewName',
            'surname': 'NewSurname',
            'address': '123 Test',
            'city': 'Testville',
            'phone_number': '123',
            'submit': 'Save'
        })
        
        assert response.status_code == 302
        
        # Verify changes
        with app.app_context():
            updated = db.session.get(User, user_id)
            assert updated.name == 'NewName'
            assert updated.surname == 'NewSurname'
            db.session.delete(updated)
            db.session.commit()