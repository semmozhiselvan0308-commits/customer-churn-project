# Semmo Project – Telecom Customer Churn Analytics and Prediction

## 1. Project Overview

This project is a complete end-to-end customer churn analysis and prediction solution built on a telecom dataset. The workflow starts with raw customer records, moves through data cleaning, SQL transformation, API exposure, dashboard visualization, and finally machine learning scoring.

The objective is to:

- Clean and validate telecom customer records
- Build business-friendly database tables
- Generate engineered features for churn analysis
- Expose APIs for customer and churn-related queries
- Build a frontend dashboard for monitoring churn risk
- Train and score a predictive churn model
- Automate data-quality checks and monitoring

This project is structured as a multi-phase solution. Each phase addresses one part of the pipeline.

---

## 2. Business Problem

Telecom companies lose customers when they move to competitors or stop using services. A churn prediction model helps identify customers who are likely to leave so that the business can act early with retention strategies.

The solution uses historical customer data, service usage information, contract type, and billing information to determine churn risk.

---

## 3. Tools and Technologies

The project uses the following technologies:

- Python
- Pandas
- NumPy
- SQLAlchemy
- MySQL
- FastAPI
- React
- Scikit-learn
- PySpark
- Joblib
- Excel/CSV data files

---

## 4. Project Structure

```text
semmo proj/
├── phase1/
│   ├── customer_cleaner.py
│   ├── customer_pipeline.py
│   ├── lab_c3.py
│   ├── lab_c4.py
│   ├── profiling.py
│   ├── Teleco_Customer_Churn.csv
│   └── output/
├── phase2/
│   ├── connection.py
│   ├── database.py
│   ├── lab_sql2.py
│   ├── lab_sql3.py
│   ├── lab_sql4.sql
│   ├── labsql5.sql
│   ├── models.py
│   └── Teleco_Customer_Churn.csv
├── phase3/
│   └── api.py
├── phase4/
│   └── customer-dashboard/
├── phase5/
│   ├── DE1_architecture/
│   ├── DE2_ingestion/
│   ├── DE3_cleaning/
│   ├── DE4_feature_pipeline/
│   ├── de5_spark/
│   ├── DE6_incremental/
│   ├── DE7_Quality/
│   └── quality_report.json
├── phase6/
│   ├── batch_score.py
│   ├── check_model.py
│   ├── ml1_problem_setup.py
│   ├── ml2.py
│   ├── ml3_interpret.py
│   ├── predict.py
│   └── models/
└── README.md
```

---

## 5. Overall Data Flow

```text
Raw CSV
   ↓
Data cleaning
   ↓
Feature engineering
   ↓
Database tables
   ↓
API layer
   ↓
Dashboard
   ↓
ML model training and scoring
   ↓
Churn risk output
```

This pipeline is designed to move from raw business data to a decision-support system.

---

# Phase 1 – Data Cleaning and Feature Engineering

## 5.1 Purpose of Phase 1

Phase 1 is responsible for cleaning the telecom dataset and preparing it for downstream analysis. The raw file contains inconsistent values, blank entries, mixed-case column names, and formatting issues that must be corrected before any model work begins.

This phase is important because poor-quality input data causes unstable models and inaccurate reports.

## 5.2 Core Cleaning Logic

The core of the data cleaning is implemented in [phase1/customer_cleaner.py](phase1/customer_cleaner.py).

```python
class CustomerCleaner:

    def __init__(self, df):
        self.df = df.copy()

    def standardize_column_names(self):
        self.df.columns = (
            self.df.columns
            .str.replace(r'([a-z])([A-Z])', r'\1_\2', regex=True)
            .str.lower()
        )
        return self
```

This code standardizes column names to snake_case. For example, the column `TotalCharges` becomes `total_charges`.

## 5.3 Fixing Numeric Values

The project specifically handles blank strings in `total_charges`, which are common in telecom datasets.

```python
self.df["total_charges"] = self.df["total_charges"].replace(
    r"^\s*$",
    np.nan,
    regex=True
)

self.df["total_charges"] = pd.to_numeric(
    self.df["total_charges"],
    errors="coerce"
)
```

