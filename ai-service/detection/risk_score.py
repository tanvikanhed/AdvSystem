def calculate_risk_score(ads_count, trackers_count):
    score = 0

    # Advertisements contribute 10 points each
    score += ads_count * 10

    # Trackers contribute 20 points each
    score += trackers_count * 20

    # Keep the score between 0 and 100
    score = min(score, 100)

    return score


def get_risk_level(score):
    if score < 30:
        return "LOW"

    elif score < 60:
        return "MEDIUM"

    else:
        return "HIGH"