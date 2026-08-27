import joblib
import pandas as pd


# ---------------------------------------------
# Model path
# ---------------------------------------------

MODEL_PATH = "ai/data/risk_model.pkl"


# ---------------------------------------------
# Feature columns
# ---------------------------------------------

FEATURE_COLUMNS = [
    "ads_count",
    "trackers_count",
    "normal_resources_count",
    "total_resources",
    "third_party_count",
    "tracker_ratio",
    "third_party_ratio",
    "rule_based_risk_score"
]


# ---------------------------------------------
# Load trained model
# ---------------------------------------------

model = joblib.load(
    MODEL_PATH
)


def predict_risk(features):
    """
    Predict webpage risk using the trained ML model.
    """

    input_data = pd.DataFrame(
        [features],
        columns=FEATURE_COLUMNS
    )

    prediction = model.predict(
        input_data
    )[0]

    probabilities = model.predict_proba(
        input_data
    )[0]

    risk_probability = float(
        probabilities[1]
    )

    if prediction == 1:
        risk_label = "HIGH"
    else:
        risk_label = "LOW"

    return {
        "ml_prediction": int(prediction),
        "ml_risk_label": risk_label,
        "ml_risk_probability": round(
            risk_probability,
            4
        )
    }
