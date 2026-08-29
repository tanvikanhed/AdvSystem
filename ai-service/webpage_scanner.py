import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from detection.detector import detect_resources
from detection.risk_score import calculate_risk_score, get_risk_level

from ai.feature_extractor import extract_features
from ai.predict import predict_risk
from ai.risk_decision import calculate_final_risk

from cookie_scanner.cookie_detector import analyze_cookies
from cookie_scanner.browser_cookie_scanner import scan_browser_cookies



def fetch_webpage(url):
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

        return response

    except requests.exceptions.RequestException as e:
        raise Exception(
            f"Unable to scan webpage: {str(e)}"
        )


def validate_url(url):
    try:
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        if not parsed.netloc:
            return False

        return True

    except Exception:
        return False


def get_domain(url):
    try:
        domain = urlparse(url).netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    except Exception:
        return ""


def analyze_url_security(url):
    """
    Analyze URL and domain characteristics.
    """

    parsed = urlparse(url)

    hostname = parsed.hostname or ""
    domain = get_domain(url)

    issues = []
    warnings = []

    uses_https = parsed.scheme.lower() == "https"

    if not uses_https:
        issues.append(
            "Website does not use HTTPS."
        )

    is_ip_address = False

    try:
        parts = hostname.split(".")

        if (
            len(parts) == 4
            and all(
                part.isdigit()
                and 0 <= int(part) <= 255
                for part in parts
            )
        ):
            is_ip_address = True

    except Exception:
        is_ip_address = False

    if is_ip_address:
        issues.append(
            "URL uses an IP address instead of a domain name."
        )

    url_length = len(url)

    if url_length > 200:
        warnings.append(
            "URL is unusually long."
        )

    subdomain_count = max(
        0,
        len(hostname.split(".")) - 2
    )

    if subdomain_count >= 3:
        warnings.append(
            "URL contains an unusually high number of subdomains."
        )

    suspicious_characters = [
        "@",
        "\\",
        "<",
        ">",
        "{",
        "}"
    ]

    found_suspicious_characters = [
        char
        for char in suspicious_characters
        if char in url
    ]

    if found_suspicious_characters:
        issues.append(
            "URL contains suspicious characters."
        )

    encoded_count = url.count("%")

    if encoded_count >= 5:
        warnings.append(
            "URL contains a high amount of encoded characters."
        )

    suspicious_keywords = [
        "login",
        "verify",
        "verification",
        "secure",
        "account",
        "update",
        "password",
        "signin",
        "confirm"
    ]

    url_lower = url.lower()

    detected_keywords = [
        keyword
        for keyword in suspicious_keywords
        if keyword in url_lower
    ]

    if len(detected_keywords) >= 3:
        warnings.append(
            "URL contains multiple security-sensitive keywords."
        )

    unusual_port = False

    try:
        port = parsed.port

        if port and port not in (
            80,
            443
        ):
            unusual_port = True

            warnings.append(
                f"Website uses an unusual port ({port})."
            )

    except ValueError:
        issues.append(
            "URL contains an invalid port."
        )

    issue_count = len(issues)
    warning_count = len(warnings)

    if issue_count >= 2:
        security_level = "HIGH"

    elif issue_count == 1 or warning_count >= 2:
        security_level = "MEDIUM"

    elif warning_count == 1:
        security_level = "LOW"

    else:
        security_level = "SAFE"

    security_score = (
        issue_count * 30
        + warning_count * 15
    )

    security_score = min(
        security_score,
        100
    )

    return {
        "domain": domain,
        "hostname": hostname,
        "protocol": parsed.scheme.lower(),
        "uses_https": uses_https,
        "is_ip_address": is_ip_address,
        "url_length": url_length,
        "subdomain_count": subdomain_count,
        "encoded_character_count": encoded_count,
        "detected_keywords": detected_keywords,
        "suspicious_characters": found_suspicious_characters,
        "unusual_port": unusual_port,
        "issues": issues,
        "warnings": warnings,
        "security_score": security_score,
        "security_level": security_level
    }


def is_external(resource_url, page_domain):
    resource_domain = get_domain(resource_url)

    if not resource_domain:
        return False

    return resource_domain != page_domain


