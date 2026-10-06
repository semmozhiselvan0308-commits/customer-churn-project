import pandas as pd
from customer_cleaner import CustomerCleaner

# -----------------------------------
# Load Dataset
# -----------------------------------
df = pd.read_csv("Teleco_Customer_Churn.csv")

# -----------------------------------
# Clean Dataset
# -----------------------------------
cleaner = CustomerCleaner(df)
clean_df = cleaner.clean()

print("Data Cleaned Successfully")

# -----------------------------------
# Feature 1 : Tenure Bucket
# -----------------------------------
bins = [0, 12, 24, 48, 72]
labels = ["0-12", "13-24", "25-48", "49-72"]

clean_df["tenure_bucket"] = pd.cut(
    clean_df["tenure"],
    bins=bins,
    labels=labels,
    include_lowest=True
)

# -----------------------------------
# Feature 2 : High Charge Flag
# -----------------------------------
median_charge = clean_df["monthly_charges"].median()

clean_df["high_charge_flag"] = (
    clean_df["monthly_charges"] > median_charge
).astype(int)

# -----------------------------------
# Feature 3 : Service Count
# -----------------------------------
service_columns = [
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies"
]

clean_df["service_count"] = (
    clean_df[service_columns]
    .astype(int)
    .sum(axis=1)
)

# -----------------------------------
# Feature 4 : Long Term Customer
# -----------------------------------
clean_df["is_long_term_customer"] = (
    clean_df["tenure"] >= 24
).astype(int)

# -----------------------------------
# Feature 5 : Streaming Bundle
# -----------------------------------
clean_df["has_streaming_bundle"] = (
    (clean_df["streaming_tv"] == 1) &
    (clean_df["streaming_movies"] == 1)
).astype(int)

# -----------------------------------
# Feature 6 : Auto Pay Flag
# -----------------------------------
clean_df["auto_pay_flag"] = (
    clean_df["payment_method"]
    .str.contains("automatic", case=False)
).astype(int)

# -----------------------------------
# Correlation with Churn
# -----------------------------------
print("\n===== Correlation with Churn =====")

feature_columns = [
    "high_charge_flag",
    "service_count",
    "is_long_term_customer",
    "has_streaming_bundle",
    "auto_pay_flag"
]

for col in feature_columns:
    corr = clean_df[col].corr(clean_df["churn"])
    print(f"{col} : {corr:.4f}")

# -----------------------------------
# Save CSV
# -----------------------------------
clean_df.to_csv("customer_features.csv", index=False)

print("\ncustomer_features.csv saved successfully.")