from pydantic import BaseModel
from typing import List
from sqlalchemy import Column, Integer, Float, String, ARRAY
from sqlalchemy.sql.sqltypes import String as SQLString  # Import String from sqlalchemy.sql.sqltypes
from database import Base

class User(BaseModel):
    name: str
    email: str
    password: str

class UserDB(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

class Loan(BaseModel):
    user_ids: List[str]
    amount: float
    annual_interest_rate: float
    loan_term_months: int

class LoanDB(Base):
    __tablename__ = 'loans'

    id = Column(Integer, primary_key=True, index=True)
    user_ids = Column(String)  # Store user IDs as a string with a delimiter
    amount = Column(Float)
    annual_interest_rate = Column(Float)
    loan_term_months = Column(Integer)