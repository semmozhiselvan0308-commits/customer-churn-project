from database import SessionLocal
from models import Customer

session = SessionLocal()

customer = session.query(Customer).first()

if customer:
    print("===== CUSTOMER DETAILS =====")
    print(f"Customer ID      : {customer.customer_id}")
    print(f"Gender           : {customer.gender}")
    print(f"Senior Citizen   : {customer.senior_citizen}")
    print(f"Partner          : {customer.partner}")
    print(f"Dependents       : {customer.dependents}")
else:
    print("Customer not found")

session.close()