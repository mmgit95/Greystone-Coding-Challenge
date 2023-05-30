from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime
from models import User, Loan, UserDB, LoanDB
from utils import find_loan_by_id, generate_loan_schedule, generate_loan_summary
from database import engine, SessionLocal, Base
from sqlalchemy.orm import Session

app = FastAPI()
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create User
@app.post('/users')
def create_user(user: User, db: Session = Depends(get_db)):
    new_user = UserDB(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Create Loan
@app.post('/loans')
def create_loan(loan: Loan, db: Session = Depends(get_db)):
    new_loan = LoanDB(
        user_ids=loan.user_ids,
        amount=loan.amount,
        annual_interest_rate=loan.annual_interest_rate,
        loan_term_months=loan.loan_term_months
    )
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    return new_loan

# Fetch Loan Schedule
@app.get('/loans/{loan_id}/schedule')
def fetch_loan_schedule(loan_id: str, db: Session = Depends(get_db)):
    loan = find_loan_by_id(loan_id, db)
    if not loan:
        raise HTTPException(status_code=404, detail='Loan not found')
    # Generate loan schedule here
    schedule = generate_loan_schedule(loan)
    return {'loan_id': loan_id, 'schedule': schedule}

# Fetch Loan Summary for Specific Month
@app.get('/loans/{loan_id}/summary/{month}')
def fetch_loan_summary(loan_id: str, month: str, db: Session = Depends(get_db)):
    loan = find_loan_by_id(loan_id, db)
    if not loan:
        raise HTTPException(status_code=404, detail='Loan not found')
    # Generate loan summary for the specific month here
    summary = generate_loan_summary(loan, month)
    return summary

# Fetch All Loans for User
@app.get('/users/{user_id}/loans')
def fetch_user_loans(user_id: str, db: Session = Depends(get_db)):
    user_loans = db.query(LoanDB).filter(LoanDB.user_ids.contains([user_id])).all()
    return {'user_id': user_id, 'loans': user_loans}

# Share Loan with Another User
@app.post('/loans/{loan_id}/share')
def share_loan(loan_id: str, recipient_user_id: str, db: Session = Depends(get_db)):
    loan = find_loan_by_id(loan_id, db)
    if not loan:
        raise HTTPException(status_code=404, detail='Loan not found')
    loan.user_ids.append(recipient_user_id)
    db.commit()
    shared_loan = {
        'loan_id': loan_id,
        'recipient_user_id': recipient_user_id
    }
    return shared_loan