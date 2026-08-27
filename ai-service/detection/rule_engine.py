def analyze_security_rules(scan_result):
    """
    Rule-based security analysis.

    Takes the result produced by the webpage scanner
    and generates security/privacy findings.
    """

    findings = []

    ads = scan_result.get("detection", {}).get(
        "ads", []
    )

    trackers = scan_result.get("detection", {}).get(
        "trackers", []
    )

    normal_resources = scan_result.get(
        "detection", {}
    ).get(
        "normal_resources", []
    )

    total_resources = scan_result.get(
        "detection", {}
    ).get(
        "total_resources",
        0
    )

    risk_score = scan_result.get(
        "risk_score",
        0
    )

    # ---------------------------------------------
    # RULE 1 — Advertisements
    # ---------------------------------------------

    if len(ads) > 0:

        findings.append({
            "rule": "ADVERTISEMENT_DETECTED",
            "severity": "LOW",
            "title": "Advertisement detected",
            "description": (
                f"{len(ads)} advertisement resource(s) "
                "were detected on the webpage."
            ),
            "count": len(ads)
        })

    # ---------------------------------------------
    # RULE 2 — Trackers
    # ---------------------------------------------

    if len(trackers) > 0:

        findings.append({
            "rule": "TRACKER_DETECTED",
            "severity": "MEDIUM",
            "title": "Tracking resource detected",
            "description": (
                f"{len(trackers)} tracking resource(s) "
                "were detected."
            ),
            "count": len(trackers)
        })

    # ---------------------------------------------
    # RULE 3 — Multiple trackers
    # ---------------------------------------------

    if len(trackers) >= 3:

        findings.append({
            "rule": "MULTIPLE_TRACKERS",
            "severity": "HIGH",
            "title": "Multiple trackers detected",
            "description": (
                "The webpage contains multiple "
                "tracking resources which may "
                "increase privacy risk."
            ),
            "count": len(trackers)
        })

    # ---------------------------------------------
    # RULE 4 — Many advertisements
    # ---------------------------------------------

    if len(ads) >= 3:

        findings.append({
            "rule": "EXCESSIVE_ADVERTISEMENTS",
            "severity": "MEDIUM",
            "title": "Multiple advertisements detected",
            "description": (
                "The webpage contains a relatively "
                "large number of advertisement resources."
            ),
            "count": len(ads)
        })

    # ---------------------------------------------
    # RULE 5 — Third-party resources
    # ---------------------------------------------

    third_party_count = 0

    all_resources = (
        ads
        + trackers
        + normal_resources
    )

    for resource in all_resources:

        if resource.get(
            "resource_origin"
        ) == "third-party":

            third_party_count += 1

    if third_party_count > 0:

        findings.append({
            "rule": "THIRD_PARTY_RESOURCE",
            "severity": "LOW",
            "title": "Third-party resources detected",
            "description": (
                f"{third_party_count} resource(s) "
                "come from third-party domains."
            ),
            "count": third_party_count
        })

    # ---------------------------------------------
    # RULE 6 — Many external resources
    # ---------------------------------------------

    if total_resources >= 10:

        findings.append({
            "rule": "HIGH_EXTERNAL_RESOURCE_COUNT",
            "severity": "MEDIUM",
            "title": "Large number of external resources",
            "description": (
                "The webpage loads a large number "
                "of external resources."
            ),
            "count": total_resources
        })

    # ---------------------------------------------
    # RULE 7 — High overall risk
    # ---------------------------------------------

    if risk_score >= 60:

        findings.append({
            "rule": "HIGH_RISK_PAGE",
            "severity": "HIGH",
            "title": "High-risk webpage",
            "description": (
                "The combined advertisement and "
                "tracking activity produces a high "
                "risk score."
            ),
            "count": risk_score
        })

    # ---------------------------------------------
    # No issues
    # ---------------------------------------------

    if not findings:

        findings.append({
            "rule": "NO_SIGNIFICANT_RISK",
            "severity": "LOW",
            "title": "No significant risks detected",
            "description": (
                "The current rule set did not identify "
                "any significant security or privacy risks."
            ),
            "count": 0
        })

    # ---------------------------------------------
    # Summary
    # ---------------------------------------------

    high_count = sum(
        1
        for finding in findings
        if finding["severity"] == "HIGH"
    )

    medium_count = sum(
        1
        for finding in findings
        if finding["severity"] == "MEDIUM"
    )

    low_count = sum(
        1
        for finding in findings
        if finding["severity"] == "LOW"
    )

    return {
        "findings": findings,
        "summary": {
            "total_findings": len(findings),
            "high": high_count,
            "medium": medium_count,
            "low": low_count
        }
    }