This ensures that empty values become `NaN`, and then they are converted into numeric values for calculations.

## 5.4 Binary Value Normalization

The script also converts Yes/No-type fields into numeric values such as 1 and 0.

```python
mapping = {
    "Yes": 1,
    "No": 0,
    "No internet service": 0
}

for col in binary_columns:
    if col in self.df.columns:
        self.df[col] = self.df[col].replace(mapping)
```

This is useful because most machine learning models require numeric input.

## 5.5 Null Handling

The project fills missing `total_charges` values using `monthly_charges` as a fallback.

```python
self.df["total_charges"] = self.df["total_charges"].fillna(
    self.df["monthly_charges"]
)
```

This avoids missing values in the final feature set.

## 5.6 Feature Engineering Pipeline

The file [phase1/customer_pipeline.py](phase1/customer_pipeline.py) is responsible for generating business features.

```python
def build_features(df):
    feature_df = df.copy()

    feature_df["tenure_group"] = pd.cut(
        feature_df["tenure"],
        bins=[0, 12, 24, 48, 72],
        labels=[
            "0-12 Months",
            "13-24 Months",
            "25-48 Months",
            "49-72 Months"
        ],
        include_lowest=True
    )
```

It creates:

- tenure groups
- average monthly spend
- high-value customer flag
- senior citizen flag
- service count
- charge per service

## 5.7 Data Quality Checks

The pipeline checks required business rules before final output is saved.

```python
def data_quality_check(df):
    assert df["monthly_charges"].isnull().sum() == 0
    assert set(df["churn"].unique()).issubset({0, 1})
```

This ensures data quality before the model is trained or the dashboard uses the data.

## 5.8 Output Files

Phase 1 saves cleaned and feature files in the output folder.

```python
clean_df.to_csv(clean_file, index=False)
feature_df.to_csv(feature_file, index=False)
```

These outputs become the base dataset for later phases.

---

# Phase 2 – Database and SQL Layer

## 6.1 Purpose of Phase 2

Phase 2 builds the database connection layer and creates the underlying relational model for storing customer data and analytical outputs.

The key files are:

- [phase2/database.py](phase2/database.py)
- [phase2/connection.py](phase2/connection.py)

## 6.2 Connection Setup

Database connectivity is created using SQLAlchemy.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/telecom_db"
engine = create_engine(DATABASE_URL)
```

This creates a database engine used by Python scripts to access MySQL tables.

## 6.3 Why the Database Matters

The data warehouse design allows the system to separate business data into logical tables such as:

- customers
- fact_customer_account
- dim_contract
- dim_payment
- customer_ml_features
- customer_risk_table

This allows the web application and model scoring process to query structured data instead of reading raw files directly.

## 6.4 Database Access Test

The connection script tests the SQL database connection.

```python
try:
    connection = engine.connect()
    print("✅ Database connected successfully!")
    connection.close()
except Exception as e:
    print("❌ Connection failed")
    print(e)
```

This is a very useful validation step before running SQL-based ingestion or model scoring.

## 6.5 SQL Design Philosophy

The database layer follows a star-style warehouse concept:

- Facts: customer account and behavior data
- Dimensions: contract, payment, and other reference data

This organization makes the system easier to report on and easier for the API layer to query.

---

# Phase 3 – API Layer

## 7.1 Purpose of Phase 3

Phase 3 exposes the business logic through a REST API. The API allows clients to query churn information, customer details, and model-based predictions without direct database access.

The main file is [phase3/api.py](phase3/api.py).

## 7.2 API Setup

The FastAPI application is initialized as follows:

```python
app = FastAPI(
    title="Telecom Customer Intelligence API",
    version="1.0.0"
)
```

This provides a clean API framework with built-in validation and documentation support.

## 7.3 Database Dependency

Each request connects to the MySQL database through a session object.

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

This ensures proper resource cleanup and prevents open database connections from accumulating.

## 7.4 API Key Validation

The API includes an authentication check using a custom header key.

```python
def verify_api_key(x_api_key: str | None = Header(default=None)):
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="API key is required")

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

