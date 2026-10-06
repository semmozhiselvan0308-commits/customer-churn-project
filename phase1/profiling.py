import pandas as pd

# Load dataset
df = pd.read_csv("Teleco_Customer_Churn.csv")

# Print shape
print("Dataset Shape:")
print(df.shape)

print("\nColumn Names:")
print(df.columns)

print("\nData Types:")
print(df.dtypes)

#checking null values 
print("\nNull Values:")
print(df.isnull().sum())


#calculating the percentage of null values

null_percentage = (df.isnull().sum() / len(df)) * 100

print("\nNull Percentage:")
print(null_percentage)


#it is a file , which has categories in the column

categorical_columns = [
    "gender",
    "Partner",
    "Dependents",
    "PhoneService",
    "InternetService",
    "Contract",
    "PaymentMethod",
    "Churn"
]

for col in categorical_columns:
    print("\n" + "=" * 50)
    print("Column:", col)

    print("\nUnique Values:")
    print(df[col].unique())

    print("\nValue Counts:")
    print(df[col].value_counts())   #checking how many yes and no 


#checking how churns 

print("\nChurn Count:")
print(df["Churn"].value_counts())

print("\nChurn Percentage:")       #churn percentge 
print(df["Churn"].value_counts(normalize=True) * 100)



#chekcing total charges     

print("\nData Type of TotalCharges:")
print(df["TotalCharges"].dtype)

total = pd.to_numeric(df["TotalCharges"], errors="coerce")

print("\nNaN Values after Conversion:")
print(total.isnull().sum())



# it prints the statistics

df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

print("\nStatistics")

for col in ["tenure", "MonthlyCharges", "TotalCharges"]:
    print("\nColumn:", col)
    print("Minimum:", df[col].min())
    print("Maximum:", df[col].max())
    print("Mean:", df[col].mean())


print("\n========== DATA PROFILING SUMMARY ==========")
print("1. The dataset contains 7043 customer records and 21 columns.")
print("2. The TotalCharges column contains blank values that become NaN after conversion.")
print("3. Around 26.5% of customers have churned, while 73.5% have not.")
print("4. customerID is an identifier and should not be used as a machine learning feature.")
print("5. The TotalCharges column should be converted to numeric and missing values handled before further analysis.")