from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from detection.detector import detect_content, extract_domain
from detection.risk_score import (
    calculate_risk_score,
    get_risk_level
)
from detection.rule_engine import analyze_security_rules
from webpage_scanner import scan_webpage


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

    # ---------------------------------------------
    # Run webpage scanner
    # ---------------------------------------------

    scan_result = scan_webpage(
        request.url
    )

    # ---------------------------------------------
    # Run rule-based security analysis
    # ---------------------------------------------

    security_analysis = analyze_security_rules(
        scan_result
    )

    # ---------------------------------------------
    # Add rule analysis to final response
    # ---------------------------------------------

    scan_result["security_analysis"] = (
        security_analysis
    )

    return scan_result