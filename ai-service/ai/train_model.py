import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import (
    train_test_split,
    cross_val_score,
    StratifiedKFold
)
from sklearn.metrics import (
    accuracy_score,
    classification_report
)

import joblib


# =========================================================
# LOAD DATASET
# =========================================================

DATASET_PATH = "ai/data/training_data.csv"
MODEL_PATH = "ai/data/risk_model.pkl"


df = pd.read_csv(DATASET_PATH)

print("Dataset loaded successfully.")
print(f"Dataset shape: {df.shape}")


# =========================================================
# FEATURES AND TARGET
# =========================================================

X = df.drop(
    "risk_label",
    axis=1
)

y = df["risk_label"]


# =========================================================
# TRAIN / TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)


print(
    f"Training samples: {len(X_train)}"
)

print(
    f"Testing samples: {len(X_test)}"
)


# =========================================================
# CREATE RANDOM FOREST MODEL
# =========================================================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)


# =========================================================
# CROSS-VALIDATION
# =========================================================

print()
print("Running 5-fold cross-validation...")

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

cv_scores = cross_val_score(
    model,
    X,
    y,
    cv=cv,
    scoring="accuracy"
)


print(
    "Cross-validation scores:"
)

for index, score in enumerate(
    cv_scores,
    start=1
):

    print(
        f"Fold {index}: "
        f"{score * 100:.2f}%"
    )


print(
    f"Average CV Accuracy: "
    f"{cv_scores.mean() * 100:.2f}%"
)


# =========================================================
# TRAIN MODEL
# =========================================================

print()
print("Training Random Forest model...")

model.fit(
    X_train,
    y_train
)

print("Training completed.")


# =========================================================
# TEST MODEL
# =========================================================

y_pred = model.predict(
    X_test
)


accuracy = accuracy_score(
    y_test,
    y_pred
)


print()
print("Test Accuracy:")
print(
    f"{accuracy * 100:.2f}%"
)


# =========================================================
# CLASSIFICATION REPORT
# =========================================================

print()
print("Classification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)


# =========================================================
# FEATURE IMPORTANCE
# =========================================================

print("Feature Importance:")

feature_importance = sorted(
    zip(
        X.columns,
        model.feature_importances_
    ),
    key=lambda item: item[1],
    reverse=True
)


for feature, importance in feature_importance:

    print(
        f"{feature}: "
        f"{importance:.4f}"
    )


# =========================================================
# SAVE MODEL
# =========================================================

joblib.dump(
    model,
    MODEL_PATH
)


print()
print(
    f"Model saved successfully to: "
    f"{MODEL_PATH}"
)