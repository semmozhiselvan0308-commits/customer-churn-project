import sys
import os
import logging

import pandas as pd
from sqlalchemy import text


# ---------------------------------------------------------
# Find project root and import database.py from phase2
# ---------------------------------------------------------

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

sys.path.append(
    os.path.join(PROJECT_ROOT, "phase2")
)

from database import engine


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Build Features
# ---------------------------------------------------------

def build_features(engine):

    logger.info("========== DE4 START ==========")
    logger.info("Starting feature pipeline...")


    # -----------------------------------------------------
    # 1. Read cleaned customers
    # -----------------------------------------------------

    logger.info("Reading cleaned_customers table...")

    df = pd.read_sql(
        "SELECT * FROM cleaned_customers",
        engine
    )

    logger.info(
        "cleaned_customers loaded successfully. Rows: %s",
        len(df)
    )


    # -----------------------------------------------------
    # 2. Calculate current batch median
    # -----------------------------------------------------

    median_monthly_charges = df["monthly_charges"].median()

    logger.info(
        "Current batch monthly_charges median: %.2f",
        median_monthly_charges
    )


    # -----------------------------------------------------
    # 3. tenure_bucket
    # -----------------------------------------------------

    df["tenure_bucket"] = pd.cut(
        df["tenure"],
        bins=[0, 12, 24, 48, 72],
        labels=[
            "0-12",
            "13-24",
            "25-48",
            "49-72"
        ],
        include_lowest=True
    ).astype(str)

    # -----------------------------------------------------
    # 4. high_charge_flag
    # -----------------------------------------------------

    df["high_charge_flag"] = (
        df["monthly_charges"] > median_monthly_charges
    ).astype(int)


    # -----------------------------------------------------
    # 5. service_count
    # -----------------------------------------------------

    service_columns = [
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies"
]

    df["service_count"] = (
        df[service_columns].sum(axis=1)
    ).astype(int)


    # -----------------------------------------------------
    # 6. is_long_term_customer
    # -----------------------------------------------------

    df["is_long_term_customer"] = (
        df["tenure"] >= 24
    ).astype(int)


    # -----------------------------------------------------
    # 7. has_streaming_bundle
    # -----------------------------------------------------

    df["has_streaming_bundle"] = (
        (df["streaming_tv"] == 1) &
        (df["streaming_movies"] == 1)
    ).astype(int)


    # -----------------------------------------------------
    # 8. auto_pay_flag
    # -----------------------------------------------------

    auto_pay_methods = [
        "Bank transfer (automatic)",
        "Credit card (automatic)"
    ]

    df["auto_pay_flag"] = (
        df["payment_method"].isin(auto_pay_methods)
    ).astype(int)


    # -----------------------------------------------------
    # 9. Select final columns
    # -----------------------------------------------------

    feature_columns = [
        "customer_id",
        "tenure_bucket",
        "high_charge_flag",
        "service_count",
        "is_long_term_customer",
        "has_streaming_bundle",
        "auto_pay_flag"
    ]

    feature_df = df[feature_columns].copy()


    # -----------------------------------------------------
    # 10. Create feature table
    # -----------------------------------------------------

    logger.info(
        "Creating customer_ml_features table..."
    )

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS customer_ml_features (
        customer_id VARCHAR(50) PRIMARY KEY,
        tenure_bucket VARCHAR(20) NOT NULL,
        high_charge_flag INT NOT NULL,
        service_count INT NOT NULL,
        is_long_term_customer INT NOT NULL,
        has_streaming_bundle INT NOT NULL,
        auto_pay_flag INT NOT NULL
    )
    """

    with engine.begin() as connection:
        connection.execute(
            text(create_table_sql)
        )


    # -----------------------------------------------------
    # 11. Remove previous feature data
    # -----------------------------------------------------

    logger.info(
        "Clearing previous feature data..."
    )

    with engine.begin() as connection:
        connection.execute(
            text("DELETE FROM customer_ml_features")
        )


    # -----------------------------------------------------
    # 12. Insert new features
    # -----------------------------------------------------

    logger.info(
        "Writing features to customer_ml_features..."
    )

    feature_df.to_sql(
        "customer_ml_features",
        engine,
        if_exists="append",
        index=False
    )

    logger.info(
        "customer_ml_features populated. Rows: %s",
        len(feature_df)
    )


    # -----------------------------------------------------
    # 13. Row count validation
    # -----------------------------------------------------

    with engine.connect() as connection:

        cleaned_count = connection.execute(
            text(
                "SELECT COUNT(*) FROM cleaned_customers"
            )
        ).scalar()

        feature_count = connection.execute(
            text(
                "SELECT COUNT(*) FROM customer_ml_features"
            )
        ).scalar()


    logger.info(
        "cleaned_customers count: %s",
        cleaned_count
    )

    logger.info(
        "customer_ml_features count: %s",
        feature_count
    )


    if cleaned_count != feature_count:
        raise ValueError(
            "Row count validation failed."
        )

    logger.info(
        "Row count validation passed."
    )


    # -----------------------------------------------------
    # 14. NULL validation
    # -----------------------------------------------------

    feature_only_columns = [
        "tenure_bucket",
        "high_charge_flag",
        "service_count",
        "is_long_term_customer",
        "has_streaming_bundle",
        "auto_pay_flag"
    ]

    null_counts = feature_df[
        feature_only_columns
    ].isnull().sum()


    if null_counts.sum() > 0:

        logger.error(
            "NULL values found:\n%s",
            null_counts
        )

        raise ValueError(
            "NULL validation failed."
        )

    logger.info(
        "Schema / NULL validation passed."
    )

    logger.info(
        "========== DE4 COMPLETE =========="
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":
    build_features(engine)