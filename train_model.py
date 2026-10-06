
from pathlib import Path

import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Project paths
PROJECT_DIR = Path(__file__).parent
DATA_PATH = PROJECT_DIR / "data" / "transactions.csv"
MODEL_PATH = PROJECT_DIR / "fraud_model.pkl"

# Load transaction data
df = pd.read_csv(DATA_PATH)

# Select features available before the fraud label is known
FEATURES = [
    "amount",
    "hour",
    "is_foreign",
    "failed_attempts",
]

X = df[FEATURES]
y = df["is_fraud"]

# Check that both classes have enough examples
if y.nunique() < 2 or y.value_counts().min() < 2:
    raise ValueError(
        "The dataset needs at least two examples of each class: 0 and 1."
    )

# Split the data for training and testing
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y,
)

# Train the model
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    random_state=42,
    class_weight="balanced",
)

model.fit(X_train, y_train)

# Evaluate on held-out test data
predictions = model.predict(X_test)

print("FraudLens AI - Model Evaluation")
print("--------------------------------")
print(
    classification_report(
        y_test,
        predictions,
        labels=[0, 1],
        target_names=["Legitimate (0)", "Fraud-labelled (1)"],
        zero_division=0,
    )
)

# Save the model and feature order
joblib.dump(
    {"model": model, "features": FEATURES},
    MODEL_PATH,
)

print(f"Model saved to: {MODEL_PATH}")
print(
    "Note: This is a learning prototype using synthetic data, "
    "not a validated real-world fraud detection system."
)
