import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
from sqlalchemy import text

# Allow Python to find phase2
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT / "phase2"))

from database import SessionLocal


# CSV file path
csv_path = (
    PROJECT_ROOT
    / "phase5"
    / "DE1_architecture"
    / "data"
    / "landing"
    / "Teleco_Customer_Churn.csv"
)


def incremental_process():

    session = SessionLocal()

    try:
        print("========== DE6 INCREMENTAL PROCESSING ==========")

        # ==========================================
        # 1. READ CSV
        # ==========================================

        print("CSV path:", csv_path)
        print("CSV exists:", csv_path.exists())

        df = pd.read_csv(csv_path)

        print(f"CSV rows loaded: {len(df)}")

        # ==========================================
        # 2. LOAD EXISTING CUSTOMERS ONCE
        # ==========================================

        existing_rows = session.execute(
            text("""
                SELECT
                    customer_id,
                    gender,
                    senior_citizen,
                    partner,
                    dependents,
                    tenure
                FROM customers_churn
            """)
        ).mappings().all()

        existing_customers = {
            row["customer_id"]: row
            for row in existing_rows
        }

        print(f"Existing customers loaded: {len(existing_customers)}")

        # ==========================================
        # 3. COUNTERS
        # ==========================================

        rows_inserted = 0
        rows_updated = 0
        rows_unchanged = 0

        # ==========================================
        # 4. PROCESS CSV CUSTOMERS
        # ==========================================

        for _, row in df.iterrows():

            customer = {
                "customer_id": str(row["customerID"]).strip(),
                "gender": row["gender"],
                "senior_citizen": int(row["SeniorCitizen"]),
                "partner": 1 if row["Partner"] == "Yes" else 0,
                "dependents": 1 if row["Dependents"] == "Yes" else 0,
                "tenure": int(row["tenure"])
            }

            customer_id = customer["customer_id"]

            existing = existing_customers.get(customer_id)

            # ======================================
            # CASE 1: NEW CUSTOMER
            # ======================================

            if existing is None:

                session.execute(
                    text("""
                        INSERT INTO customers_churn
                        (
                            customer_id,
                            gender,
                            senior_citizen,
                            partner,
                            dependents,
                            tenure
                        )
                        VALUES
                        (
                            :customer_id,
                            :gender,
                            :senior_citizen,
                            :partner,
                            :dependents,
                            :tenure
                        )
                    """),
                    customer
                )

                rows_inserted += 1

            # ======================================
            # CASE 2: UPDATED CUSTOMER
            # ======================================

            else:

                changed = (
                    existing["gender"] != customer["gender"]
                    or existing["senior_citizen"] != customer["senior_citizen"]
                    or existing["partner"] != customer["partner"]
                    or existing["dependents"] != customer["dependents"]
                    or existing["tenure"] != customer["tenure"]
                )

                if changed:

                    session.execute(
                        text("""
                            UPDATE customers_churn
                            SET
                                gender = :gender,
                                senior_citizen = :senior_citizen,
                                partner = :partner,
                                dependents = :dependents,
                                tenure = :tenure
                            WHERE customer_id = :customer_id
                        """),
                        customer
                    )

                    rows_updated += 1

                # ==================================
                # CASE 3: UNCHANGED CUSTOMER
                # ==================================

                else:
                    rows_unchanged += 1

        # ==========================================
        # 5. PIPELINE RUN LOG
        # ==========================================

        session.execute(
            text("""
                INSERT INTO pipeline_run_log
                (
                    file_name,
                    rows_inserted,
                    rows_updated,
                    rows_unchanged,
                    run_timestamp
                )
                VALUES
                (
                    :file_name,
                    :rows_inserted,
                    :rows_updated,
                    :rows_unchanged,
                    :run_timestamp
                )
            """),
            {
                "file_name": csv_path.name,
                "rows_inserted": rows_inserted,
                "rows_updated": rows_updated,
                "rows_unchanged": rows_unchanged,
                "run_timestamp": datetime.now()
            }
        )

        # ==========================================
        # 6. COMMIT
        # ==========================================

        session.commit()

        # ==========================================
        # 7. SUMMARY
        # ==========================================

        print("\n========== RUN SUMMARY ==========")
        print(f"Rows inserted  : {rows_inserted}")
        print(f"Rows updated   : {rows_updated}")
        print(f"Rows unchanged : {rows_unchanged}")
        print(f"Run timestamp  : {datetime.now()}")

    except Exception as e:

        session.rollback()

        print("ERROR:", e)

    finally:

        session.close()


if __name__ == "__main__":
    incremental_process()