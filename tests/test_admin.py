import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import patch
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
from App.models.database import db, User

# --------------------------
# Fixtures
# --------------------------

@pytest.fixture(scope='module')
def app():
    """Application fixture with test configuration"""
    from App import create_app
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'MAIL_SUPPRESS_SEND': True
    })
    
    ctx = app.app_context()
    ctx.push()
    
    yield app
    
    ctx.pop()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_client(client):
    with client.session_transaction() as sess:
        sess['user'] = 'admin@fet.ba'
    return client

# --------------------------
# Tests
# --------------------------

def test_add_staff_form_validation(app):
    """Test form validation rules"""
    from App.routes.admin import AddStaffForm
    
    with app.test_request_context():
        valid_form = AddStaffForm(
            email="valid@fet.ba",
            password="validpassword",
            role="professor"
        )
        assert valid_form.validate()
        
        invalid_form = AddStaffForm(
            email="invalid@gmail.com",
            password="validpassword",
            role="professor"
        )
        assert not invalid_form.validate()

def test_add_staff_route_access(admin_client, client):
    """Test route access control"""
    # Admin can access
    response = admin_client.get(url_for('admin_bp.add_staff'))
    assert response.status_code == 200
    
    # Non-admin gets redirected (clear session first)
    with client.session_transaction() as sess:
        sess.clear()
    response = client.get(url_for('admin_bp.add_staff'), follow_redirects=False)
    assert response.status_code == 302
    assert url_for('login_bp.dashboard') in response.location

@patch('App.routes.admin.mail.send')
@patch('App.routes.admin.generate_confirmation_token', return_value='mock-token')
def test_add_staff_success(mock_token, mock_mail, admin_client, app):
    """Test successful staff creation"""
    with app.app_context():
        User.query.delete()
        db.session.commit()
        
        response = admin_client.post(
            url_for('admin_bp.add_staff'),
            data={
                'email': 'newstaff@fet.ba',
                'password': 'TempPass123',
                'role': 'laborant'
            },
            follow_redirects=True
        )
        
        assert b'User successfully added' in response.data
        user = User.query.filter_by(email='newstaff@fet.ba').first()
        assert user is not None
        assert user.name == 'None'  # Default values from admin.py
        assert user.surname == 'None'

def test_add_staff_duplicate_email(admin_client, app):
    """Test duplicate email handling"""
    with app.app_context():
        # Create complete test user first
        user = User(
            email='existing@fet.ba',
            password=generate_password_hash('password123'),
            name='Test',
            surname='User',
            address='Test Address',
            city='Test City',
            phone_number='123-456',
            role='professor',
            verified=False
        )
        db.session.add(user)
        db.session.commit()
        
        response = admin_client.post(
            url_for('admin_bp.add_staff'),
            data={
                'email': 'existing@fet.ba',
                'password': 'newpassword',
                'role': 'laborant'
            },
            follow_redirects=True
        )
        
        assert b'already exists' in response.data

def test_add_staff_invalid_form_data(admin_client):
    """Test form error handling"""
    response = admin_client.post(
        url_for('admin_bp.add_staff'),
        data={
            'email': 'invalid-email',
            'password': 'short',
            'role': ''
        },
        follow_redirects=True
    )
    
    assert b'Invalid email' in response.data or b'This field is required' in response.data