This is important in production-grade systems because it protects sensitive business data.

## 7.5 Example Data Model

The API uses Pydantic models to define expected request and response structures.

```python
class ChurnPredictionRequest(BaseModel):
    tenure: int = Field(..., ge=0, le=100)
    monthly_charges: float = Field(..., gt=0)
    contract_type: str
    service_count: int
```

This validates user input before calling the prediction logic.

## 7.6 Churn Summary Query

The API queries aggregate churn performance by contract type and churn status.

```python
contract_rows = db.execute(
    text("""
        SELECT
            dc.contract_name,
            AVG(fca.churn) AS churn_rate
        FROM fact_customer_account fca
        JOIN dim_contract dc
            ON fca.contract_id = dc.contract_id
        GROUP BY dc.contract_name
    """)
).fetchall()
```

This gives managers a quick understanding of which contract types have higher churn rates.

## 7.7 API Value

The API is the bridge between the data layer and the dashboard. Without it, the frontend cannot retrieve customer records or churn predictions in real time.

---

# Phase 4 – React Dashboard

## 8.1 Purpose of Phase 4

The dashboard provides a user-facing interface for business users to inspect churn summaries, search customers, and review high-risk accounts.

The frontend is built in React and located under [phase4/customer-dashboard](phase4/customer-dashboard).

## 8.2 Main App Layout

The main app combines several dashboard components.

```jsx
import CustomerSearch from "./pages/CustomerSearch";
import ChurnSummary from "./pages/ChurnSummary";
import HighRiskCustomers from "./pages/HighRiskCustomers";
import ChurnPrediction from "./pages/ChurnPrediction";

function App() {
  return (
    <div>
      <h1>Customer Churn Dashboard</h1>
      <CustomerSearch />
      <ChurnSummary />
      <HighRiskCustomers />
      <ChurnPrediction />
    </div>
  );
}
```

## 8.3 Dashboard Modules

The dashboard includes:

- customer search
- churn summary display
- high-risk customer list
- dynamic churn prediction view

This makes the solution business-friendly and easy to present to non-technical stakeholders.

## 8.4 Business Use Case

The dashboard is useful for:

- identifying at-risk customers
- checking churn rates by contract type
- prioritizing retention campaigns
- monitoring model-driven risk scores

---

# Phase 5 – Data Engineering Pipeline

## 9.1 Purpose of Phase 5

Phase 5 focuses on production-style data engineering. It handles ingestion, schema validation, quality control, cleaning, feature generation, incremental updates, and pipeline orchestration.

This phase is located under [phase5](phase5).

## 9.2 Architecture Overview

The architecture file [phase5/DE1_architecture/architecture.md](phase5/DE1_architecture/architecture.md) explains the end-to-end design.

```text
CRM Extract
   ↓
Daily Raw CSV
   ↓
Schema Validation
   ↓
Staging Table
   ↓
Data Cleaning
   ↓
Data Quality Check
   ↓
Feature Engineering
   ↓
PySpark Analytics
   ↓
ML Scoring
   ↓
FastAPI
   ↓
React Dashboard
```

This is the main reference architecture for the entire project.

## 9.3 Ingestion Process

The ingestion step is handled by [phase5/DE2_ingestion/ingestion.py](phase5/DE2_ingestion/ingestion.py).

```python
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
```

The script validates that the file contains exactly the expected columns before loading it into the database.

## 9.4 Schema Validation

```python
def validate_schema(filepath):
    df = pd.read_csv(filepath)
    return df.columns.tolist() == EXPECTED_COLUMNS
```

If the schema fails, the file is not loaded and is marked as failed in the ingestion log.

## 9.5 Staging and Cleaning

The cleaning process is in [phase5/DE3_cleaning/cleaning.py](phase5/DE3_cleaning/cleaning.py).

