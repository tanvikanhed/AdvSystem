from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


def scan_browser_cookies(url):
    """
    Open a webpage in Chromium and collect cookies
    available after the page finishes loading.
    """

    parsed_url = urlparse(url)

    page_domain = (
        parsed_url.hostname or ""
    ).lower()

    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=True
        )

        context = browser.new_context()

        page = context.new_page()

        try:
            page.goto(
                url,
                wait_until="networkidle",
                timeout=30000
            )

            cookies = context.cookies()

        finally:
            browser.close()

    analyzed_cookies = []

    first_party_count = 0
    third_party_count = 0
    secure_count = 0
    httponly_count = 0

    for cookie in cookies:

        cookie_domain = (
            cookie.get("domain", "")
            .lower()
            .lstrip(".")
        )

        is_third_party = True

        if cookie_domain == page_domain:
            is_third_party = False

        elif page_domain.endswith(
            "." + cookie_domain
        ):
            is_third_party = False

        cookie_data = {
            "name": cookie.get(
                "name",
                ""
            ),

            "domain": cookie.get(
                "domain",
                ""
            ),

            "path": cookie.get(
                "path",
                "/"
            ),

            "secure": bool(
                cookie.get(
                    "secure",
                    False
                )
            ),

            "httponly": bool(
                cookie.get(
                    "httpOnly",
                    False
                )
            ),

            "samesite": cookie.get(
                "sameSite",
                "Not specified"
            ),

            "expires": cookie.get(
                "expires"
            ),

            "third_party": is_third_party
        }

        analyzed_cookies.append(
            cookie_data
        )

        if is_third_party:
            third_party_count += 1
        else:
            first_party_count += 1

        if cookie_data["secure"]:
            secure_count += 1

        if cookie_data["httponly"]:
            httponly_count += 1

    return {
        "cookies": analyzed_cookies,

        "total_cookies": len(
            analyzed_cookies
        ),

        "first_party_cookies":
            first_party_count,

        "third_party_cookies":
            third_party_count,

        "secure_cookies":
            secure_count,

        "httponly_cookies":
            httponly_count
    }