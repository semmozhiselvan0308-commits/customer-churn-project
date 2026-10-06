from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import os



from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType
)

# ==========================================
# 1. CREATE SPARK SESSION
# ==========================================

spark = (
    SparkSession.builder
    .appName("DE5_Customer_Churn")
    .master("local[2]")
    .config("spark.driver.memory", "4g")
    .config("spark.hadoop.fs.permissions.umask-mode", "000")
    .config("spark.hadoop.fs.file.impl", "org.apache.hadoop.fs.RawLocalFileSystem")
    .getOrCreate()
)

print("===== SPARK SESSION STARTED =====")


# ==========================================
# 2. DEFINE MANUAL SCHEMA
# ==========================================

customer_schema = StructType([
    StructField("customerID", StringType(), True),
    StructField("gender", StringType(), True),
    StructField("SeniorCitizen", IntegerType(), True),
    StructField("Partner", StringType(), True),
    StructField("Dependents", StringType(), True),
    StructField("tenure", IntegerType(), True),
    StructField("PhoneService", StringType(), True),
    StructField("MultipleLines", StringType(), True),
    StructField("InternetService", StringType(), True),
    StructField("OnlineSecurity", StringType(), True),
    StructField("OnlineBackup", StringType(), True),
    StructField("DeviceProtection", StringType(), True),
    StructField("TechSupport", StringType(), True),
    StructField("StreamingTV", StringType(), True),
    StructField("StreamingMovies", StringType(), True),
    StructField("Contract", StringType(), True),
    StructField("PaperlessBilling", StringType(), True),
    StructField("PaymentMethod", StringType(), True),
    StructField("MonthlyCharges", DoubleType(), True),
    StructField("TotalCharges", StringType(), True),
    StructField("Churn", StringType(), True)
])

print("===== MANUAL SCHEMA CREATED =====")
print(customer_schema.simpleString())


# ==========================================
# 3. READ CSV
# ==========================================

csv_path = "DE1_architecture/data/landing/Teleco_Customer_Churn.csv"

df = (
    spark.read
    .option("header", True)
    .schema(customer_schema)
    .csv(csv_path)
)

print("===== CSV LOADED =====")

df.printSchema()

print(f"Total rows: {df.count()}")


# ==========================================
# 4. CLEAN TOTALCHARGES
# ==========================================

df = df.withColumn(
    "TotalCharges",
    F.regexp_replace(
        F.col("TotalCharges"),
        r"^\s*$",
        ""
    )
)

df = df.withColumn(
    "TotalCharges",
    F.col("TotalCharges").cast("double")
)

print("===== TOTALCHARGES CLEANED =====")

df.printSchema()

df.select(
    "customerID",
    "tenure",
    "MonthlyCharges",
    "TotalCharges"
).show(15, truncate=False)



# ==========================================
# 5. ENCODE CHURN
# ==========================================

df = df.withColumn(
    "churn_encoded",
    F.when(F.col("Churn") == "Yes", 1)
     .otherwise(0)
)

print("===== CHURN ENCODED =====")

df.select(
    "customerID",
    "Churn",
    "churn_encoded"
).show(10, truncate=False)



# ==========================================
# 6. CONTRACT-LEVEL CHURN SUMMARY
# ==========================================

contract_summary = (
    df.groupBy("Contract")
    .agg(
        F.count("*").alias("customer_count"),
        F.avg("churn_encoded").alias("churn_rate")
    )
    .orderBy("Contract")
)

print("===== CONTRACT CHURN SUMMARY =====")

contract_summary.show(truncate=False)\



# ==========================================
# 7. INTERNET SERVICE SUMMARY
# ==========================================

internet_summary = (
    df.groupBy("InternetService")
    .agg(
        F.avg("MonthlyCharges").alias("avg_monthly_charges"),
        F.avg("churn_encoded").alias("churn_rate")
    )
    .orderBy("InternetService")
)

print("===== INTERNET SERVICE SUMMARY =====")

internet_summary.show(truncate=False)



# ==========================================
# 8. WRITE CONTRACT SUMMARY TO PARQUET
# ==========================================

output_path = "data/spark_output/contract_summary"

contract_summary.write \
    .mode("overwrite") \
    .partitionBy("Contract") \
    .parquet(output_path)

print("===== CONTRACT SUMMARY WRITTEN TO PARQUET =====")
print(f"Output path: {output_path}")

# ==========================================
# 5. STOP SPARK
# ==========================================

spark.stop()