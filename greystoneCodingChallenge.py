from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class User(BaseModel):
    name: str
    email: str
    password: str

class Loan(BaseModel):
    user_ids: list[str]
    amount: float
    annual_interest_rate: float
    loan_term_months: int

users = []
loans = []

# Create User
@app.post('/users')
def create_user(user: User):
    new_user = {
        'id': str(len(users) + 1),
        'name': user.name,
        'email': user.email
    }
    users.append(new_user)
    return new_user

# Create Loan
@app.post('/loans')
def create_loan(loan: Loan):
    new_loan = {
        'id': str(len(loans) + 1),
        'user_ids': loan.user_ids,
        'amount': loan.amount,
        'annual_interest_rate': loan.annual_interest_rate,
        'loan_term_months': loan.loan_term_months
    }
    loans.append(new_loan)
    return new_loan

# Fetch Loan Schedule
@app.get('/loans/{loan_id}/schedule')
def fetch_loan_schedule(loan_id: str):
    loan = find_loan_by_id(loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail='Loan not found')
    # Generate loan schedule here
    schedule = generate_loan_schedule(loan)
    return {'loan_id': loan_id, 'schedule': schedule}

# Fetch Loan Summary for Specific Month
@app.get('/loans/{loan_id}/summary/{month}')
def fetch_loan_summary(loan_id: str, month: str):
    loan = find_loan_by_id(loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail='Loan not found')
    # Generate loan summary for the specific month here
    summary = generate_loan_summary(loan, month)
    return summary

# Fetch All Loans for User
@app.get('/users/{user_id}/loans')
def fetch_user_loans(user_id: str):
    user_loans = [loan for loan in loans if user_id in loan['user_ids']]
    return {'user_id': user_id, 'loans': user_loans}

# Share Loan with Another User
@app.post('/loans/{loan_id}/share')
def share_loan(loan_id: str, recipient_user_id: str):
    loan = find_loan_by_id(loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail='Loan not found')
    loan['user_ids'].append(recipient_user_id)
    shared_loan = {
        'loan_id': loan_id,
        'recipient_user_id': recipient_user_id
    }
    return shared_loan

# Utility functions
def find_loan_by_id(loan_id):
    for loan in loans:
        if loan['id'] == loan_id:
            return loan
    return None

def generate_loan_schedule(loan):
    monthly_interest_rate = loan['annual_interest_rate'] / 12
    loan_term_months = loan['loan_term_months']

    # Calculate the fixed monthly payment
    monthly_payment = (loan['amount'] * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -loan_term_months)

    schedule = []
    remaining_balance = loan['amount']

    for month in range(1, loan_term_months + 1):
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment

        schedule.append({
            'Month': month,
            'Payment': monthly_payment,
            'Principal': principal_payment,
            'Interest': interest_payment,
            'Balance': remaining_balance
        })

    return schedule

def generate_loan_summary(loan, month):
    principal_paid = 0
    interest_paid = 0
    remaining_balance = loan['amount']
    month_date = datetime.strptime(month, '%Y-%m')

    # Iterate over loan schedule and calculate principal and interest paid
    for payment in generate_loan_schedule(loan):
        payment_date = datetime.strptime(payment['payment_date'], '%Y-%m-%d')
        if payment_date <= month_date:
            principal_paid += payment['Principal']
            interest_paid += payment['Interest']
            remaining_balance = payment['Balance']

    loan_summary = {
        'loan_id': loan['id'],
        'month': month,
        'current_balance': remaining_balance,
        'principal_paid': principal_paid,
        'interest_paid': interest_paid
    }

    return loan_summary