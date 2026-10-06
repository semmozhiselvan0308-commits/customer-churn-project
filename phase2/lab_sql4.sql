SELECT
    churn,
    AVG(monthly_charges) AS avg_monthly_charges
FROM fact_customer_account
GROUP BY churn
ORDER BY churn;



