

SELECT AVG(monthly_charges) AS avg_monthly_charges
FROM customer_ml_features;



#test the high risk customers 
SELECT
    f.customer_id,
    f.tenure,
    f.monthly_charges,
    d.contract_name AS contract,
    'Month-to-month + tenure < 12 + charges above dataset average' AS risk_reason
FROM customer_ml_features f
JOIN fact_customer_account a
    ON f.customer_id = a.customer_id
JOIN dim_contract d
    ON a.contract_id = d.contract_id
WHERE d.contract_name = 'Month-to-month'
  AND f.tenure < 12
  AND f.monthly_charges > 64.761692;


# create v_high_risk_customers

CREATE OR REPLACE VIEW v_high_risk_customers AS
SELECT
    f.customer_id,
    f.tenure,
    f.monthly_charges,
    d.contract_name AS contract,
    'Month-to-month + tenure < 12 + charges above dataset average' AS risk_reason
FROM customer_ml_features f
JOIN fact_customer_account a
    ON f.customer_id = a.customer_id
JOIN dim_contract d
    ON a.contract_id = d.contract_id
WHERE d.contract_name = 'Month-to-month'
  AND f.tenure < 12
  AND f.monthly_charges > 64.761692;

  #Step 7 — Query the view
  SELECT *
FROM v_high_risk_customers
LIMIT 10;

