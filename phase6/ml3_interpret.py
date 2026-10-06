import pandas as pd
import joblib
import matplotlib.pyplot as plt

from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split


print("========== ML3 START ==========")


# ==================================================
# 1. LOAD DATA
# ==================================================

engine = create_engine(
    "mysql+pymysql://root:root@localhost/telecom_db"
)

ml_df = pd.read_sql(
    "SELECT * FROM cleaned_customers",
    engine
)

print("Loaded cleaned_customers:", ml_df.shape)


# ==================================================
# 2. CREATE SAME FEATURES AS ML2
# ==================================================

y = ml_df["churn"]

X = ml_df.copy()

service_columns = [
    "phone_service",
    "multiple_lines",
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies"
]

X["service_count"] = (
    X[service_columns]
    .apply(lambda row: (row == 1).sum(), axis=1)
)

median_charge = X["monthly_charges"].median()

X["high_charge_flag"] = (
    X["monthly_charges"] > median_charge
).astype(int)

X["is_long_term_customer"] = (
    X["tenure"] >= 24
).astype(int)

X["auto_pay_flag"] = (
    X["payment_method"].isin([
        "Bank transfer (automatic)",
        "Credit card (automatic)"
    ])
).astype(int)

X["has_streaming_bundle"] = (
    (X["streaming_tv"] == 1) &
    (X["streaming_movies"] == 1)
).astype(int)


# ==================================================
# 3. SELECT FEATURES
# ==================================================

feature_columns = [
    "tenure",
    "monthly_charges",
    "total_charges",
    "service_count",
    "high_charge_flag",
    "is_long_term_customer",
    "auto_pay_flag",
    "has_streaming_bundle",
    "contract",
    "internet_service"
]

X = X[feature_columns].copy()


# ==================================================
# 4. ENCODE FEATURES
# ==================================================

X = pd.get_dummies(
    X,
    columns=[
        "contract",
        "internet_service"
    ],
    drop_first=False
)

X = X.fillna(0)

X = X.astype(float)


# ==================================================
# 5. TRAIN / TEST SPLIT
# ==================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)


# ==================================================
# 6. LOAD LOGISTIC MODEL
# ==================================================

logistic_model = joblib.load(
    "models/logistic_churn.pkl"
)

print("\nLogistic Regression model loaded.")


# ==================================================
# 7. LOGISTIC COEFFICIENTS
# ==================================================

logistic_coefficients = pd.Series(
    logistic_model.coef_[0],
    index=X.columns
)

print("\n===== LOGISTIC REGRESSION COEFFICIENTS =====")

print(
    logistic_coefficients
    .sort_values(ascending=False)
)


# ==================================================
# 8. TOP 10 FEATURES
# ==================================================

top_10 = (
    logistic_coefficients
    .abs()
    .sort_values(ascending=False)
    .head(10)
)

print("\n===== TOP 10 FEATURES =====")

print(top_10)


# ==================================================
# 9. TOP 10 FEATURE CHART
# ==================================================

plt.figure(figsize=(10, 6))

top_10.sort_values().plot(
    kind="barh"
)

plt.title(
    "Top 10 Logistic Regression Features"
)

plt.xlabel(
    "Absolute Coefficient"
)

plt.ylabel(
    "Feature"
)

plt.tight_layout()

plt.show()


# ==================================================
# 10. CHURN PROBABILITY
# ==================================================

churn_probability = (
    logistic_model
    .predict_proba(X_test)[:, 1]
)


# ==================================================
# 11. CREATE RISK TABLE
# ==================================================

risk_df = pd.DataFrame({

    "customer_id": ml_df.loc[
        X_test.index,
        "customer_id"
    ],

    "churn_probability": churn_probability

})


# ==================================================
# 12. TOP 20 HIGHEST-RISK CUSTOMERS
# ==================================================

top_20_risk = (
    risk_df
    .sort_values(
        "churn_probability",
        ascending=False
    )
    .head(20)
)


print("\n========================================")
print("TOP 20 HIGHEST-RISK CUSTOMERS")
print("========================================")

print(
    top_20_risk.to_string(index=False)
)


print("\n========== ML3 PART 3 COMPLETE ==========")



# ==================================================
# 13. SQL6 HIGH-RISK CUSTOMERS
# ==================================================

sql6_risk = pd.read_sql(
    "SELECT * FROM v_high_risk_customers",
    engine
)

print("\n========================================")
print("SQL6 HIGH-RISK CUSTOMERS")
print("========================================")

print(sql6_risk.head())


# ==================================================
# 14. OVERLAP ANALYSIS
# ==================================================

ml_top20_ids = set(
    top_20_risk["customer_id"]
)

sql6_ids = set(
    sql6_risk["customer_id"]
)

overlap = ml_top20_ids.intersection(
    sql6_ids
)

print("\n========================================")
print("ML vs SQL6 OVERLAP")
print("========================================")

print(
    "ML top-20 customers:",
    len(ml_top20_ids)
)

print(
    "SQL6 high-risk customers:",
    len(sql6_ids)
)

print(
    "Customers appearing in both:",
    len(overlap)
)

print(
    "Overlapping customer IDs:",
    sorted(overlap)
)


print("\n========== ML3 COMPLETE ==========")