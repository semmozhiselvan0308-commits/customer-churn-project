import json
import logging
import pandas as pd
from sqlalchemy import create_engine


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


DATABASE_URL = "mysql+pymysql://root:root@localhost/telecom_db"

engine = create_engine(DATABASE_URL)


# 1. Check NULL rate
def check_null_rate(df, col, threshold):
    null_rate = df[col].isnull().mean()

    return {
        "check_name": f"Null rate check - {col}",
        "status": "PASS" if null_rate <= threshold else "FAIL",
        "value": round(null_rate, 4),
        "threshold": threshold
    }


# 2. Check value range
def check_value_range(df, col, min_value, max_value=None):
    if max_value is not None:
        passed = df[col].between(min_value, max_value).all()
        threshold = f"{min_value} - {max_value}"
    else:
        passed = (df[col] > min_value).all()
        threshold = f"> {min_value}"

    return {
        "check_name": f"Value range check - {col}",
        "status": "PASS" if passed else "FAIL",
        "value": f"min={df[col].min()}, max={df[col].max()}",
        "threshold": threshold
    }


# 3. Check allowed values
def check_allowed_values(df, col, allowed_set):
    invalid_count = (~df[col].isin(allowed_set)).sum()

    return {
        "check_name": f"Allowed values check - {col}",
        "status": "PASS" if invalid_count == 0 else "FAIL",
        "value": f"invalid_rows={invalid_count}",
        "threshold": list(allowed_set)
    }


# 4. Check row count
def check_row_count(df, expected_min):
    row_count = len(df)

    return {
        "check_name": "Row count check",
        "status": "PASS" if row_count >= expected_min else "FAIL",
        "value": row_count,
        "threshold": expected_min
    }


# 5. Check duplicate customer IDs
def check_no_duplicates(df, key_col):
    duplicate_count = df[key_col].duplicated().sum()

    return {
        "check_name": f"Duplicate check - {key_col}",
        "status": "PASS" if duplicate_count == 0 else "FAIL",
        "value": f"duplicate_rows={duplicate_count}",
        "threshold": "0 duplicates"
    }


# 6. Check churn distribution
def check_churn_distribution(df):
    churn_rate = (df["churn"] == 1).mean()

    return {
        "check_name": "Churn distribution check",
        "status": "PASS" if 0.05 <= churn_rate <= 0.95 else "FAIL",
        "value": round(churn_rate, 4),
        "threshold": "5% - 95%"
    }


if __name__ == "__main__":

    logger.info("========== DE7 QUALITY CHECK START ==========")

    # Load cleaned data from MySQL
    df = pd.read_sql(
        "SELECT * FROM cleaned_customers",
        engine
    )

    logger.info(
        "Loaded cleaned_customers with %s rows and %s columns",
        df.shape[0],
        df.shape[1]
    )

    results = []

    # 1. NULL checks
    results.append(
        check_null_rate(df, "monthly_charges", 0)
    )

    results.append(
        check_null_rate(df, "tenure", 0)
    )

    # 2. VALUE RANGE checks
    results.append(
        check_value_range(df, "tenure", 0, 100)
    )

    results.append(
        check_value_range(df, "monthly_charges", 0)
    )

    # 3. ALLOWED VALUES check
    results.append(
        check_allowed_values(
            df,
            "contract",
            {"Month-to-month", "One year", "Two year"}
        )
    )

    # 4. ROW COUNT check
    results.append(
        check_row_count(df, 7000)
    )

    # 5. DUPLICATE check
    results.append(
        check_no_duplicates(df, "customer_id")
    )

    # 6. CHURN DISTRIBUTION check
    results.append(
        check_churn_distribution(df)
    )

    # Display results
    logger.info("========== QUALITY CHECK RESULTS ==========")

    for result in results:

        if result["check_name"] in [
            "Null rate check - monthly_charges",
            "Null rate check - tenure",
            "Value range check - tenure",
            "Value range check - monthly_charges",
            "Allowed values check - contract",
            "Row count check",
            "Duplicate check - customer_id"
        ]:
            result["severity"] = "CRITICAL"
        else:
            result["severity"] = "WARNING"

        logger.info(
            "%s | %s | %s | value=%s | threshold=%s",
            result["check_name"],
            result["status"],
            result["severity"],
            result["value"],
            result["threshold"]
        )

    # Create quality report
    with open("quality_report.json", "w") as file:
        json.dump(results, file, indent=4)

    # Stop pipeline if a critical check fails
    critical_failures = [
        result for result in results
        if result["status"] == "FAIL"
        and result["severity"] == "CRITICAL"
    ]

    if critical_failures:
        raise Exception("CRITICAL DATA QUALITY CHECK FAILED - PIPELINE STOPPED")

    logger.info("========== DE7 QUALITY CHECK PASSED ==========")