from detection.detector import detect_content, extract_domain
from detection.risk_score import calculate_risk_score


def test_clean_content():
    result = detect_content(
        "Welcome to our educational website."
    )

    assert result["ads"] == []
    assert result["trackers"] == []


def test_ad_detection():
    result = detect_content(
        "This is an advertisement."
    )

    assert "advertisement" in result["ads"]


def test_tracker_detection():
    result = detect_content(
        "This website uses analytics tracking."
    )

    assert "analytics" in result["trackers"]
    assert "tracking" in result["trackers"]


def test_ad_domain():
    result = detect_content(
        "Content loaded from doubleclick.net"
    )

    assert "doubleclick.net" in result["ads"]


def test_tracker_domain():
    result = detect_content(
        "Analytics from google-analytics.com"
    )

    assert "google-analytics.com" in result["trackers"]


def test_risk_score():
    assert calculate_risk_score(1, 2) == 50


def test_domain_extraction():
    assert extract_domain(
        "https://example.com/page"
    ) == "example.com"