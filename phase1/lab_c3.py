import pandas as pd
from customer_cleaner import CustomerCleaner

# -----------------------------
# Load Dataset
# -----------------------------
df = pd.read_csv("Teleco_Customer_Churn.csv")

# -----------------------------
# Clean Data
# -----------------------------
cleaner = CustomerCleaner(df)
clean_df = cleaner.clean()

print("\n========== CLEAN DATA ==========")
print(clean_df.head())

# ----------------------------------------------------
# 1. Churn Rate by Contract Type
# ----------------------------------------------------
print("\n========== CHURN RATE BY CONTRACT ==========")

contract_churn = (
    clean_df.groupby("contract")["churn"]
    .mean()
    .sort_values(ascending=False) * 100
)

print(contract_churn.round(2))

# ----------------------------------------------------
# 2. Churn Rate by Internet Service
# ----------------------------------------------------
print("\n========== CHURN RATE BY INTERNET SERVICE ==========")

internet_churn = (
    clean_df.groupby("internet_service")["churn"]
    .mean()
    .sort_values(ascending=False) * 100
)

print(internet_churn.round(2))

# ----------------------------------------------------
# 3. Churn Rate by Payment Method
# ----------------------------------------------------
print("\n========== CHURN RATE BY PAYMENT METHOD ==========")

payment_churn = (
    clean_df.groupby("payment_method")["churn"]
    .mean()
    .sort_values(ascending=False) * 100
)

print(payment_churn.round(2))

# ----------------------------------------------------
# 4. Churn Rate by Tenure Bucket
# ----------------------------------------------------
print("\n========== CHURN RATE BY TENURE ==========")

bins = [0, 12, 24, 48, 72]
labels = ["0-12", "13-24", "25-48", "49-72"]

clean_df["tenure_bucket"] = pd.cut(
    clean_df["tenure"],
    bins=bins,
    labels=labels,
    include_lowest=True
)

tenure_churn = (
    clean_df.groupby("tenure_bucket")["churn"]
    .mean() * 100
)

print(tenure_churn.round(2))

# ----------------------------------------------------
# 5. Average Monthly Charges
# ----------------------------------------------------
print("\n========== AVERAGE MONTHLY CHARGES ==========")

monthly = clean_df.groupby("churn")["monthly_charges"].mean()

monthly.index = ["No Churn", "Churn"]

print(monthly.round(2))

# ----------------------------------------------------
# 6. Highest Risk Combination
# ----------------------------------------------------
print("\n========== CONTRACT + INTERNET SERVICE ==========")

combo = (
    clean_df.groupby(["contract", "internet_service"])["churn"]
    .mean()
    .sort_values(ascending=False) * 100
)

print(combo.round(2))

print("\nHighest Risk Segment")
print(combo.head(1))

# ----------------------------------------------------
# 7. Business Summary
# ----------------------------------------------------
print("\n========== BUSINESS SUMMARY ==========")

print("""
1. Customers with Month-to-Month contracts have the highest churn rate,
especially those using Fiber Optic internet.

2. Customers in the first 12 months of service and those paying through
Electronic Check are more likely to leave the company.

3. The retention team should focus on these high-risk customers by offering
discounts, loyalty rewards, or contract upgrade plans to reduce churn.
""")