```sql
CREATE TABLE cleaned_customers AS
SELECT
    customerID AS customer_id,
    gender,
    SeniorCitizen AS senior_citizen,
    CASE
        WHEN Partner = 'Yes' THEN 1
        WHEN Partner = 'No' THEN 0
        ELSE NULL
    END AS partner,
    tenure,
    MonthlyCharges AS monthly_charges,
    CASE
        WHEN Churn = 'Yes' THEN 1
        WHEN Churn = 'No' THEN 0
        ELSE NULL
    END AS churn
FROM stg_customer_raw
```

This creates a cleaned and normalized base table used by later ML and API work.

## 9.6 Quality Checks in Phase 5

The quality-check script [phase5/DE7_Quality/de7_quality.py](phase5/DE7_Quality/de7_quality.py) uses a rule-based validation strategy.

```python
def check_null_rate(df, col, threshold):
    null_rate = df[col].isnull().mean()
    return {
        "check_name": f"Null rate check - {col}",
        "status": "PASS" if null_rate <= threshold else "FAIL",
        "value": round(null_rate, 4),
        "threshold": threshold
    }
```

It verifies things like:

- null rates
- valid ranges
- duplicate customer IDs
- churn distribution
- row count thresholds

Any critical failure stops the pipeline.

## 9.7 Quality Report

The project writes the quality results to:

```text
phase5/quality_report.json
```

This makes the quality gate transparent and auditable.

## 9.8 Feature Pipeline and Spark Work

The project includes additional feature and Spark-based processing in the DE4 and DE5 folders. These components transform the cleaned dataset into analytics-ready outputs used by ML training and dashboard queries.

## 9.9 Incremental Processing

The project also includes incremental logic so that repeated ingestion of the same file does not create duplicate records. The logic checks whether the file has already been processed.

```python
def already_processed(filename):
    query = """
        SELECT COUNT(*)
        FROM ingestion_log
        WHERE filename = %s
        AND status = 'SUCCESS'
    """
```

This is an important production-quality safeguard.

---

# Phase 6 – Machine Learning and Model Scoring

## 10.1 Purpose of Phase 6

Phase 6 is responsible for preparing the model input, training the churn prediction model, and scoring customers in batch mode.

It includes files such as:

- [phase6/ml1_problem_setup.py](phase6/ml1_problem_setup.py)
- [phase6/ml2.py](phase6/ml2.py)
- [phase6/ml3_interpret.py](phase6/ml3_interpret.py)
- [phase6/predict.py](phase6/predict.py)
- [phase6/batch_score.py](phase6/batch_score.py)

## 10.2 Model Input Preparation

The model feature transformation is done in [phase6/ml2.py](phase6/ml2.py).

```python
X["service_count"] = (
    X[service_columns]
    .apply(lambda row: (row == 1).sum(), axis=1)
)

X["high_charge_flag"] = (
    X["monthly_charges"] > median_charge
).astype(int)

X["is_long_term_customer"] = (
    X["tenure"] >= 24
).astype(int)
```

These engineered values help the model separate churners from non-churners more clearly.

## 10.3 Encoding Categorical Variables

Categorical features like contract and internet service are transformed with one-hot encoding.

```python
X = pd.get_dummies(
    X,
    columns=["contract", "internet_service"],
    drop_first=False
)
```

This is a standard machine learning preprocessing step required for many algorithms.

## 10.4 Training Models

The project compares multiple models.

```python
logistic_model = LogisticRegression(max_iter=1000)
tree_model = DecisionTreeClassifier(max_depth=5, random_state=42)
```

These models are trained on the cleaned customer dataset and then evaluated using classification metrics.

## 10.5 Evaluation Metrics

The script prints metrics like:

- classification report
- confusion matrix
- accuracy
- churn vs active classification

```python
print(classification_report(
    y_test,
    logistic_pred,
    target_names=["Active", "Churned"]
))
```

This allows the team to compare which model performs better.

## 10.6 Model for Production Use

The final prediction logic is implemented in [phase6/predict.py](phase6/predict.py). It loads a persisted model and applies preprocessing to incoming values.

```python
def preprocess_input(
    tenure,
    monthly_charges,
    contract_type,
    service_count
):
    high_charge_flag = 1 if monthly_charges > 64.761692 else 0
    is_long_term_customer = 1 if tenure >= 24 else 0
```

