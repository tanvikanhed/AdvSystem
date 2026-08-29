import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [summary, setSummary] = useState(null);

  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [error, setError] = useState("");

  const loadHistory = async () => {
    try {
      setHistoryLoading(true);

      const response = await fetch(`${API_URL}/scan-history`);

      if (!response.ok) {
        throw new Error("Unable to load scan history.");
      }

      const data = await response.json();
      setHistory(data.history || []);
    } catch (err) {
      console.error("History error:", err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const loadSummary = async () => {
    try {
      const response = await fetch(`${API_URL}/dashboard-summary`);

      if (!response.ok) {
        throw new Error("Unable to load dashboard summary.");
      }

      const data = await response.json();
      setSummary(data);
    } catch (err) {
      console.error("Dashboard summary error:", err);
    }
  };

  useEffect(() => {
    loadHistory();
    loadSummary();
  }, []);

  const scanWebsite = async () => {
    if (!url.trim()) {
      setError("Please enter a website URL.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/scan-url`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: url.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to scan the website."
        );
      }

      setResult(data);

      await loadHistory();
      await loadSummary();
    } catch (err) {
      console.error("Scan error:", err);
      setError(err.message || "Unable to scan the website.");
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to delete all scan history?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");

      const response = await fetch(`${API_URL}/scan-history`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to clear scan history."
        );
      }

      setHistory([]);
      setSummary(null);
      setResult(null);

      await loadSummary();
    } catch (err) {
      console.error("Clear history error:", err);
      setError(err.message || "Unable to clear scan history.");
    }
  };

  const openHistoryScan = (item) => {
    setUrl(item.url);

    if (item.result) {
      setResult(item.result);
    }

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const getRiskPercentage = () => {
    if (!result) {
      return 0;
    }

    return Math.min(Number(result.risk_score) || 0, 100);
  };

  const getFinalRiskPercentage = () => {
    if (!result?.final_risk) {
      return 0;
    }

    return Math.min(
      Number(result.final_risk.final_risk_score) || 0,
      100
    );
  };

  const getRiskClass = (level) => {
    if (!level) {
      return "low";
    }

    return String(level).toLowerCase();
  };

  const formatConfidence = (confidence) => {
    if (confidence === undefined || confidence === null) {
      return "N/A";
    }

    if (typeof confidence === "number") {
      return `${(confidence * 100).toFixed(1)}%`;
    }

    return confidence;
  };

  const ads = result?.detection?.ads || [];
  const trackers = result?.detection?.trackers || [];
  const normalResources =
    result?.detection?.normal_resources || [];

  const totalResources =
    result?.detection?.total_resources ??
    ads.length + trackers.length + normalResources.length;

  return (
    <div className="app">
      {/* HEADER */}

      <header className="header">
        <div>
          <h1>AdvSystem</h1>

          <p>
            Web Advertisement & Tracker Security Scanner
          </p>
        </div>

        <span className="status">
          ● AI Scanner Online
        </span>
      </header>

      <main className="container">
        {/* DASHBOARD */}

        <section className="dashboard">
          <div className="dashboard-header">
            <div>
              <h2>Security Overview</h2>

              <p>
                Overall statistics from your website scans
              </p>
            </div>
          </div>

          {summary ? (
            <div className="dashboard-stats">
              <div className="dashboard-card">
                <span>Total Scans</span>
                <strong>
                  {summary.total_scans ?? 0}
                </strong>
              </div>

              <div className="dashboard-card">
                <span>Advertisements</span>
                <strong>
                  {summary.total_ads ?? 0}
                </strong>
              </div>

              <div className="dashboard-card">
                <span>Trackers</span>
                <strong>
                  {summary.total_trackers ?? 0}
                </strong>
              </div>

              <div className="dashboard-card">
                <span>Resources</span>
                <strong>
                  {summary.total_resources ?? 0}
                </strong>
              </div>

              <div className="dashboard-card">
                <span>Average Risk</span>
                <strong>
                  {summary.average_risk_score ?? 0}
                </strong>
              </div>

              <div className="dashboard-card">
                <span>High-Risk Scans</span>
                <strong>
                  {summary.high_risk_scans ?? 0}
                </strong>
              </div>
            </div>
          ) : (
            <div className="dashboard-stats">
              <div className="dashboard-card">
                <span>Total Scans</span>
                <strong>0</strong>
              </div>

              <div className="dashboard-card">
                <span>Advertisements</span>
                <strong>0</strong>
              </div>

              <div className="dashboard-card">
                <span>Trackers</span>
                <strong>0</strong>
              </div>
            </div>
          )}
        </section>

        {/* SCANNER */}

        <section className="hero">
          <h2>Scan a Website</h2>

          <p>
            Analyze a webpage for advertisements, trackers,
            external resources, and security risk.
          </p>

          <div className="scan-box">
            <input
              type="text"
              placeholder="https://example.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !loading) {
                  scanWebsite();
                }
              }}
            />

            <button
              onClick={scanWebsite}
              disabled={loading}
            >
              {loading ? "Scanning..." : "Scan Website"}
            </button>
          </div>

          {error && (
            <div className="error">
              {error}
            </div>
          )}
        </section>

        {/* LOADING */}

        {loading && (
          <section className="loading">
            <div className="spinner"></div>

            <p>
              Analyzing webpage...
            </p>
          </section>
        )}

        {/* RESULTS */}

        {result && !loading && (
          <section className="results">
            <div className="result-header">
              <div>
                <h2>Scan Results</h2>

                <p className="scanned-url">
                  {result.url}
                </p>
              </div>

              <div
                className={`risk-badge ${getRiskClass(
                  result.risk_level
                )}`}
              >
                {result.risk_level || "UNKNOWN"}
              </div>
            </div>

            {/* AI RISK */}

            {result.final_risk && (
              <div className="ai-risk-card">
                <div className="ai-risk-header">
                  <div>
                    <h3>
                      AI Security Assessment
                    </h3>

                    <p>
                      Final risk decision using rule-based
                      analysis and machine learning.
                    </p>
                  </div>

                  <div
                    className={`ai-risk-badge ${getRiskClass(
                      result.final_risk.final_risk_level
                    )}`}
                  >
                    {
                      result.final_risk.final_risk_level
                    }
                  </div>
                </div>

                <div className="ai-risk-score">
                  <div>
                    <span>
                      Final Risk Score
                    </span>

                    <strong>
                      {
                        result.final_risk
                          .final_risk_score
                      }{" "}
                      / 100
                    </strong>
                  </div>

                  <div>
                    <span>
                      Confidence
                    </span>

                    <strong>
                      {formatConfidence(
                        result.final_risk.confidence
                      )}
                    </strong>
                  </div>
                </div>

                <div className="ai-risk-meter">
                  <div
                    className={`ai-risk-meter-fill ${getRiskClass(
                      result.final_risk.final_risk_level
                    )}`}
                    style={{
                      width: `${getFinalRiskPercentage()}%`,
                    }}
                  ></div>
                </div>

                <div className="ai-analysis-grid">
                  <div className="ai-analysis-item">
                    <span>
                      Rule-Based Risk
                    </span>

                    <strong>
                      {result.risk_score}
                    </strong>
                  </div>

                  <div className="ai-analysis-item">
                    <span>
                      ML Prediction
                    </span>

                    <strong>
                      {
                        result.ml_prediction
                          ?.ml_risk_label
                      }
                    </strong>
                  </div>

                  <div className="ai-analysis-item">
                    <span>
                      ML Probability
                    </span>

                    <strong>
                      {
                        result.ml_prediction
                          ?.ml_risk_probability
                      }
                    </strong>
                  </div>

                  <div className="ai-analysis-item">
                    <span>
                      AI Decision
                    </span>

                    <strong>
                      {
                        result.final_risk
                          .final_risk_level
                      }
                    </strong>
                  </div>
                </div>
              </div>
            )}

            {/* RULE RISK */}

            <div className="score-card">
              <div className="score-main">
                <p>
                  Rule-Based Risk Score
                </p>

                <h3>
                  {result.risk_score} / 100
                </h3>
              </div>

              <div className="score-description">
                <div className="risk-meter">
                  <div
                    className={`risk-meter-fill ${getRiskClass(
                      result.risk_level
                    )}`}
                    style={{
                      width: `${getRiskPercentage()}%`,
                    }}
                  ></div>
                </div>

                <p>
                  {result.risk_level === "LOW" &&
                    "The webpage has a low detected privacy/security risk."}

                  {result.risk_level === "MEDIUM" &&
                    "The webpage contains some potentially risky resources."}

                  {result.risk_level === "HIGH" &&
                    "The webpage contains a high number of detected risky resources."}
                </p>
              </div>
            </div>

            {/* BREAKDOWN */}

            <div className="risk-breakdown">
              <h3>
                Risk Breakdown
              </h3>

              <div className="breakdown-row">
                <span>
                  Advertisements
                </span>

                <strong>
                  {ads.length}
                  {" × 10 = "}
                  {ads.length * 10}
                </strong>
              </div>

              <div className="breakdown-row">
                <span>
                  Trackers
                </span>

                <strong>
                  {trackers.length}
                  {" × 20 = "}
                  {trackers.length * 20}
                </strong>
              </div>

              <div className="breakdown-total">
                <span>
                  Total Risk Score
                </span>

                <strong>
                  {result.risk_score}
                </strong>
              </div>
            </div>

            {/* STATISTICS */}

            <div className="stats">
              <div className="stat-card">
                <span>
                  Advertisements
                </span>

                <strong>
                  {ads.length}
                </strong>
              </div>

              <div className="stat-card">
                <span>
                  Trackers
                </span>

                <strong>
                  {trackers.length}
                </strong>
              </div>

              <div className="stat-card">
                <span>
                  Normal Resources
                </span>

                <strong>
                  {normalResources.length}
                </strong>
              </div>

              <div className="stat-card">
                <span>
                  Total Resources
                </span>

                <strong>
                  {totalResources}
                </strong>
              </div>
            </div>

            {/* DETAILS */}

            <div className="details">
              <div className="detail-card">
                <h3>
                  Detected Advertisements
                </h3>

                {ads.length === 0 ? (
                  <p className="empty">
                    No advertisements detected.
                  </p>
                ) : (
                  ads.map((ad, index) => (
                    <div
                      className="resource"
                      key={`ad-${index}`}
                    >
                      <strong>
                        {ad.domain || "Unknown domain"}
                      </strong>

                      <span>
                        {ad.url || "URL unavailable"}
                      </span>

                      <small>
                        Evidence:{" "}
                        {Array.isArray(ad.matches)
                          ? ad.matches.join(", ")
                          : ad.matches || "None"}
                      </small>
                    </div>
                  ))
                )}
              </div>

              <div className="detail-card">
                <h3>
                  Detected Trackers
                </h3>

                {trackers.length === 0 ? (
                  <p className="empty">
                    No trackers detected.
                  </p>
                ) : (
                  trackers.map((tracker, index) => (
                    <div
                      className="resource"
                      key={`tracker-${index}`}
                    >
                      <strong>
                        {tracker.domain ||
                          "Unknown domain"}
                      </strong>

                      <span>
                        {tracker.url ||
                          "URL unavailable"}
                      </span>

                      <small>
                        Evidence:{" "}
                        {Array.isArray(
                          tracker.matches
                        )
                          ? tracker.matches.join(", ")
                          : tracker.matches ||
                            "None"}
                      </small>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* THIRD-PARTY RESOURCE ANALYSIS */}

{result.third_party_analysis && (
  <div className="third-party-card">

    <div className="third-party-header">
      <div>
        <h3>Third-Party Resource Analysis</h3>

        <p>
          Analysis of external resources loaded or referenced
          by the scanned webpage.
        </p>
      </div>

      <div className="third-party-domain-count">
        <strong>
          {result.third_party_analysis.third_party_domain_count}
        </strong>

        <span>
          Third-Party Domains
        </span>
      </div>
    </div>

    <div className="third-party-grid">

      <div className="third-party-item">
        <span>External Scripts</span>

        <strong>
          {result.third_party_analysis.external_script_count}
        </strong>
      </div>

      <div className="third-party-item">
        <span>External Iframes</span>

        <strong>
          {result.third_party_analysis.external_iframe_count}
        </strong>
      </div>

      <div className="third-party-item">
        <span>External Images</span>

        <strong>
          {result.third_party_analysis.external_image_count}
        </strong>
      </div>

      <div className="third-party-item">
        <span>External Links</span>

        <strong>
          {result.third_party_analysis.external_link_count}
        </strong>
      </div>

    </div>

    <div className="third-party-domains">

      {/* SECURITY RULE ANALYSIS */}

{result.security_analysis && (
  <div className="security-analysis-card">

    <div className="security-analysis-header">
      <div>
        <h3>Security Rule Analysis</h3>

        <p>
          Rule-based checks performed on the scanned webpage.
        </p>
      </div>
    </div>

    {Array.isArray(result.security_analysis) ? (
      result.security_analysis.length === 0 ? (
        <p className="empty">
          No security issues detected.
        </p>
      ) : (
        <div className="security-rule-list">
          {result.security_analysis.map((rule, index) => (
            <div
              className="security-rule-item"
              key={index}
            >
              <div>
                <strong>
                  {rule.rule ||
                    rule.name ||
                    "Security Rule"}
                </strong>

                <span>
                  {rule.description ||
                    rule.message ||
                    rule.reason ||
                    "Security check performed."}
                </span>
              </div>

              <b
                className={`security-severity ${
                  String(
                    rule.severity || "INFO"
                  ).toLowerCase()
                }`}
              >
                {rule.severity || "INFO"}
              </b>
            </div>
          ))}
        </div>
      )
    ) : (
      <div className="security-rule-item">
        <div>
          <strong>Security Analysis</strong>

          <span>
            {JSON.stringify(
              result.security_analysis
            )}
          </span>
        </div>
      </div>
    )}

  </div>
)}

      <h4>Third-Party Domains</h4>

      {result.third_party_analysis.third_party_domains.length === 0 ? (
        <p className="empty">
          No third-party domains detected.
        </p>
      ) : (
        result.third_party_analysis.third_party_domains.map(
          (domain, index) => (
            <div
              className="third-party-domain"
              key={index}
            >
              {domain}
            </div>
          )
        )
      )}

    </div>

  </div>
)}

            {/* NORMAL RESOURCES */}

            <div className="detail-card">
              <h3>
                Normal Resources
              </h3>

              {normalResources.length === 0 ? (
                <p className="empty">
                  No normal resources detected.
                </p>
              ) : (
                normalResources.map(
                  (resource, index) => (
                    <div
                      className="resource"
                      key={`resource-${index}`}
                    >
                      {typeof resource === "string" ? (
                        <span>
                          {resource}
                        </span>
                      ) : (
                        <>
                          <strong>
                            {resource.domain ||
                              "Resource"}
                          </strong>

                          <span>
                            {resource.url ||
                              resource.src ||
                              "URL unavailable"}
                          </span>
                        </>
                      )}
                    </div>
                  )
                )
              )}
            </div>
          </section>
        )}

        {/* HISTORY */}

        <section className="history">
          <div className="history-header">
            <div>
              <h2>
                Scan History
              </h2>

              <p>
                Previously scanned websites
              </p>
            </div>

            {history.length > 0 && (
              <button
                className="clear-button"
                onClick={clearHistory}
              >
                Clear History
              </button>
            )}
          </div>

          {historyLoading ? (
            <div className="history-empty">
              <p>
                Loading scan history...
              </p>
            </div>
          ) : history.length === 0 ? (
            <div className="history-empty">
              <p>
                No scan history yet.
              </p>

              <span>
                Scan a website to see it here.
              </span>
            </div>
          ) : (
            <div className="history-list">
              {history.map((item, index) => {
                const historyRisk =
                  item.risk_level ||
                  item.final_risk_level ||
                  "LOW";

                const historyScore =
                  item.risk_score ??
                  item.final_risk_score ??
                  0;

                const historyAds =
                  item.ads ??
                  item.ad_count ??
                  0;

                const historyTrackers =
                  item.trackers ??
                  item.tracker_count ??
                  0;

                const historyResources =
                  item.total_resources ??
                  item.resource_count ??
                  0;

                return (
                  <div
                    className="history-item"
                    key={
                      item.id ||
                      item._id ||
                      `history-${index}`
                    }
                  >
                    <div className="history-info">
                      <strong>
                        {item.url}
                      </strong>

                      <span>
                        Scan #{history.length - index}
                      </span>
                    </div>

                    <div className="history-stats">
                      <span>
                        Ads: {historyAds}
                      </span>

                      <span>
                        Trackers: {historyTrackers}
                      </span>

                      <span>
                        Resources: {historyResources}
                      </span>
                    </div>

                    <div className="history-risk">
                      <strong>
                        {historyScore}
                      </strong>

                      <span
                        className={`history-level ${getRiskClass(
                          historyRisk
                        )}`}
                      >
                        {historyRisk}
                      </span>
                    </div>

                    <button
                      className="view-button"
                      onClick={() =>
                        openHistoryScan(item)
                      }
                    >
                      View
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </main>

      <footer>
        AdvSystem — AI-Powered Advertisement &
        Tracker Security Scanner
      </footer>
    </div>
  );
}

export default App;