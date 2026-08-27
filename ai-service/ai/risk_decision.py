def calculate_final_risk(
    rule_based_score,
    rule_based_level,
    ml_prediction,
    ml_probability
):
    """
    Combine rule-based analysis and ML prediction
    into one final risk assessment.
    """

    # ---------------------------------------------
    # Normalize values
    # ---------------------------------------------

    rule_based_score = float(
        rule_based_score
    )

    ml_probability = float(
        ml_probability
    )

    ml_prediction = int(
        ml_prediction
    )

    # ---------------------------------------------
    # Start with rule-based score
    # ---------------------------------------------

    final_score = rule_based_score

    # ---------------------------------------------
    # ML influence
    # ---------------------------------------------

    # High ML prediction
    if ml_prediction == 1:

        # Increase confidence in higher risk
        final_score = max(
            final_score,
            ml_probability * 100
        )

    # ---------------------------------------------
    # Medium ML probability
    # ---------------------------------------------

    elif ml_probability >= 0.50:

        final_score = max(
            final_score,
            ml_probability * 100
        )

    # ---------------------------------------------
    # Limit score to 0-100
    # ---------------------------------------------

    final_score = min(
        max(final_score, 0),
        100
    )

    # ---------------------------------------------
    # Determine final risk level
    # ---------------------------------------------

    if final_score < 30:

        final_level = "LOW"

    elif final_score < 60:

        final_level = "MEDIUM"

    else:

        final_level = "HIGH"

    # ---------------------------------------------
    # Confidence
    # ---------------------------------------------

    if (
        rule_based_level == final_level
        and (
            (ml_prediction == 0 and final_level == "LOW")
            or
            (ml_prediction == 1 and final_level == "HIGH")
        )
    ):

        confidence = "HIGH"

    elif rule_based_level == final_level:

        confidence = "MEDIUM"

    else:

        confidence = "LOW"

    # ---------------------------------------------
    # Return final decision
    # ---------------------------------------------

    return {
        "final_risk_score": round(
            final_score,
            2
        ),

        "final_risk_level": final_level,

        "confidence": confidence
    }
