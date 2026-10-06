# DE1 — Customer Data Pipeline Architecture

## 1. Pipeline Architecture


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


## 2. Pipeline Layer Mapping

| Layer | Data Format | Tool | Who Reads It Next |
|---|---|---|---|
| CRM Extract | CSV | CRM / Source System | Ingestion Process |
| Raw File | CSV | Python | Schema Validation |
| Staging Table | MySQL Table | Python + SQLAlchemy | Cleaning Process |
| Cleaned Data | DataFrame / Table | Pandas + Python | Feature Engineering |
| Feature Table | DataFrame / Table | Python / PySpark | PySpark Analytics |
| Analytics Output | Table | PySpark | ML Scoring |
| ML Scoring | Table / JSON | Scikit-learn | FastAPI |
| API | JSON | FastAPI | React Dashboard |
| Dashboard | Web UI | React | End User |






## 3. Quality Gate 1 — Schema Validation

Schema validation happens after the raw CSV arrives and before the
data is loaded into the staging table.

### What We Check

- Required columns exist
- Column names are correct
- Expected data types are present
- No unexpected structural changes are present
- The input file can be read successfully

### Example

Expected columns:

- customerID
- gender
- tenure
- MonthlyCharges
- TotalCharges
- Contract
- InternetService
- PaymentMethod
- Churn

### If Validation Passes

The file is allowed to move forward:

Raw CSV
   ↓
Schema Validation
   ↓
PASS
   ↓
Staging Table

### If Validation Fails

The pipeline must stop:

Raw CSV
   ↓
Schema Validation
   ↓
FAIL
   ↓
Stop Pipeline
   ↓
Log Error
   ↓
Do Not Load Invalid Data





## 4. Quality Gate 2 — Data Quality Check

The data quality check happens after cleaning and before feature
engineering.

### What We Check

- customerID is not missing
- customerID is not duplicated
- tenure is valid
- MonthlyCharges is numeric
- MonthlyCharges is not negative
- TotalCharges is numeric
- Contract contains valid values
- InternetService contains valid values
- PaymentMethod contains valid values
- Churn contains valid values

### Example Valid Data

customerID = 7590-VHVEG
tenure = 12
MonthlyCharges = 70.50
TotalCharges = 846.00
Churn = No

### Example Invalid Data

customerID = NULL
MonthlyCharges = -50
Churn = Unknown

### If Validation Passes

Cleaned Data
     ↓
Data Quality Check
     ↓
PASS
     ↓
Feature Engineering

### If Validation Fails

Cleaned Data
     ↓
Data Quality Check
     ↓
FAIL
     ↓
Stop Downstream Processing
     ↓
Log Error / Invalid Records




## 5. Incremental Processing Strategy

The customer_id will be used as the business key.

Each daily customer extract may contain:

- New customers
- Existing customers
- Updated customer information

### Processing Logic

For every incoming customer record:

1. Check whether customer_id already exists.
2. If customer_id does not exist, INSERT the new customer.
3. If customer_id already exists, UPDATE the existing customer.
4. Do not create duplicate current customer records.

### Upsert Logic

Incoming Customer
       ↓
Does customer_id exist?
       │
    ┌──┴──┐
    │     │
   YES    NO
    │     │
 UPDATE  INSERT
    │     │
    └──┬──┘
       ↓
 Updated Customer Data

### Idempotency

The pipeline must be idempotent.

If the same daily file is processed twice, the second run
must not create duplicate records.

Example:

First run:

    7,043 customers

Second run with the same file:

    7,043 customers

The result should remain the same.

### Batch Strategy

The source provides one daily customer extract.

The initial implementation can process the complete daily
batch.

As the dataset grows, incremental processing can be introduced
to process only new or changed customer records.


## 6. Layer-to-Lab Mapping

The Phase 5 Data Engineering pipeline builds on the work completed
in the previous Customer Pipeline, SQL, and API labs.

| Pipeline Layer | Existing Lab / Work |
|---|---|
| CRM Extract | Source customer dataset |
| Raw CSV | Teleco_Customer_Churn.csv |
| Ingestion | CP5 — Customer Pipeline |
| Staging Table | SQL staging work |
| Cleaning | CP2 — CustomerCleaner |
| Business Analysis | CP3 — Business Insights |
| Feature Engineering | CP4 — Engineered Features |
| Pipeline | CP5 — Customer Pipeline |
| Curated Database Tables | SQL3 |
| Business Analytics | SQL4 |
| ML Feature Table | SQL5 |
| High-Risk Customer Rules | SQL6 |
| Customer Profile API | API1 |
| Churn Summary API | API2 |
| PySpark Analytics | DE5 |
| ML Scoring | ML pipeline |
| Dashboard | React application |

### Pipeline Relationship

CP2
 ↓
Cleaning

CP3
 ↓
Business Understanding

CP4
 ↓
Feature Engineering

CP5
 ↓
Pipeline

SQL Labs
 ↓
Database Storage + Analytics

DE Labs
 ↓
Production Data Engineering

API Labs
 ↓
Serving Data to Applications