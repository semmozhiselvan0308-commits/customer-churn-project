import pandas as pd
import numpy as np
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class CustomerCleaner:

    def __init__(self, df):
        self.df = df.copy()
        logger.info("CustomerCleaner initialized with DataFrame shape: %s", self.df.shape)

    # Standardize column names
    def standardize_column_names(self):

        self.df.columns = (
            self.df.columns
            .str.replace(r'([a-z])([A-Z])', r'\1_\2', regex=True)
            .str.lower()
        )

        logger.info("Column names standardized to snake_case")
        return self

    # Fix total_charges
    def fix_total_charges(self):

        try:
            affected_rows = (
                self.df["total_charges"]
                .astype(str)
                .str.strip()
                .eq("")
                .sum()
            )

            self.df["total_charges"] = self.df["total_charges"].replace(
                r"^\s*$",
                np.nan,
                regex=True
            )

            self.df["total_charges"] = pd.to_numeric(
                self.df["total_charges"],
                errors="coerce"
            )

            logger.info(
                "total_charges converted to float. Rows affected: %s",
                affected_rows
            )

        except Exception as e:
            logger.error("Error while fixing total_charges: %s", str(e))

        return self

    # Normalize binary columns
    def normalize_binary_columns(self):

        binary_columns = [
            "partner",
            "dependents",
            "phone_service",
            "paperless_billing",
            "churn",
            "online_security",
            "online_backup",
            "device_protection",
            "tech_support",
            "streaming_tv",
            "streaming_movies"
        ]

        mapping = {
            "Yes": 1,
            "No": 0,
            "No internet service": 0
        }

        for col in binary_columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].replace(mapping)

        logger.info("Binary columns normalized")
        return self

    # Handle null values
    def handle_nulls(self):

        null_count = self.df["total_charges"].isna().sum()

        self.df["total_charges"] = self.df["total_charges"].fillna(
            self.df["monthly_charges"]
        )

        logger.info(
            "Filled %s null values in total_charges using monthly_charges",
            null_count
        )

        return self

    # Cleaning pipeline
    def clean_data(self):

        logger.info("Starting cleaning pipeline")

        self.standardize_column_names()
        self.fix_total_charges()
        self.normalize_binary_columns()
        self.handle_nulls()

        logger.info("Cleaning pipeline completed")

        return self.df