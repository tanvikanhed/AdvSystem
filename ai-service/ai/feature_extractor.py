def extract_features(scan_result):
    """
    Convert webpage scan results into numerical
    features for the machine-learning model.
    """

    detection = scan_result.get("detection", {})

    ads = detection.get("ads", [])
    trackers = detection.get("trackers", [])
    normal_resources = detection.get(
        "normal_resources", []
    )

    total_resources = detection.get(
        "total_resources", 0
    )

    risk_score = scan_result.get(
        "risk_score", 0
    )

    # Resource counts
    ads_count = len(ads)
    trackers_count = len(trackers)
    normal_resources_count = len(
        normal_resources
    )

    # All detected resources
    all_resources = (
        ads
        + trackers
        + normal_resources
    )

    # Third-party resources
    third_party_count = sum(
        1
        for resource in all_resources
        if resource.get("resource_origin")
        == "third-party"
    )

    # Ratios
    if total_resources > 0:
        tracker_ratio = (
            trackers_count / total_resources
        )

        third_party_ratio = (
            third_party_count
            / total_resources
        )
    else:
        tracker_ratio = 0.0
        third_party_ratio = 0.0

    return {
        "ads_count": ads_count,
        "trackers_count": trackers_count,
        "normal_resources_count":
            normal_resources_count,
        "total_resources":
            total_resources,
        "third_party_count":
            third_party_count,
        "tracker_ratio":
            round(tracker_ratio, 4),
        "third_party_ratio":
            round(third_party_ratio, 4),
        "rule_based_risk_score":
            risk_score
    }