

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers_churn"

    customer_id = Column(String(20), primary_key=True)
    gender = Column(String(10))
    senior_citizen = Column(Integer)
    partner = Column(Integer)
    dependents = Column(Integer)


'''  what is happening here 
customers_churn
-----------------------------------
customer_id
gender
senior_citizen
partner
dependents

becomes



customer.customer_id
customer.gender
customer.partner
customer.dependents '''