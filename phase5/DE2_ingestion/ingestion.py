import os
import pandas as pd
import mysql.connector


LANDING_DIR = "DE1_architecture/data/landing"

EXPECTED_COLUMNS = [
    "customerID",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
    "Churn"
]


def detect_files():
    files = []

    for filename in os.listdir(LANDING_DIR):
        if filename.endswith(".csv"):
            files.append(os.path.join(LANDING_DIR, filename))

    return files


def validate_schema(filepath):
    df = pd.read_csv(filepath)
    return df.columns.tolist() == EXPECTED_COLUMNS


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="telecom_db"
    )


def load_to_staging(filepath):
    df = pd.read_csv(filepath)

    conn = get_connection()
    cursor = conn.cursor()

    columns = ", ".join(EXPECTED_COLUMNS)
    placeholders = ", ".join(["%s"] * len(EXPECTED_COLUMNS))

    query = f"""
        INSERT INTO stg_customer_raw ({columns})
        VALUES ({placeholders})
    """

    for _, row in df.iterrows():
        cursor.execute(query, tuple(row))

    conn.commit()

    cursor.close()
    conn.close()

    return len(df)


def log_ingestion(filename, row_count, status):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO ingestion_log
        (filename, row_count, load_time, status)
        VALUES (%s, %s, NOW(), %s)
    """

    cursor.execute(query, (filename, row_count, status))

    conn.commit()

    cursor.close()
    conn.close()


def already_processed(filename):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT COUNT(*)
        FROM ingestion_log
        WHERE filename = %s
        AND status = 'SUCCESS'
    """

    cursor.execute(query, (filename,))
    count = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return count > 0

if __name__ == "__main__":

    files = detect_files()

    print("Files detected:")
    print(files)

    for file in files:

        filename = os.path.basename(file)

        if already_processed(filename):
            print(f"File already processed. Skipping: {filename}")
            continue

        if validate_schema(file):

            print(f"Schema validation passed: {file}")

            rows = load_to_staging(file)

            print(f"Loaded {rows} rows into stg_customer_raw")

            log_ingestion(filename, rows, "SUCCESS")

            print("Ingestion logged successfully.")

        else:

            print(f"Schema validation failed: {file}")

            log_ingestion(filename, 0, "FAILED")

            print("Failed ingestion logged.")