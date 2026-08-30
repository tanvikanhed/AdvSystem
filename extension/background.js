// AdvSystem - Cookie Scanner
// Phase 3: Cookies & Tracking Information


chrome.runtime.onMessage.addListener(
    (message, sender, sendResponse) => {

        if (message.action === "scanCookies") {

            scanCookies(message.url)
                .then((result) => {

                    sendResponse({
                        success: true,
                        data: result
                    });

                })
                .catch((error) => {

                    console.error(
                        "Cookie scan error:",
                        error
                    );

                    sendResponse({
                        success: false,
                        error: error.message
                    });

                });

            return true;
        }
    }
);


// =========================================================
// COOKIE SCANNER
// =========================================================

async function scanCookies(url) {

    if (!url) {
        throw new Error(
            "Website URL is required."
        );
    }


    const websiteUrl = new URL(url);

    const websiteHostname =
        websiteUrl.hostname;


    const cookies =
        await chrome.cookies.getAll({
            url: url
        });


    const cookieMetadata =
        cookies.map((cookie) => {

            const isFirstParty =
                isFirstPartyCookie(
                    cookie.domain,
                    websiteHostname
                );


            return {

                name:
                    cookie.name,

                domain:
                    cookie.domain,

                path:
                    cookie.path,

                secure:
                    Boolean(cookie.secure),

                httpOnly:
                    Boolean(cookie.httpOnly),

                sameSite:
                    normalizeSameSite(
                        cookie.sameSite
                    ),

                expirationDate:
                    cookie.expirationDate || null,

                firstParty:
                    isFirstParty,

                thirdParty:
                    !isFirstParty
            };
        });


    const firstPartyCookies =
        cookieMetadata.filter(
            (cookie) =>
                cookie.firstParty
        );


    const thirdPartyCookies =
        cookieMetadata.filter(
            (cookie) =>
                cookie.thirdParty
        );


    return {

        website:
            websiteHostname,

        totalCookies:
            cookieMetadata.length,

        firstPartyCookies:
            firstPartyCookies.length,

        thirdPartyCookies:
            thirdPartyCookies.length,

        cookies:
            cookieMetadata
    };
}


// =========================================================
// SAME-SITE NORMALIZATION
// =========================================================

function normalizeSameSite(value) {

    if (!value) {
        return "Unspecified";
    }


    switch (value) {

        case "no_restriction":
            return "None";

        case "lax":
            return "Lax";

        case "strict":
            return "Strict";

        case "unspecified":
            return "Unspecified";

        default:
            return String(value);
    }
}


// =========================================================
// FIRST-PARTY / THIRD-PARTY DETECTION
// =========================================================

function isFirstPartyCookie(
    cookieDomain,
    websiteHostname
) {

    if (!cookieDomain) {
        return false;
    }


    const cleanCookieDomain =
        cookieDomain.startsWith(".")
            ? cookieDomain.substring(1)
            : cookieDomain;


    return (
        websiteHostname ===
            cleanCookieDomain
        ||
        websiteHostname.endsWith(
            "." + cleanCookieDomain
        )
    );
}