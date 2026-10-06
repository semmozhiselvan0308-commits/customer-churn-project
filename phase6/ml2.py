import os
import pandas as pd
import joblib

from sqlalchemy import create_engine

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score
)


print("========== ML2 START ==========")


# ==================================================
# 1. LOAD CLEANED DATA
# ==================================================

engine = create_engine(
    "mysql+pymysql://root:root@localhost/telecom_db"
)

ml_df = pd.read_sql(
    "SELECT * FROM cleaned_customers",
    engine
)

print("Loaded cleaned_customers:", ml_df.shape)


# ==================================================
# 2. CREATE ML1 FEATURES
# ==================================================

y = ml_df["churn"]

X = ml_df.copy()


# --------------------------------------------------
# Service count
# --------------------------------------------------

service_columns = [
    "phone_service",
    "multiple_lines",
    "online_security",
    "online_backup",
    "device_protection",
    "tech_support",
    "streaming_tv",
    "streaming_movies"
]

X["service_count"] = (
    X[service_columns]
    .apply(lambda row: (row == 1).sum(), axis=1)
)


# --------------------------------------------------
# High charge flag
# --------------------------------------------------

median_charge = X["monthly_charges"].median()

X["high_charge_flag"] = (
    X["monthly_charges"] > median_charge
).astype(int)


# --------------------------------------------------
# Long-term customer flag
# --------------------------------------------------

X["is_long_term_customer"] = (
    X["tenure"] >= 24
).astype(int)


# --------------------------------------------------
# Auto-pay flag
# --------------------------------------------------

X["auto_pay_flag"] = (
    X["payment_method"]
    .isin([
        "Bank transfer (automatic)",
        "Credit card (automatic)"
    ])
).astype(int)


# --------------------------------------------------
# Streaming bundle
# --------------------------------------------------

X["has_streaming_bundle"] = (
    (X["streaming_tv"] == 1) &
    (X["streaming_movies"] == 1)
).astype(int)


# ==================================================
# 3. SELECT FINAL ML1 FEATURES
# ==================================================

feature_columns = [
    "tenure",
    "monthly_charges",
    "total_charges",
    "service_count",
    "high_charge_flag",
    "is_long_term_customer",
    "auto_pay_flag",
    "has_streaming_bundle",
    "contract",
    "internet_service"
]

X = X[feature_columns].copy()


# ==================================================
# 4. ENCODE CATEGORICAL FEATURES
# ==================================================

X = pd.get_dummies(
    X,
    columns=[
        "contract",
        "internet_service"
    ],
    drop_first=False
)

X = X.fillna(0)

X = X.astype(float)


print("\n===== FINAL FEATURE SET =====")
print(X.columns.tolist())

print("\nX shape:", X.shape)
print("y shape:", y.shape)


# ==================================================
# 5. TRAIN / TEST SPLIT
# ==================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

print("\nTraining rows:", len(X_train))
print("Testing rows:", len(X_test))


# ==================================================
# 6. CREATE MODELS
# ==================================================

logistic_model = LogisticRegression(
    max_iter=1000
)

tree_model = DecisionTreeClassifier(
    max_depth=5,
    random_state=42
)


# ==================================================
# 7. TRAIN MODELS
# ==================================================

print("\nTraining Logistic Regression...")
logistic_model.fit(
    X_train,
    y_train
)

print("Training Decision Tree...")
tree_model.fit(
    X_train,
    y_train
)


# ==================================================
# 8. PREDICTIONS
# ==================================================

logistic_pred = logistic_model.predict(X_test)

tree_pred = tree_model.predict(X_test)


# ==================================================
# 9. LOGISTIC REGRESSION EVALUATION
# ==================================================

print("\n========================================")
print("LOGISTIC REGRESSION")
print("========================================")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        logistic_pred,
        target_names=["Active", "Churned"]
    )
)

print("Confusion Matrix:")

print(
    confusion_matrix(
        y_test,
        logistic_pred
    )
)


# ==================================================
# 10. DECISION TREE EVALUATION
# ==================================================

print("\n========================================")
print("DECISION TREE")
print("========================================")

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        tree_pred,
        target_names=["Active", "Churned"]
    )
)

print("Confusion Matrix:")

print(
    confusion_matrix(
        y_test,
        tree_pred
    )
)


# ==================================================
# 11. 5-FOLD CROSS VALIDATION F1
# ==================================================

print("\n========================================")
print("5-FOLD CROSS VALIDATION F1")
print("========================================")

logistic_cv = cross_val_score(
    logistic_model,
    X,
    y,
    cv=5,
    scoring="f1"
)

tree_cv = cross_val_score(
    tree_model,
    X,
    y,
    cv=5,
    scoring="f1"
)

print("Logistic Regression CV F1:")
print(logistic_cv)

print(
    "Logistic Regression Mean CV F1:",
    logistic_cv.mean()
)

print("\nDecision Tree CV F1:")
print(tree_cv)

print(
    "Decision Tree Mean CV F1:",
    tree_cv.mean()
)


# ==================================================
# 12. GET CLASSIFICATION METRICS
# ==================================================

logistic_report = classification_report(
    y_test,
    logistic_pred,
    output_dict=True
)

tree_report = classification_report(
    y_test,
    tree_pred,
    output_dict=True
)


# ==================================================
# 13. COMPARISON TABLE
# ==================================================

comparison = pd.DataFrame({

    "Model": [
        "Logistic Regression",
        "Decision Tree"
    ],

    "Accuracy": [
        accuracy_score(
            y_test,
            logistic_pred
        ),
        accuracy_score(
            y_test,
            tree_pred
        )
    ],

    "Precision (Churned)": [
        logistic_report["1"]["precision"],
        tree_report["1"]["precision"]
    ],

    "Recall (Churned)": [
        logistic_report["1"]["recall"],
        tree_report["1"]["recall"]
    ],

    "F1 (Churned)": [
        logistic_report["1"]["f1-score"],
        tree_report["1"]["f1-score"]
    ],

    "CV F1": [
        logistic_cv.mean(),
        tree_cv.mean()
    ]
})


print("\n========================================")
print("MODEL COMPARISON")
print("========================================")

print(
    comparison.to_string(index=False)
)


# ==================================================
# 14. MODEL SELECTION
# ==================================================

logistic_f1 = logistic_report["1"]["f1-score"]

tree_f1 = tree_report["1"]["f1-score"]


print("\n========================================")
print("MODEL SELECTION")
print("========================================")


if logistic_f1 > tree_f1:

    print("Better Model: Logistic Regression")

    print(
        "Justification: Logistic Regression has "
        "the higher F1 score for the Churned class."
    )

elif tree_f1 > logistic_f1:

    print("Better Model: Decision Tree")

    print(
        "Justification: Decision Tree has "
        "the higher F1 score for the Churned class."
    )

else:

    print(
        "Both models have the same "
        "Churned F1 score."
    )


# ==================================================
# 15. SAVE MODELS
# ==================================================

os.makedirs(
    "models",
    exist_ok=True
)

joblib.dump(
    logistic_model,
    "models/logistic_churn.pkl"
)

joblib.dump(
    tree_model,
    "models/tree_churn.pkl"
)


print("\n========================================")
print("MODELS SAVED")
print("========================================")

print("models/logistic_churn.pkl")
print("models/tree_churn.pkl")

print("\n========== ML2 COMPLETE ==========")