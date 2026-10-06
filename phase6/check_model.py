import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "logistic_churn.pkl"
)

print("Looking for model at:")
print(MODEL_PATH)

model = joblib.load(MODEL_PATH)

print("===== MODEL FEATURES =====")
print(model.feature_names_in_)