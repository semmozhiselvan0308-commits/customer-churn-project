import pandas as pd
from datetime import datetime
import sys

# Access Phase 2 database.py
sys.path.append(r"C:\Users\semmozhiselvan.a\Documents\semmo proj\phase2")

from database import engine
from predict import predict_churn


print("========== ML5 BATCH SCORING START ==========")


# 1. Load ML features + contract information
query = """
SELECT
    ml.customer_id,
    fc.tenure,
    fc.monthly_charges,
    ml.service_count,
    fc.contract_id,
    dc.contract_name
FROM customer_ml_features ml
JOIN fact_customer_account fc
    ON ml.customer_id = fc.customer_id
JOIN dim_contract dc
    ON fc.contract_id = dc.contract_id
"""

df = pd.read_sql(query, engine)

print(f"Loaded customers: {len(df)}")

print("\n===== JOINED DATA CHECK =====")
print(df.head(10).to_string(index=False))
print("\nMissing values:")
print(df.isnull().sum())



# 2. Apply ML4 prediction to every customer
def score_customer(row):

    result = predict_churn(
        row["tenure"],
        row["monthly_charges"],
        row["contract_name"],
        row["service_count"]
    )

    return pd.Series({
        "risk_score": result["risk_score"],
        "prediction": result["prediction"],
        "confidence": result["confidence"]
    })


scores = df.apply(score_customer, axis=1)


# 3. Add prediction results
df = pd.concat([df, scores], axis=1)


# 4. Add scoring date
df["scoring_date"] = datetime.today().strftime("%Y-%m-%d")


# 5. Create final risk table
risk_table = df[
    [
        "customer_id",
        "risk_score",
        "prediction",
        "confidence",
        "scoring_date"
    ]
]


# 6. Save to SQL
risk_table.to_sql(
    "customer_risk_table",
    engine,
    if_exists="replace",
    index=False
)


# 7. Prediction summary
print("\n===== PREDICTION SUMMARY =====")

summary = risk_table["prediction"].value_counts()

print(summary)

total = len(risk_table)
likely = summary.get("Likely to churn", 0)
unlikely = summary.get("Unlikely to churn", 0)

print(f"\nTotal customers      : {total}")
print(f"Likely to churn      : {likely}")
print(f"Unlikely to churn    : {unlikely}")
print(f"Predicted churn rate : {(likely / total) * 100:.2f}%")


# 8. Top 10 highest-risk customers
print("\n===== TOP 10 HIGH-RISK CUSTOMERS =====")

top10 = risk_table.sort_values(
    by="risk_score",
    ascending=False
).head(10)

print(top10.to_string(index=False))


print("\n========== ML5 BATCH SCORING COMPLETE ==========")