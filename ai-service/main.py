import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from detection.detector import detect_content, extract_domain
from detection.risk_score import (
    calculate_risk_score,
    get_risk_level
)
from detection.rule_engine import analyze_security_rules
from webpage_scanner import scan_webpage


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="AdvSystem AI Security Scanner",
    description="Advertisement, Tracker and Web Security Analysis API",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# TEMPORARY SCAN HISTORY
# =========================================================
#
# MongoDB connection is temporarily disabled because the
# current network is causing a TLS handshake problem.
#
# We will reconnect MongoDB later.
#
# For now, scan history works while the AI server is running.
# =========================================================

scan_history = []


# =========================================================
# REQUEST MODELS
# =========================================================

class DetectionRequest(BaseModel):
    text: str
    url: str = ""


class URLScanRequest(BaseModel):
    url: str


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "AdvSystem AI service is running!"
    }


# =========================================================
# BASIC CONTENT DETECTION
# =========================================================

@app.post("/detect")
def detect(request: DetectionRequest):

    result = detect_content(
        request.text
    )

    ads_count = len(
        result["ads"]
    )

    trackers_count = len(
        result["trackers"]
    )

    risk_score = calculate_risk_score(
        ads_count,
        trackers_count
    )

    risk_level = get_risk_level(
        risk_score
    )

    domain = (
        extract_domain(request.url)
        if request.url
        else ""
    )

    return {
        "url": request.url,
        "domain": domain,
        "ads": result["ads"],
        "trackers": result["trackers"],
        "ads_count": ads_count,
        "trackers_count": trackers_count,
        "risk_score": risk_score,
        "risk_level": risk_level
    }


# =========================================================
# WEBSITE SCANNER
# =========================================================

@app.post("/scan-url")
def scan_url(request: URLScanRequest):

    try:

        # -------------------------------------------------
        # Run webpage scanner
        # -------------------------------------------------

        scan_result = scan_webpage(
            request.url
        )

        # -------------------------------------------------
        # Run security rule analysis
        # -------------------------------------------------

        security_analysis = analyze_security_rules(
            scan_result
        )

        # -------------------------------------------------
        # Add security analysis
        # -------------------------------------------------

        scan_result["security_analysis"] = (
            security_analysis
        )

        # -------------------------------------------------
        # Extract detection information
        # -------------------------------------------------

        detection = scan_result.get(
            "detection",
            {}
        )

        final_risk = scan_result.get(
            "final_risk",
            {}
        )

        # -------------------------------------------------
        # Calculate history values
        # -------------------------------------------------

        ads_count = len(
            detection.get(
                "ads",
                []
            )
        )

        trackers_count = len(
            detection.get(
                "trackers",
                []
            )
        )

        total_resources = detection.get(
            "total_resources",
            0
        )

        risk_score = float(
            final_risk.get(
                "final_risk_score",
                scan_result.get(
                    "risk_score",
                    0
                )
            )
        )

        risk_level = final_risk.get(
            "final_risk_level",
            scan_result.get(
                "risk_level",
                "LOW"
            )
        )

        # -------------------------------------------------
        # Save scan to temporary history
        # -------------------------------------------------

        history_document = {
            "id": len(scan_history) + 1,

            "url": scan_result.get(
                "url",
                request.url
            ),

            "scan_date": datetime.now(
                timezone.utc
            ).strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            ),

            "ads_count": ads_count,

            "trackers_count": trackers_count,

            "total_resources": total_resources,

            "risk_score": risk_score,

            "risk_level": risk_level
        }

        scan_history.insert(
            0,
            history_document
        )

        # -------------------------------------------------
        # Return complete scan result
        # -------------------------------------------------

        return scan_result

    except Exception as error:

        print(
            f"Website scan error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail=f"Unable to scan website: {str(error)}"
        )


# =========================================================
# SCAN HISTORY
# =========================================================

@app.get("/scan-history")
def get_scan_history():

    return {
        "history": scan_history
    }


# =========================================================
# CLEAR SCAN HISTORY
# =========================================================

@app.delete("/scan-history")
def clear_scan_history():

    deleted_count = len(
        scan_history
    )

    scan_history.clear()

    return {
        "message": "Scan history cleared successfully.",
        "deleted_count": deleted_count
    }


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

@app.get("/dashboard-summary")
def dashboard_summary():

    total_scans = len(
        scan_history
    )

    total_ads = sum(
        scan.get(
            "ads_count",
            0
        )
        for scan in scan_history
    )

    total_trackers = sum(
        scan.get(
            "trackers_count",
            0
        )
        for scan in scan_history
    )

    total_resources = sum(
        scan.get(
            "total_resources",
            0
        )
        for scan in scan_history
    )

    total_risk = sum(
        float(
            scan.get(
                "risk_score",
                0
            )
        )
        for scan in scan_history
    )

    average_risk_score = (
        round(
            total_risk / total_scans,
            2
        )
        if total_scans > 0
        else 0
    )

    high_risk_scans = sum(
        1
        for scan in scan_history
        if str(
            scan.get(
                "risk_level",
                ""
            )
        ).upper() == "HIGH"
    )

    medium_risk_scans = sum(
        1
        for scan in scan_history
        if str(
            scan.get(
                "risk_level",
                ""
            )
        ).upper() == "MEDIUM"
    )

    low_risk_scans = sum(
        1
        for scan in scan_history
        if str(
            scan.get(
                "risk_level",
                ""
            )
        ).upper() == "LOW"
    )

    return {
        "total_scans": total_scans,
        "total_ads": total_ads,
        "total_trackers": total_trackers,
        "total_resources": total_resources,
        "average_risk_score": average_risk_score,
        "high_risk_scans": high_risk_scans,
        "medium_risk_scans": medium_risk_scans,
        "low_risk_scans": low_risk_scans
    }