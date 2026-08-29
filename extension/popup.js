// AdvSystem - Privacy & Cookie Scanner
// Phase 3: Popup Controller


const websiteElement = document.getElementById("website");
const scanButton = document.getElementById("scanButton");
const statusElement = document.getElementById("status");
const resultsElement = document.getElementById("results");
const cookieListElement = document.getElementById("cookieList");

let currentTabUrl = null;


// Get the currently active Chrome tab
async function getCurrentTab() {
    const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    return tabs[0];
}


// Initialize popup
async function initialize() {
    try {
        const tab = await getCurrentTab();

        if (!tab || !tab.url) {
            websiteElement.textContent =
                "Unable to detect website.";

            scanButton.disabled = true;

            return;
        }

        currentTabUrl = tab.url;

        const url = new URL(tab.url);

        if (
            url.protocol !== "http:" &&
            url.protocol !== "https:"
        ) {
            websiteElement.textContent =
                "This page cannot be scanned.";

            scanButton.disabled = true;

            statusElement.textContent =
                "Please open a normal HTTP or HTTPS website.";

            return;
        }

        websiteElement.textContent = url.hostname;

    } catch (error) {
        console.error(
            "Popup initialization error:",
            error
        );

        websiteElement.textContent =
            "Unable to detect website.";

        scanButton.disabled = true;

        statusElement.innerHTML =
            `<span class="error">
                Unable to detect the current website.
            </span>`;
    }
}


// Scan cookies
scanButton.addEventListener("click", async () => {

    if (!currentTabUrl) {
        return;
    }

    scanButton.disabled = true;

    statusElement.textContent =
        "Scanning cookies...";

    resultsElement.innerHTML = "";

    cookieListElement.innerHTML = "";

    try {

        const response = await chrome.runtime.sendMessage({
            action: "scanCookies",
            url: currentTabUrl
        });


        if (!response || !response.success) {

            throw new Error(
                response?.error ||
                "Cookie scan failed."
            );
        }


        displayResults(response.data);


        statusElement.textContent =
            "Cookie scan completed successfully.";

    } catch (error) {

        console.error(
            "Cookie scan error:",
            error
        );

        statusElement.innerHTML =
            `<span class="error">
                Error: ${escapeHtml(error.message)}
            </span>`;
    }


    scanButton.disabled = false;
});


// Display scan results
function displayResults(data) {

    resultsElement.innerHTML = `
        <div class="result-card">
            <div class="result-label">
                Total Cookies
            </div>

            <div class="result-value">
                ${data.totalCookies}
            </div>
        </div>


        <div class="result-card">
            <div class="result-label">
                First-Party Cookies
            </div>

            <div class="result-value">
                ${data.firstPartyCookies}
            </div>
        </div>


        <div class="result-card">
            <div class="result-label">
                Third-Party Cookies
            </div>

            <div class="result-value">
                ${data.thirdPartyCookies}
            </div>
        </div>
    `;


    if (!data.cookies || data.cookies.length === 0) {

        cookieListElement.innerHTML = `
            <div class="cookie-item">
                No cookies detected.
            </div>
        `;

        return;
    }


    const limitedCookies =
        data.cookies.slice(0, 20);


    cookieListElement.innerHTML = `
        <h3>Cookie Metadata</h3>

        ${limitedCookies.map((cookie) => `

            <div class="cookie-item">

                <div class="cookie-name">
                    ${escapeHtml(cookie.name)}
                </div>


                <div class="cookie-detail">
                    Domain:
                    ${escapeHtml(cookie.domain)}
                </div>


                <div class="cookie-detail">
                    Path:
                    ${escapeHtml(cookie.path)}
                </div>


                <div class="cookie-detail">
                    Secure:
                    ${cookie.secure ? "Yes" : "No"}
                </div>


                <div class="cookie-detail">
                    HttpOnly:
                    ${cookie.httpOnly ? "Yes" : "No"}
                </div>


                <div class="cookie-detail">
                    SameSite:
                    ${escapeHtml(cookie.sameSite)}
                </div>


                <div class="cookie-detail">
                    Type:
                    ${
                        cookie.thirdParty
                            ? "Third-Party"
                            : "First-Party"
                    }
                </div>

            </div>

        `).join("")}
    `;


    if (data.cookies.length > 20) {

        cookieListElement.innerHTML += `
            <div class="cookie-item">
                Showing first 20 cookies only.
            </div>
        `;
    }
}


// Prevent HTML injection when displaying cookie metadata
function escapeHtml(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// Start popup
initialize();