import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from detection.detector import detect_resources
from detection.risk_score import calculate_risk_score, get_risk_level

from ai.feature_extractor import extract_features
from ai.predict import predict_risk
from ai.risk_decision import calculate_final_risk


def fetch_webpage(url):
    """
    Fetch webpage HTML from the given URL.
    """

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/151.0 Safari/537.36"
                )
            }
        )

        response.raise_for_status()

        return response.text

    except requests.exceptions.RequestException as e:
        raise Exception(
            f"Unable to scan webpage: {str(e)}"
        )


def validate_url(url):
    """
    Validate that the URL is a complete HTTP/HTTPS URL.
    """

    try:
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        if not parsed.netloc:
            return False

        return True

    except Exception:
        return False


def extract_page_structure(html, base_url):
    """
    Extract webpage resources.

    Detects:
    - scripts
    - iframes
    - images
    - links
    """

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    scripts = []
    iframes = []
    images = []
    links = []

    # Scripts
    for tag in soup.find_all(
        "script",
        src=True
    ):
        resource_url = urljoin(
            base_url,
            tag.get("src")
        )
        scripts.append(resource_url)

    # Iframes
    for tag in soup.find_all(
        "iframe",
        src=True
    ):
        resource_url = urljoin(
            base_url,
            tag.get("src")
        )
        iframes.append(resource_url)

    # Images
    for tag in soup.find_all(
        "img",
        src=True
    ):
        resource_url = urljoin(
            base_url,
            tag.get("src")
        )
        images.append(resource_url)

    # Links
    for tag in soup.find_all(
        "a",
        href=True
    ):
        resource_url = urljoin(
            base_url,
            tag.get("href")
        )
        links.append(resource_url)

    # Remove duplicates
    scripts = list(dict.fromkeys(scripts))
    iframes = list(dict.fromkeys(iframes))
    images = list(dict.fromkeys(images))
    links = list(dict.fromkeys(links))

    # Page domain
    page_domain = urlparse(
        base_url
    ).netloc.lower()

    external_scripts = []
    external_iframes = []
    external_images = []
    external_links = []

    # External scripts
    for resource_url in scripts:

        domain = urlparse(
            resource_url
        ).netloc.lower()

        if domain and domain != page_domain:
            external_scripts.append(
                resource_url
            )

    # External iframes
    for resource_url in iframes:

        domain = urlparse(
            resource_url
        ).netloc.lower()

        if domain and domain != page_domain:
            external_iframes.append(
                resource_url
            )

    # External images
    for resource_url in images:

        domain = urlparse(
            resource_url
        ).netloc.lower()

        if domain and domain != page_domain:
            external_images.append(
                resource_url
            )

    # External links
    for resource_url in links:

        domain = urlparse(
            resource_url
        ).netloc.lower()

        if domain and domain != page_domain:
            external_links.append(
                resource_url
            )

    return {
        "scripts": scripts,
        "iframes": iframes,
        "images": images,
        "links": links,
        "external_scripts": external_scripts,
        "external_iframes": external_iframes,
        "external_images": external_images,
        "external_links": external_links
    }


def scan_webpage(url):
    """
    Complete webpage scanning pipeline.

    Steps:
    1. Validate URL
    2. Fetch webpage
    3. Extract HTML structure
    4. Detect resources
    5. Calculate rule-based risk
    6. Extract AI features
    7. Run ML prediction
    8. Calculate final risk
    9. Return complete result
    """

    # ---------------------------------------------
    # Validate URL
    # ---------------------------------------------

    if not validate_url(url):

        raise ValueError(
            "Invalid URL. Please provide a complete URL "
            "starting with http:// or https://"
        )

    # ---------------------------------------------
    # Fetch webpage
    # ---------------------------------------------

    html = fetch_webpage(url)

    # ---------------------------------------------
    # Extract webpage structure
    # ---------------------------------------------

    structure = extract_page_structure(
        html,
        url
    )

    # ---------------------------------------------
    # Detect resources
    # ---------------------------------------------

    detection_result = detect_resources(
        structure,
        url
    )

    # ---------------------------------------------
    # Count resources
    # ---------------------------------------------

    ads_count = len(
        detection_result["ads"]
    )

    trackers_count = len(
        detection_result["trackers"]
    )

    normal_count = len(
        detection_result["normal_resources"]
    )

    total_resources = (
        ads_count
        + trackers_count
        + normal_count
    )

    # ---------------------------------------------
    # Rule-based risk
    # ---------------------------------------------

    risk_score = calculate_risk_score(
        ads_count,
        trackers_count
    )

    risk_level = get_risk_level(
        risk_score
    )

    # ---------------------------------------------
    # Initial scan result
    # ---------------------------------------------

    scan_result = {
        "url": url,

        "page_structure": structure,

        "detection": {
            "ads": detection_result["ads"],
            "trackers": detection_result["trackers"],
            "normal_resources": detection_result[
                "normal_resources"
            ],
            "total_resources": total_resources
        },

        "risk_score": risk_score,
        "risk_level": risk_level
    }

    # ---------------------------------------------
    # AI feature extraction
    # ---------------------------------------------

    ai_features = extract_features(
        scan_result
    )

    scan_result["ai_features"] = ai_features

    # ---------------------------------------------
    # ML prediction
    # ---------------------------------------------

    ml_prediction = predict_risk(
        ai_features
    )

    scan_result["ml_prediction"] = ml_prediction

    # ---------------------------------------------
    # Final risk decision
    # ---------------------------------------------

    final_risk = calculate_final_risk(
        rule_based_score=risk_score,
        rule_based_level=risk_level,
        ml_prediction=ml_prediction[
            "ml_prediction"
        ],
        ml_probability=ml_prediction[
            "ml_risk_probability"
        ]
    )

    scan_result["final_risk"] = final_risk

    # ---------------------------------------------
    # Return final result
    # ---------------------------------------------

    return scan_result


