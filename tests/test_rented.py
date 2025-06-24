import pytest
import datetime
import os
import sys
from flask import url_for
from werkzeug.security import generate_password_hash

#root putanja
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from App import create_app, db
from App.models.database import User, Oprema, Rented

#Flask aplikacija za testiranje
@pytest.fixture(scope='module')
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:1234@localhost:5432/rentalab_test'
    app.config['MAIL_SUPPRESS_SEND'] = True

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

#Test client
@pytest.fixture
def client(app):
    return app.test_client()

#Priprema korisnika i opreme (ciscnje + dodavanje)
@pytest.fixture
def setup_rent_data(app):
    with app.app_context():
        db.session.query(Rented).delete()
        db.session.query(Oprema).delete()
        db.session.query(User).delete()
        db.session.commit()

        admin = User(email="admin@fet.ba", name="Admin", surname="One", address="Admin St", city="AdminCity",
                     phone_number="000", password=generate_password_hash("admin123"), role="admin", verified=True)
        lab = User(email="lab@fet.ba", name="Lab", surname="Tech", address="Lab St", city="LabCity",
                   phone_number="111", password=generate_password_hash("lab123"), role="laborant", verified=True)
        student = User(email="student@fet.ba", name="Stu", surname="Dent", address="Stu St", city="StuCity",
                       phone_number="222", password=generate_password_hash("student123"), role="student", verified=True)
        prof = User(email="prof@fet.ba", name="Prof", surname="Essor", address="Prof St", city="ProfCity",
                    phone_number="333", password=generate_password_hash("prof123"), role="professor", verified=True)
        db.session.add_all([admin, lab, student, prof])

        oprema = Oprema(
            inventory_number="INV-123",
            name="Multimeter",
            description="Digital multimeter",
            serial_number="SER-123",
            model_number="MOD-123",
            supplier="SupplierX",
            date_of_acquisition=datetime.date.today(),
            warranty_until=datetime.date.today() + datetime.timedelta(days=365),
            purchase_value=100,
            project="Test",
            service_period="12m",
            next_service=datetime.date.today() + datetime.timedelta(days=180),
            labaratory_assistant="Lab Tech",
            location="Room 1",
            available=1,
            note="Test item"
        )
        db.session.add(oprema)
        db.session.commit()

        yield {
            'admin': admin,
            'lab': lab,
            'student': student,
            'prof': prof,
            'oprema': oprema
        }

#Prijavljen student
@pytest.fixture
def student_client(client, setup_rent_data):
    with client.session_transaction() as sess:
        sess['user'] = setup_rent_data['student'].email
    return client

#Prijavljen admin
@pytest.fixture
def admin_client(client, setup_rent_data):
    with client.session_transaction() as sess:
        sess['user'] = setup_rent_data['admin'].email
    return client

#TESTOVI

def test_rent_page_access_redirect(client):
    response = client.get("/rent/INV-123", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_rent_page_get(student_client, setup_rent_data):
    response = student_client.get(f"/rent/{setup_rent_data['oprema'].inventory_number}")
    assert response.status_code == 200
    assert b"Rental" in response.data or b"Submit" in response.data

def test_post_rent_success(student_client, setup_rent_data, app):
    with app.app_context():
        equipment = setup_rent_data['oprema']
        prof = setup_rent_data['prof']

        response = student_client.post(
            f"/rent/{equipment.inventory_number}",
            data={
                'approver_name': str(prof.id),
                'project': 'Test Project',
                'subject': 'Physics',
                'note_rent': 'Please approve.',
                'inventory_number': equipment.inventory_number,
                'name': equipment.name,
                'description': equipment.description,
                'serial_number': equipment.serial_number,
                'model_number': equipment.model_number,
                'supplier': equipment.supplier,
                'date_of_acquisition': str(equipment.date_of_acquisition),
                'warranty_until': str(equipment.warranty_until),
                'purchase_value': str(equipment.purchase_value),
                'service_period': equipment.service_period,
                'next_service': str(equipment.next_service),
                'available': str(equipment.available),
                'submit': 'Submit'
            },
            follow_redirects=True
        )

        assert response.status_code == 200

        rent_record = Rented.query.filter_by(project='Test Project').first()
        assert rent_record is not None


def test_request_browse_view(admin_client, app):
    response = admin_client.get("/request_browse")
    assert response.status_code == 200
    assert b"Equipment" in response.data or b"Pending" in response.data

def test_request_detail_redirect_if_not_logged_in(client):
    response = client.get("/request/1")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
