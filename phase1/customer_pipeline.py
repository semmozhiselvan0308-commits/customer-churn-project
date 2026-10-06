import os
import logging
from datetime import datetime
import pandas as pd

from customer_cleaner import CustomerCleaner

# -----------------------------------------------------
# Logging Configuration
# -----------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------
# Load Data
# -----------------------------------------------------

def load_data(filepath):
    """
    Reads the CSV file and returns a DataFrame.
    """

    try:
        logger.info("Loading data from %s", filepath)

        df = pd.read_csv(filepath)

        logger.info("Rows Loaded : %d", len(df))

        return df

    except Exception as e:
        logger.error("Error while loading data.")
        logger.exception(e)
        raise


# -----------------------------------------------------
# Feature Engineering
# -----------------------------------------------------

def build_features(df):
    """
    Performs Feature Engineering (CP4)
    """

    try:

        logger.info("Building Features...")

        feature_df = df.copy()

        # -------------------------------------------------
        # 1. Tenure Groups
        # -------------------------------------------------

        feature_df["tenure_group"] = pd.cut(
            feature_df["tenure"],
            bins=[0, 12, 24, 48, 72],
            labels=[
                "0-12 Months",
                "13-24 Months",
                "25-48 Months",
                "49-72 Months"
            ],
            include_lowest=True
        )

        # -------------------------------------------------
        # 2. Average Monthly Spend
        # -------------------------------------------------

        feature_df["avg_monthly_spend"] = (
            feature_df["total_charges"] /
            feature_df["tenure"].replace(0, 1)
        )

        # -------------------------------------------------
        # 3. High Value Customer
        # -------------------------------------------------

        feature_df["high_value_customer"] = (
            feature_df["monthly_charges"] >
            feature_df["monthly_charges"].median()
        ).astype(int)

        # -------------------------------------------------
        # 4. Senior Citizen Flag
        # -------------------------------------------------

        feature_df["senior_flag"] = feature_df["senior_citizen"]

        # -------------------------------------------------
        # 5. Number of Services
        # -------------------------------------------------

        service_columns = [
            "phone_service",
            "multiple_lines",
            "internet_service",
            "online_security",
            "online_backup",
            "device_protection",
            "tech_support",
            "streaming_tv",
            "streaming_movies"
        ]

        def count_services(row):

            count = 0

            for col in service_columns:

                value = str(row[col]).lower()

                if value not in [
                    "no",
                    "no internet service",
                    "no phone service"
                ]:
                    count += 1

            return count

        feature_df["service_count"] = feature_df.apply(
            count_services,
            axis=1
        )

        # -------------------------------------------------
        # 6. Charges Per Service
        # -------------------------------------------------

        feature_df["charge_per_service"] = (
            feature_df["monthly_charges"] /
            feature_df["service_count"].replace(0, 1)
        )

        logger.info("Feature Engineering Completed")

        return feature_df

    except Exception as e:

        logger.error("Feature Engineering Failed")
        logger.exception(e)
        raise


# -----------------------------------------------------
# Save Outputs
# -----------------------------------------------------

def save_outputs(clean_df, feature_df, output_dir):

    try:

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now().strftime("%Y%m%d")

        clean_file = os.path.join(
            output_dir,
            f"cleaned_customer_{timestamp}.csv"
        )

        feature_file = os.path.join(
            output_dir,
            f"customer_features_{timestamp}.csv"
        )

        clean_df.to_csv(clean_file, index=False)

        feature_df.to_csv(feature_file, index=False)

        logger.info("Cleaned Data Saved : %s", clean_file)
        logger.info("Feature Data Saved : %s", feature_file)

    except Exception as e:

        logger.error("Saving Failed")
        logger.exception(e)
        raise


# -----------------------------------------------------
# Data Quality Checks
# -----------------------------------------------------

def data_quality_check(df):

    logger.info("Running Data Quality Checks...")

    assert df["monthly_charges"].isnull().sum() == 0, \
        "monthly_charges contains NULL values."

    assert set(df["churn"].unique()).issubset({0, 1}), \
        "churn contains values other than 0 and 1."

    logger.info("Data Quality Checks Passed")


# -----------------------------------------------------
# Main Pipeline
# -----------------------------------------------------

def main():

    logger.info("=" * 60)
    logger.info("CUSTOMER PIPELINE STARTED")
    logger.info("=" * 60)

    try:

        # Step 1
        df = load_data("Teleco_Customer_Churn.csv")

        # Step 2
        cleaner = CustomerCleaner(df)

        # -------------------------------------------------
        # Replace this with YOUR cleaning method
        # -------------------------------------------------

        clean_df = cleaner.clean_data()

        logger.info("Cleaning Completed")

        # Step 3
        feature_df = build_features(clean_df)

        # Step 4
        data_quality_check(feature_df)

        # Step 5
        save_outputs(
            clean_df,
            feature_df,
            "output"
        )

        logger.info("Pipeline Finished Successfully")

    except Exception as e:

        logger.error("Pipeline Failed")
        logger.exception(e)
        raise


# -----------------------------------------------------
# Entry Point
# -----------------------------------------------------

if __name__ == "__main__":
    main()