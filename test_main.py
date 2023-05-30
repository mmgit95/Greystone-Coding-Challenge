from fastapi.testclient import TestClient
from main import app, get_db
from database import Base, engine
from sqlalchemy.orm import Session

client = TestClient(app)

def override_get_db():
    try:
        db = Session(engine)
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def setup_module(module):
    Base.metadata.create_all(bind=engine)

def teardown_module(module):
    Base.metadata.drop_all(bind=engine)

def test_create_user():
    user_data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'password': 'password123'
    }
    response = client.post('/users', json=user_data)
    assert response.status_code == 200
    assert response.json()['name'] == user_data['name']
    assert response.json()['email'] == user_data['email']

def test_create_loan():
    loan_data = {
        'user_ids': ['1'],
        'amount': 10000,
        'annual_interest_rate': 5.0,
        'loan_term_months': 12
    }
    response = client.post('/loans', json=loan_data)
    assert response.status_code == 200
    assert response.json()['user_ids'] == loan_data['user_ids']
    assert response.json()['amount'] == loan_data['amount']

def test_fetch_loan_schedule():
    loan_id = '1'
    response = client.get(f'/loans/{loan_id}/schedule')
    assert response.status_code == 200
    assert response.json()['loan_id'] == loan_id
    assert len(response.json()['schedule']) == 12

def test_fetch_loan_summary():
    loan_id = '1'
    month = '2023-01'
    response = client.get(f'/loans/{loan_id}/summary/{month}')
    assert response.status_code == 200
    assert response.json()['loan_id'] == loan_id
    assert response.json()['month'] == month

def test_fetch_user_loans():
    user_id = '1'
    response = client.get(f'/users/{user_id}/loans')
    assert response.status_code == 200
    assert response.json()['user_id'] == user_id

def test_share_loan():
    loan_id = '1'
    recipient_user_id = '2'
    response = client.post(f'/loans/{loan_id}/share', json={'recipient_user_id': recipient_user_id})
    assert response.status_code == 200
    assert response.json()['loan_id'] == loan_id
    assert response.json()['recipient_user_id'] == recipient_user_id