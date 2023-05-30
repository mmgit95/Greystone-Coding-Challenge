from datetime import datetime

from models import Loan, LoanDB
from sqlalchemy.orm import Session

def find_loan_by_id(loan_id: str, db: Session):
    return db.query(LoanDB).filter(LoanDB.id == loan_id).first()

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