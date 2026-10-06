import sys
import os
import pandas as pd

# Find phase2/database.py
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.append(
    os.path.join(PROJECT_ROOT, "phase2")
)

from database import engine


print("========== ML1 START ==========")

# -------------------------------------------------
# 1. Load cleaned customer data
# -------------------------------------------------

df = pd.read_sql(
    "SELECT * FROM cleaned_customers",
    engine
)

print("Loaded cleaned_customers:", df.shape)


# -------------------------------------------------
# 2. Create engineered features
# -------------------------------------------------

median_monthly_charges = df["monthly_charges"].median()

df["high_charge_flag"] = (
    df["monthly_charges"] > median_monthly_charges
).astype(int)

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

df["is_long_term_customer"] = (
    df["tenure"] >= 24
).astype(int)

df["has_streaming_bundle"] = (
    (df["streaming_tv"] == 1) &
    (df["streaming_movies"] == 1)
).astype(int)

auto_pay_methods = [
    "Bank transfer (automatic)",
    "Credit card (automatic)"
]

df["auto_pay_flag"] = (
    df["payment_method"].isin(auto_pay_methods)
).astype(int)


# -------------------------------------------------
# 3. Select ML columns
# -------------------------------------------------

feature_columns = [
    "customer_id",
    "tenure",
    "monthly_charges",
    "total_charges",
    "service_count",
    "high_charge_flag",
    "is_long_term_customer",
    "auto_pay_flag",
    "has_streaming_bundle",
    "contract",
    "internet_service",
    "churn"
]

ml_df = df[feature_columns].copy()


# -------------------------------------------------
# 4. Target
# -------------------------------------------------

y = ml_df["churn"]


# -------------------------------------------------
# 5. Remove ID and target from features
# -------------------------------------------------

X = ml_df.drop(
    columns=["customer_id", "churn"]
)


# -------------------------------------------------
# 6. One-hot encoding
# -------------------------------------------------

X = pd.get_dummies(
    X,
    columns=["contract", "internet_service"],
    drop_first=False
)


# -------------------------------------------------
# 7. Convert boolean columns to integers
# -------------------------------------------------

X = X.fillna(0)

# -------------------------------------------------
# 8. Print final ML information
# -------------------------------------------------

print("\n===== FINAL FEATURE SET =====")

print(X.columns.tolist())

print("\nX shape:", X.shape)

print("y shape:", y.shape)


# -------------------------------------------------
# 9. Class balance
# -------------------------------------------------

print("\n===== CLASS BALANCE =====")

print(y.value_counts(normalize=True))


print("\n===== CLASS COUNTS =====")

print(y.value_counts())


print("\n========== ML1 COMPLETE ==========")