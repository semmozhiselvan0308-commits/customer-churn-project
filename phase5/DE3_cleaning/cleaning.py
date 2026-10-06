import sys
import os
import logging

# Allow Python to find the phase2 folder
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
)

from sqlalchemy import text
from phase2.database import engine


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def clean_staging(engine):
    """
    Clean data from stg_customer_raw and create cleaned_customers.
    """

    logger.info("Starting DE3 cleaning process...")

    with engine.begin() as conn:

        # ---------------------------------------------------------
        # 1. Create cleaned_customers
        # ---------------------------------------------------------
        logger.info("Creating cleaned_customers table...")

        conn.execute(text("""
            DROP TABLE IF EXISTS cleaned_customers
        """))

        conn.execute(text("""
    CREATE TABLE cleaned_customers AS
    SELECT
        customerID AS customer_id,
        gender,
        SeniorCitizen AS senior_citizen,
        CASE
            WHEN Partner = 'Yes' THEN 1
            WHEN Partner = 'No' THEN 0
            ELSE NULL
        END AS partner,
        CASE
            WHEN Dependents = 'Yes' THEN 1
            WHEN Dependents = 'No' THEN 0
            ELSE NULL
        END AS dependents,
        tenure,
        CASE
            WHEN PhoneService = 'Yes' THEN 1
            WHEN PhoneService = 'No' THEN 0
            ELSE NULL
        END AS phone_service,
        MultipleLines AS multiple_lines,
        InternetService AS internet_service,
        CASE
            WHEN OnlineSecurity = 'Yes' THEN 1
            WHEN OnlineSecurity = 'No' THEN 0
            ELSE NULL
        END AS online_security,
        CASE
            WHEN OnlineBackup = 'Yes' THEN 1
            WHEN OnlineBackup = 'No' THEN 0
            ELSE NULL
        END AS online_backup,
        CASE
            WHEN DeviceProtection = 'Yes' THEN 1
            WHEN DeviceProtection = 'No' THEN 0
            ELSE NULL
        END AS device_protection,
        CASE
            WHEN TechSupport = 'Yes' THEN 1
            WHEN TechSupport = 'No' THEN 0
            ELSE NULL
        END AS tech_support,
        CASE
            WHEN StreamingTV = 'Yes' THEN 1
            WHEN StreamingTV = 'No' THEN 0
            ELSE NULL
        END AS streaming_tv,
        CASE
            WHEN StreamingMovies = 'Yes' THEN 1
            WHEN StreamingMovies = 'No' THEN 0
            ELSE NULL
        END AS streaming_movies,
        Contract AS contract,
        CASE
            WHEN PaperlessBilling = 'Yes' THEN 1
            WHEN PaperlessBilling = 'No' THEN 0
            ELSE NULL
        END AS paperless_billing,
        PaymentMethod AS payment_method,
        MonthlyCharges AS monthly_charges,
        CASE
            WHEN TRIM(TotalCharges) = '' THEN NULL
            ELSE CAST(TotalCharges AS DECIMAL(10,2))
        END AS total_charges,
        CASE
            WHEN Churn = 'Yes' THEN 1
            WHEN Churn = 'No' THEN 0
            ELSE NULL
        END AS churn
    FROM stg_customer_raw
"""))
        logger.info("cleaned_customers created successfully.")

        # ---------------------------------------------------------
        # 2. Row count check
        # ---------------------------------------------------------
        result = conn.execute(text("""
            SELECT COUNT(*) FROM cleaned_customers
        """))

        row_count = result.scalar()

        logger.info(
            "cleaned_customers row count: %s",
            row_count
        )

        # ---------------------------------------------------------
        # 3. customer_id NULL check
        # ---------------------------------------------------------
        result = conn.execute(text("""
            SELECT COUNT(*)
            FROM cleaned_customers
            WHERE customer_id IS NULL
        """))

        customer_id_nulls = result.scalar()

        # ---------------------------------------------------------
        # 4. monthly_charges NULL check
        # ---------------------------------------------------------
        result = conn.execute(text("""
            SELECT COUNT(*)
            FROM cleaned_customers
            WHERE monthly_charges IS NULL
        """))

        monthly_charges_nulls = result.scalar()

        # ---------------------------------------------------------
        # 5. churn validation
        # ---------------------------------------------------------
        result = conn.execute(text("""
            SELECT COUNT(*)
            FROM cleaned_customers
            WHERE churn NOT IN (0, 1)
               OR churn IS NULL
        """))

        invalid_churn = result.scalar()

        # ---------------------------------------------------------
        # 6. Quality report
        # ---------------------------------------------------------
        logger.info("========== DATA QUALITY REPORT ==========")

        if row_count > 0:
            logger.info("PASS - cleaned_customers contains rows")
        else:
            logger.error("FAIL - cleaned_customers is empty")

        if customer_id_nulls == 0:
            logger.info("PASS - customer_id NULL check")
        else:
            logger.error(
                "FAIL - customer_id NULL count: %s",
                customer_id_nulls
            )

        if monthly_charges_nulls == 0:
            logger.info("PASS - monthly_charges NULL check")
        else:
            logger.error(
                "FAIL - monthly_charges NULL count: %s",
                monthly_charges_nulls
            )

        if invalid_churn == 0:
            logger.info("PASS - churn contains only 0/1")
        else:
            logger.error(
                "FAIL - invalid churn values: %s",
                invalid_churn
            )

        logger.info("=========================================")


