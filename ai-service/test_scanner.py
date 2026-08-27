from webpage_scanner import scan_webpage


TEST_URLS = [
    "https://example.com",
    "https://www.wikipedia.org",
    "https://www.python.org"
]


for url in TEST_URLS:

    print("\n" + "=" * 60)
    print("URL:", url)
    print("=" * 60)

    try:
        result = scan_webpage(url)

        print(
            "Rule-based risk:",
            result["risk_level"],
            f"({result['risk_score']})"
        )

        print(
            "Ads:",
            result["ai_features"]["ads_count"]
        )

        print(
            "Trackers:",
            result["ai_features"]["trackers_count"]
        )

        print(
            "Total resources:",
            result["ai_features"]["total_resources"]
        )

        print(
            "Third-party resources:",
            result["ai_features"]["third_party_count"]
        )

        print(
            "ML prediction:",
            result["ml_prediction"]["ml_risk_label"]
        )

        print(
            "ML probability:",
            result["ml_prediction"]["ml_risk_probability"]
        )

        print(
            "Security findings:",
            result["security_analysis"]["summary"]
            if "security_analysis" in result
            else "Not available"
        )

    except Exception as e:

        print(
            "ERROR:",
            str(e)
        )
