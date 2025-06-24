import pytest
import sys
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from App import create_app, db
from App.models.database import User

# --- Fixtures ---
@pytest.fixture(scope='session')
def app():
    """Application fixture with proper testing config"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'MAIL_SUPPRESS_SEND': True
    })
    
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()

@pytest.fixture
def client(app):
    """Test client fixture"""
    return app.test_client()

@pytest.fixture
def init_db(app):
    """Database fixture with test data"""
    with app.app_context():
        # Clean slate
        db.drop_all()
        db.create_all()
        
        # Create test users
        test_users = [
            {
                'email': 'admin@fet.ba',
                'password': generate_password_hash('admin123'),
                'role': 'admin',
                'verified': True,
                'name': 'Admin',
                'surname': 'User',
                'address': 'Admin Street 1',
                'city': 'AdminCity',
                'phone_number': '111-111'
            },
            {
                'email': 'laborant@fet.ba',
                'password': generate_password_hash('laborant123'),
                'role': 'laborant',
                'verified': True,
                'name': 'Lab',
                'surname': 'Tech',
                'address': 'Lab Street 2',
                'city': 'LabCity',
                'phone_number': '222-222'
            },
            {
                'email': 'student@fet.ba',
                'password': generate_password_hash('student123'),
                'role': 'student',
                'verified': True,
                'name': 'Student',
                'surname': 'One',
                'address': 'Student Ave 3',
                'city': 'StudentCity',
                'phone_number': '333-333'
            }
        ]
        
        for user_data in test_users:
            user = User(**user_data)
            db.session.add(user)
        
        db.session.commit()
        
        yield db
        
        # Cleanup
        db.session.remove()
        db.drop_all()
        if hasattr(db, 'engine'):
            db.engine.dispose()

# --- Test Cases ---

def test_predefined_users_exist(client, init_db):
    """Test that predefined users exist"""
    with client.application.app_context():
        admin = User.query.filter_by(email='admin@fet.ba').first()
        laborant = User.query.filter_by(email='laborant@fet.ba').first()
        student = User.query.filter_by(email='student@fet.ba').first()
        
        assert admin is not None
        assert laborant is not None
        assert student is not None
        assert admin.role == 'admin'
        assert laborant.role == 'laborant'
        assert student.role == 'student'
        assert admin.verified is True
        assert laborant.verified is True
        assert student.verified is True

def test_admin_login(client, init_db):
    """Test admin login"""
    response = client.post('/login', data={
        'email': 'admin@fet.ba',
        'password': 'admin123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Check for redirect to dashboard
    assert b'Dashboard' in response.data or b'dashboard' in response.data.lower()
    with client.session_transaction() as session:
        assert session.get('user') == 'admin@fet.ba'
        assert session.get('role') == 'admin'

def test_laborant_login(client, init_db):
    """Test laborant login"""
    response = client.post('/login', data={
        'email': 'laborant@fet.ba',
        'password': 'laborant123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Check for redirect to dashboard
    assert b'Dashboard' in response.data or b'dashboard' in response.data.lower()
    with client.session_transaction() as session:
        assert session.get('user') == 'laborant@fet.ba'
        assert session.get('role') == 'laborant'

def test_student_login(client, init_db):
    """Test student login"""
    response = client.post('/login', data={
        'email': 'student@fet.ba',
        'password': 'student123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Check for redirect to dashboard
    assert b'Dashboard' in response.data or b'dashboard' in response.data.lower()
    with client.session_transaction() as session:
        assert session.get('user') == 'student@fet.ba'
        assert session.get('role') == 'student'

def test_login_with_wrong_password(client, init_db):
    """Test login with incorrect password"""
    response = client.post('/login', data={
        'email': 'admin@fet.ba',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'invalid email or password' in response.data.lower()
    with client.session_transaction() as session:
        assert session.get('user') is None
        assert session.get('role') is None

def test_login_nonexistent_user(client, init_db):
    """Test login with non-existent email"""
    response = client.post('/login', data={
        'email': 'nonexistent@fet.ba',
        'password': 'anypassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'invalid email or password' in response.data.lower()
    with client.session_transaction() as session:
        assert session.get('user') is None
        assert session.get('role') is None

def test_logout(client, init_db):
    """Test logout functionality"""
    # First login
    client.post('/login', data={
        'email': 'admin@fet.ba',
        'password': 'admin123'
    })
    
    # Verify session before logout
    with client.session_transaction() as pre_session:
        print("PRE-LOGOUT SESSION:", pre_session)
        assert pre_session.get('user') == 'admin@fet.ba'
        assert pre_session.get('role') == 'admin'
    
    # Perform logout
    response = client.get('/logout', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'login' in response.data.lower()
    
    # Verify session after logout
    with client.session_transaction() as post_session:
        print("POST-LOGOUT SESSION:", post_session)
        assert 'user' not in post_session
        assert 'role' not in post_session
        # We can be more specific about what should remain if needed


def test_unverified_user_login(client, init_db):
    """Test login with unverified account"""
    # Add an unverified user
    with client.application.app_context():
        unverified_user = User(
            email='unverified@fet.ba',
            password=generate_password_hash('test123'),
            role='student',
            verified=False,
            name='Test',
            surname='User',
            address='123 Test St',
            city='Testville',
            phone_number='444-444'
        )
        db.session.add(unverified_user)
        db.session.commit()
    
    response = client.post('/login', data={
        'email': 'unverified@fet.ba',
        'password': 'test123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'please verify your email before logging in' in response.data.lower()
    with client.session_transaction() as session:
        assert session.get('user') is None
        assert session.get('role') is None


def test_successful_registration(client, init_db):
    """Test new user registration flow"""
    response = client.post('/register', data={
        'name': 'Test',
        'surname': 'Student',
        'email': 'newstudent@fet.ba',
        'address': '456 Uni Road',
        'city': 'Campus City',
        'phone_number': '555-1234',
        'password': 'newpass123',
        'confirm_password': 'newpass123',
        'agree': 'on'

    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'registration successful' in response.data.lower()

    # Verify DB record
    with client.application.app_context():
        user = User.query.filter_by(email='newstudent@fet.ba').first()
        assert user is not None
        assert user.verified is False  # Should require email verification
        assert user.role == 'student'  # Default role

def test_registration_existing_email(client, init_db):
    """Test duplicate email rejection"""
    response = client.post('/register', data={
        'name': 'Duplicate',
        'surname': 'User',
        'email': 'admin@fet.ba',  # Already exists in test DB
        'address': '123 Fake St',
        'city': 'Testville',
        'phone_number': '555-5555',
        'password': 'mypassword',
        'confirm_password': 'mypassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'email already exists' in response.data.lower()