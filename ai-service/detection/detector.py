from urllib.parse import urlparse
import re

from .ad_rules import AD_KEYWORDS, AD_DOMAINS
from .tracker_rules import TRACKER_KEYWORDS, TRACKER_DOMAINS


def unique_matches(matches):
    return list(dict.fromkeys(matches))


def detect_content(text):
    text_lower = text.lower()

    detected_ads = []

    for keyword in AD_KEYWORDS:
        keyword_lower = keyword.lower()

        if keyword_lower in text_lower:
            detected_ads.append(keyword)

    detected_ad_domains = [
        domain
        for domain in AD_DOMAINS
        if domain.lower() in text_lower
    ]

    detected_trackers = []

    for keyword in TRACKER_KEYWORDS:
        keyword_lower = keyword.lower()

        if keyword_lower.startswith("/"):
            pattern = re.escape(keyword_lower) + r"(?=/|$)"

            if re.search(pattern, text_lower):
                detected_trackers.append(keyword)

        elif keyword_lower.endswith("/"):
            if keyword_lower in text_lower:
                detected_trackers.append(keyword)

        else:
            if keyword_lower in text_lower:
                detected_trackers.append(keyword)

    detected_tracker_domains = [
        domain
        for domain in TRACKER_DOMAINS
        if domain.lower() in text_lower
    ]

    return {
        "ads": unique_matches(
            detected_ads + detected_ad_domains
        ),
        "trackers": unique_matches(
            detected_trackers + detected_tracker_domains
        )
    }


def extract_domain(url):
    parsed_url = urlparse(url)

    return parsed_url.netloc.lower()


def get_base_domain(domain):
    """
    Get the main domain used for first-party comparison.

    Example:
    www.example.com -> example.com
    cdn.example.com -> example.com
    """

    parts = domain.split(".")

    if len(parts) >= 2:
        return ".".join(parts[-2:])

    return domain


def is_third_party(resource_url, page_url):
    """
    Determine whether a resource belongs to another domain.
    """

    resource_domain = extract_domain(resource_url)
    page_domain = extract_domain(page_url)

    if not resource_domain or not page_domain:
        return False

    resource_base = get_base_domain(resource_domain)
    page_base = get_base_domain(page_domain)

    return resource_base != page_base


def detect_resources(page_structure, page_url=""):
    """
    Analyze resources extracted from a webpage.

    Each resource is checked for:
    - advertisements
    - trackers
    - first-party / third-party origin
    """

    detected_ads = []
    detected_trackers = []
    normal_resources = []

    resource_types = {
        "scripts": page_structure.get(
            "external_scripts", []
        ),
        "iframes": page_structure.get(
            "external_iframes", []
        ),
        "images": page_structure.get(
            "external_images", []
        ),
        "links": page_structure.get(
            "external_links", []
        )
    }

    for resource_type, resources in resource_types.items():

        for url in resources:

            result = detect_content(url)

            resource_info = {
                "url": url,
                "type": resource_type,
                "domain": extract_domain(url)
            }

            if page_url:
                if is_third_party(url, page_url):
                    resource_info["resource_origin"] = "third-party"
                else:
                    resource_info["resource_origin"] = "first-party"

            if result["ads"]:

                resource_info["matches"] = result["ads"]

                detected_ads.append(
                    resource_info
                )

            elif result["trackers"]:

                resource_info["matches"] = result["trackers"]

                detected_trackers.append(
                    resource_info
                )

            else:

                normal_resources.append(
                    resource_info
                )

    return {
        "ads": detected_ads,
        "trackers": detected_trackers,
        "normal_resources": normal_resources
    }