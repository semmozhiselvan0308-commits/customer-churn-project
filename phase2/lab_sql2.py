import pandas as pd
from sqlalchemy import create_engine
df = pd.read_csv("Teleco_Customer_Churn.csv")
print(df.head())
print(df.shape)
engine = create_engine(
    "mysql+pymysql://root:root@localhost/telecom_db"
)
df.to_sql(
    "stg_customer_raw",
    engine,
    if_exists="replace",
    index=False
)
print("Data Loaded Successfully")
print("Rows Loaded:", len(df))