The script then computes risk score and churn prediction.

```python
risk_score = model.predict_proba(input_data)[0][1]

if prediction == 1:
    result = "Likely to churn"
else:
    result = "Unlikely to churn"
```

## 10.7 Batch Scoring

The script [phase6/batch_score.py](phase6/batch_score.py) loads all customers, scores them, and saves the results to a database table.

```python
scores = df.apply(score_customer, axis=1)
df = pd.concat([df, scores], axis=1)
```

Then the output is written to `customer_risk_table`.

```python
risk_table.to_sql(
    "customer_risk_table",
    engine,
    if_exists="replace",
    index=False
)
```

This is the batch prediction layer used for operational churn monitoring.

## 10.8 Why This Matters

This step transforms the project from descriptive analytics into business action. It gives the company a method to flag customers at risk before they churn.

---

## 11. How the Full System Works Together

The entire project is a pipeline that connects all stages:

1. Collect raw customer data
2. Clean and normalize data
3. Store it in MySQL
4. Build curated tables and analytics tables
5. Expose data through APIs
6. Present results in dashboard widgets
7. Train machine learning models
8. Score each customer for churn risk
9. Return output to business stakeholders

This is a practical example of an end-to-end data science and analytics project.

---

## 12. Setup Instructions

### 12.1 Database Setup

Make sure MySQL is installed and running. Create a database named:

```sql
CREATE DATABASE telecom_db;
```

Update the connection strings inside the project where necessary.

### 12.2 Python Environment

It is recommended to create a virtual environment and install the dependencies:

```bash
pip install pandas numpy sqlalchemy pymysql fastapi uvicorn scikit-learn joblib mysql-connector-python
```

### 12.3 Run Phase 1 Pipeline

```bash
python phase1/customer_pipeline.py
```

### 12.4 Run API

```bash
uvicorn phase3.api:app --reload
```

### 12.5 Run Dashboard

Open the React dashboard and start the application.

```bash
cd phase4/customer-dashboard
npm install
npm start
```

### 12.6 Run ML Batch Scoring

```bash
python phase6/batch_score.py
```

---

## 13. Expected Deliverables

The project produces the following outputs:

- cleaned customer CSV files
- engineered feature files
- SQL database tables
- API responses for churn data
- interactive dashboard screen
- churn model outputs
- risk table for customer scoring
- quality report for validation monitoring

---

## 14. Key Lessons Learned

This project demonstrates the following important data engineering and analytics principles:

- Data quality is the foundation of model accuracy
- SQL tables structure the analytical pipeline clearly
- APIs provide a clean operational interface
- Reporting dashboards help business teams act on results
- ML models must be validated and tested before deployment
- Batch scoring makes churn monitoring process-driven and repeatable

---

## 15. Final Summary

The Semmo Project is a complete business intelligence and machine learning project focused on telecom churn prediction. It covers the full lifecycle from raw data ingestion to model-based risk scoring and business reporting.

The project is valuable because it combines:

- data engineering
- database design
- analytics
- API development
- dashboard building
- predictive modeling

This makes it an excellent end-to-end case study for practical data science and analytics work.

---

## 16. Quick Reference

| Phase | Focus | Main Files |
|---|---|---|
| Phase 1 | Cleaning and feature engineering | customer_cleaner.py, customer_pipeline.py |
| Phase 2 | Database and SQL setup | database.py, connection.py |
| Phase 3 | API services | api.py |
| Phase 4 | Dashboard | customer-dashboard |
| Phase 5 | Data engineering | DE1 to DE7 folders |
| Phase 6 | ML model and batch scoring | ml2.py, predict.py, batch_score.py |

---

## 17. Closing Note

This README is intentionally structured to be clear and compact while still being detailed enough for documentation export into a Word document. The project is practical, scalable, and suitable for business analytics and retention modeling work.

This project can be extended with:

- additional model tuning
- automated scheduling
- real-time API integration
- customer segmentation
- retention campaign trigger rules

The main goal remains the same: detect churn early and reduce customer loss through better data-driven decision making.