def extract_page_structure(html, base_url):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    scripts = []
    iframes = []
    images = []
    links = []

    for tag in soup.find_all(
        "script",
        src=True
    ):
        src = tag.get("src")

        if src:
            scripts.append(
                urljoin(base_url, src)
            )

    for tag in soup.find_all(
        "iframe",
        src=True
    ):
        src = tag.get("src")

        if src:
            iframes.append(
                urljoin(base_url, src)
            )

    for tag in soup.find_all(
        "img",
        src=True
    ):
        src = tag.get("src")

        if src:
            images.append(
                urljoin(base_url, src)
            )

    for tag in soup.find_all(
        "a",
        href=True
    ):
        href = tag.get("href")

        if href:
            links.append(
                urljoin(base_url, href)
            )

    scripts = list(
        dict.fromkeys(scripts)
    )

    iframes = list(
        dict.fromkeys(iframes)
    )

    images = list(
        dict.fromkeys(images)
    )

    links = list(
        dict.fromkeys(links)
    )

    page_domain = get_domain(
        base_url
    )

    external_scripts = [
        url
        for url in scripts
        if is_external(
            url,
            page_domain
        )
    ]

    external_iframes = [
        url
        for url in iframes
        if is_external(
            url,
            page_domain
        )
    ]

    external_images = [
        url
        for url in images
        if is_external(
            url,
            page_domain
        )
    ]

    external_links = [
        url
        for url in links
        if is_external(
            url,
            page_domain
        )
    ]

    all_external_resources = (
        external_scripts
        + external_iframes
        + external_images
    )

    third_party_domains = []

    for resource_url in all_external_resources:

        domain = get_domain(
            resource_url
        )

        if (
            domain
            and domain != page_domain
            and domain not in third_party_domains
        ):
            third_party_domains.append(
                domain
            )

    third_party_domains.sort()

    third_party_resource_count = (
        len(external_scripts)
        + len(external_iframes)
        + len(external_images)
    )

    return {
        "scripts": scripts,
        "iframes": iframes,
        "images": images,
        "links": links,

        "external_scripts": external_scripts,
        "external_iframes": external_iframes,
        "external_images": external_images,
        "external_links": external_links,

        "page_domain": page_domain,

        "third_party_domains": third_party_domains,

        "third_party_domain_count": len(
            third_party_domains
        ),

        "external_script_count": len(
            external_scripts
        ),

        "external_iframe_count": len(
            external_iframes
        ),

        "external_image_count": len(
            external_images
        ),

        "external_link_count": len(
            external_links
        ),

        "third_party_resource_count":
            third_party_resource_count
    }


def scan_webpage(url):

    if not validate_url(url):
        raise ValueError(
            "Invalid URL. Please provide a complete URL "
            "starting with http:// or https://"
        )

    response = fetch_webpage(url)

    html = response.text

    structure = extract_page_structure(
        html,
        url
    )

    url_security = analyze_url_security(
        url
    )

    detection_result = detect_resources(
        structure,
        url
    )

    ads_count = len(
        detection_result.get(
            "ads",
            []
        )
    )

    trackers_count = len(
        detection_result.get(
            "trackers",
            []
        )
    )

    normal_count = len(
        detection_result.get(
            "normal_resources",
            []
        )
    )

    total_resources = (
        ads_count
        + trackers_count
        + normal_count
    )

    risk_score = calculate_risk_score(
        ads_count,
        trackers_count
    )

    risk_level = get_risk_level(
        risk_score
    )

    third_party_analysis = {
        "page_domain": structure.get(
            "page_domain",
            ""
        ),

        "third_party_domains":
            structure.get(
                "third_party_domains",
                []
            ),

        "third_party_domain_count":
            structure.get(
                "third_party_domain_count",
                0
            ),

        "external_script_count":
            structure.get(
                "external_script_count",
                0
            ),

        "external_iframe_count":
            structure.get(
                "external_iframe_count",
                0
            ),

        "external_image_count":
            structure.get(
                "external_image_count",
                0
            ),

        "external_link_count":
            structure.get(
                "external_link_count",
                0
            ),

        "third_party_resource_count":
            structure.get(
                "third_party_resource_count",
                0
            )
    }

    cookie_analysis = analyze_cookies(
        response,
        url
    )
    browser_cookie_analysis = scan_browser_cookies(
    url
    )

    scan_result = {
        "url": url,

        "page_structure": structure,

        "url_security": url_security,

        "third_party_analysis":
            third_party_analysis,

        "cookies": cookie_analysis,
        "browser_cookies": browser_cookie_analysis,

        "detection": {
            "ads": detection_result.get(
                "ads",
                []
            ),

            "trackers": detection_result.get(
                "trackers",
                []
            ),

            "normal_resources":
                detection_result.get(
                    "normal_resources",
                    []
                ),

            "total_resources":
                total_resources
        },

        "risk_score": risk_score,

        "risk_level": risk_level
    }

    ai_features = extract_features(
        scan_result
    )

    scan_result["ai_features"] = (
        ai_features
    )

    ml_prediction = predict_risk(
        ai_features
    )

    scan_result["ml_prediction"] = (
        ml_prediction
    )

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

    scan_result["final_risk"] = (
        final_risk
    )

    return scan_result