def build_curated_tables(engine):
    """
    Build the four existing Phase 2 curated tables from
    cleaned_customers.

    Existing tables:
        dim_contract
        dim_payment
        customers
        fact_customer_account
    """

    logger.info("Starting curated table build...")

    with engine.begin() as conn:

        # =========================================================
        # 1. DIM_CONTRACT
        # =========================================================

        logger.info("Populating dim_contract...")

        conn.execute(text("""
            INSERT INTO dim_contract (contract_name)
            SELECT DISTINCT contract
            FROM cleaned_customers
            WHERE contract IS NOT NULL
              AND contract <> ''
            ON DUPLICATE KEY UPDATE
                contract_name = VALUES(contract_name)
        """))

        logger.info("dim_contract populated.")

        # =========================================================
        # 2. DIM_PAYMENT
        # =========================================================

        logger.info("Populating dim_payment...")

        conn.execute(text("""
            INSERT INTO dim_payment (payment_name)
            SELECT DISTINCT payment_method
            FROM cleaned_customers
            WHERE payment_method IS NOT NULL
              AND payment_method <> ''
            ON DUPLICATE KEY UPDATE
                payment_name = VALUES(payment_name)
        """))

        logger.info("dim_payment populated.")

        # =========================================================
        # 3. CUSTOMERS
        # =========================================================

        logger.info("Populating customers...")

        conn.execute(text("""
            INSERT INTO customers (
                customer_id,
                customer_name,
                age,
                city,
                calls_made,
                telecom_partner
            )
            SELECT
                customer_id,
                NULL,
                NULL,
                NULL,
                NULL,
                NULL
            FROM cleaned_customers
            WHERE customer_id IS NOT NULL
            ON DUPLICATE KEY UPDATE
                customer_id = VALUES(customer_id)
        """))

        logger.info("customers populated.")

        # =========================================================
        # 4. FACT_CUSTOMER_ACCOUNT
        # =========================================================

        logger.info("Populating fact_customer_account...")

        conn.execute(text("""
    INSERT INTO fact_customer_account (
        customer_id,
        contract_id,
        payment_id,
        tenure,
        monthly_charges,
        total_charges,
        churn,
        internet_service
    )
    SELECT
        c.customer_id,
        dc.contract_id,
        dp.payment_id,
        c.tenure,
        c.monthly_charges,
        c.total_charges,
        c.churn,
        c.internet_service
    FROM cleaned_customers c

    LEFT JOIN dim_contract dc
        ON dc.contract_name = c.contract

    LEFT JOIN dim_payment dp
        ON dp.payment_name = c.payment_method

    WHERE c.customer_id IS NOT NULL

      AND NOT EXISTS (
          SELECT 1
          FROM fact_customer_account f
          WHERE f.customer_id = c.customer_id
      )
"""))

        logger.info("fact_customer_account populated.")

        logger.info("Curated table build completed successfully.")


def verify_curated_tables(engine):
    """
    Verify all four curated tables.
    """

    logger.info("========== CURATED TABLE VERIFICATION ==========")

    with engine.connect() as conn:

        tables = [
            "dim_contract",
            "dim_payment",
            "customers",
            "fact_customer_account"
        ]

        for table in tables:

            result = conn.execute(
                text(f"SELECT COUNT(*) FROM {table}")
            )

            count = result.scalar()

            logger.info(
                "%s row count: %s",
                table,
                count
            )

            if count > 0:
                logger.info(
                    "PASS - %s contains data",
                    table
                )
            else:
                logger.error(
                    "FAIL - %s is empty",
                    table
                )

    logger.info("================================================")


if __name__ == "__main__":

    logger.info("========== DE3 START ==========")

    # Step 1
    clean_staging(engine)

    # Step 2
    build_curated_tables(engine)

    # Step 3
    verify_curated_tables(engine)

    logger.info("=========== DE3 END ===========")