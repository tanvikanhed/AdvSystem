from urllib.parse import urlparse


def get_cookie_domain(cookie):
    """Return the cookie domain."""
    return cookie.domain or ""


def is_cookie_secure(cookie):
    """Check whether the cookie has the Secure attribute."""
    return bool(cookie.secure)


def is_cookie_httponly(cookie):
    """Check whether the cookie has the HttpOnly attribute."""
    rest = getattr(cookie, "_rest", {})

    for key in rest:
        if str(key).lower() == "httponly":
            return True

    return False


def get_cookie_samesite(cookie):
    """Return the SameSite attribute when available."""
    rest = getattr(cookie, "_rest", {})

    for key, value in rest.items():
        if str(key).lower() == "samesite":
            return str(value)

    return "Not specified"


def get_cookie_expires(cookie):
    """Return the cookie expiration timestamp."""
    return cookie.expires


def is_third_party_cookie(cookie_domain, page_domain):
    """Determine whether a cookie belongs to another domain."""

    if not cookie_domain or not page_domain:
        return False

    cookie_domain = cookie_domain.lower().lstrip(".")
    page_domain = page_domain.lower().lstrip(".")

    if cookie_domain == page_domain:
        return False

    if page_domain.endswith("." + cookie_domain):
        return False

    return True


def analyze_cookie(cookie, page_domain):
    """Convert a requests cookie into structured metadata."""

    cookie_domain = get_cookie_domain(cookie)

    return {
        "name": cookie.name,
        "domain": cookie_domain,
        "path": cookie.path or "/",
        "secure": is_cookie_secure(cookie),
        "httponly": is_cookie_httponly(cookie),
        "samesite": get_cookie_samesite(cookie),
        "expires": get_cookie_expires(cookie),
        "third_party": is_third_party_cookie(
            cookie_domain,
            page_domain
        )
    }


def analyze_cookies(response, page_url):
    """
    Analyze cookies received from the HTTP response.

    Returns cookie metadata and summary statistics.
    """

    parsed_url = urlparse(page_url)

    page_domain = (
        parsed_url.hostname or ""
    ).lower()

    cookies = []

    first_party_count = 0
    third_party_count = 0
    secure_count = 0
    httponly_count = 0

    for cookie in response.cookies:
        cookie_data = analyze_cookie(
            cookie,
            page_domain
        )

        cookies.append(cookie_data)

        if cookie_data["third_party"]:
            third_party_count += 1
        else:
            first_party_count += 1

        if cookie_data["secure"]:
            secure_count += 1

        if cookie_data["httponly"]:
            httponly_count += 1

    return {
        "cookies": cookies,
        "total_cookies": len(cookies),
        "first_party_cookies": first_party_count,
        "third_party_cookies": third_party_count,
        "secure_cookies": secure_count,
        "httponly_cookies": httponly_count
    }