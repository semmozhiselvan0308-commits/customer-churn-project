import os
import joblib
import pandas as pd


# Load model once when the API starts
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "logistic_churn.pkl"
)

model = joblib.load(MODEL_PATH)


def preprocess_input(
    tenure,
    monthly_charges,
    contract_type,
    service_count
):
    # Derived features
    high_charge_flag = 1 if monthly_charges > 64.761692 else 0
    is_long_term_customer = 1 if tenure >= 24 else 0

    # Default values for features not supplied by API
    total_charges = monthly_charges * tenure
    auto_pay_flag = 0
    has_streaming_bundle = 0

    # Contract encoding
    contract_month = 0
    contract_one_year = 0
    contract_two_year = 0

    if contract_type == "Month-to-month":
        contract_month = 1
    elif contract_type == "One year":
        contract_one_year = 1
    elif contract_type == "Two year":
        contract_two_year = 1

    # Internet service encoding
    internet_dsl = 0
    internet_fiber = 1
    internet_no = 0

    data = {
        "tenure": [tenure],
        "monthly_charges": [monthly_charges],
        "total_charges": [total_charges],
        "service_count": [service_count],
        "high_charge_flag": [high_charge_flag],
        "is_long_term_customer": [is_long_term_customer],
        "auto_pay_flag": [auto_pay_flag],
        "has_streaming_bundle": [has_streaming_bundle],
        "contract_Month-to-month": [contract_month],
        "contract_One year": [contract_one_year],
        "contract_Two year": [contract_two_year],
        "internet_service_DSL": [internet_dsl],
        "internet_service_Fiber optic": [internet_fiber],
        "internet_service_No": [internet_no]
    }

    return pd.DataFrame(data)


def predict_churn(
    tenure,
    monthly_charges,
    contract_type,
    service_count
):
    input_data = preprocess_input(
        tenure,
        monthly_charges,
        contract_type,
        service_count
    )

    prediction = model.predict(input_data)[0]

    risk_score = model.predict_proba(input_data)[0][1]

    if prediction == 1:
        result = "Likely to churn"
    else:
        result = "Unlikely to churn"

    return {
        "risk_score": float(risk_score),
        "prediction": result,
        "confidence": float(risk_score)
    }