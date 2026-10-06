import sys
from pathlib import Path

import pandas as pd
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "phase2"))

from database import SessionLocal


csv_path = (
    PROJECT_ROOT
    / "phase5"
    / "DE1_architecture"
    / "data"
    / "landing"
    / "Teleco_Customer_Churn.csv"
)


session = SessionLocal()

try:

    df = pd.read_csv(csv_path)

    for _, row in df.iterrows():

        customer_id = str(row["customerID"]).strip()
        tenure = int(row["tenure"])

        session.execute(
            text("""
                UPDATE customers_churn
                SET tenure = :tenure
                WHERE customer_id = :customer_id
            """),
            {
                "customer_id": customer_id,
                "tenure": tenure
            }
        )

    session.commit()

    print("Tenure values populated successfully.")

except Exception as e:

    session.rollback()
    print("ERROR:", e)

finally:

    session.close()