// AdvSystem - Cookie Scanner
// Phase 3: Cookies & Tracking Information

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "scanCookies") {
        scanCookies(message.url)
            .then((result) => {
                sendResponse({
                    success: true,
                    data: result
                });
            })
            .catch((error) => {
                console.error("Cookie scan error:", error);

                sendResponse({
                    success: false,
                    error: error.message
                });
            });

        return true;
    }
});


async function scanCookies(url) {
    if (!url) {
        throw new Error("Website URL is required.");
    }

    const cookies = await chrome.cookies.getAll({
        url: url
    });

    const websiteUrl = new URL(url);
    const websiteHostname = websiteUrl.hostname;

    const cookieMetadata = cookies.map((cookie) => {
        const isFirstParty = isFirstPartyCookie(
            cookie.domain,
            websiteHostname
        );

        return {
            name: cookie.name,
            domain: cookie.domain,
            path: cookie.path,
            secure: cookie.secure,
            httpOnly: cookie.httpOnly,
            sameSite: cookie.sameSite,
            expirationDate: cookie.expirationDate || null,
            firstParty: isFirstParty,
            thirdParty: !isFirstParty
        };
    });

    const firstPartyCookies = cookieMetadata.filter(
        (cookie) => cookie.firstParty
    );

    const thirdPartyCookies = cookieMetadata.filter(
        (cookie) => cookie.thirdParty
    );

    return {
        website: websiteHostname,

        totalCookies: cookieMetadata.length,

        firstPartyCookies: firstPartyCookies.length,

        thirdPartyCookies: thirdPartyCookies.length,

        cookies: cookieMetadata
    };
}


function isFirstPartyCookie(cookieDomain, websiteHostname) {
    const cleanCookieDomain = cookieDomain.startsWith(".")
        ? cookieDomain.substring(1)
        : cookieDomain;

    return (
        websiteHostname === cleanCookieDomain ||
        websiteHostname.endsWith("." + cleanCookieDomain)
    );
}