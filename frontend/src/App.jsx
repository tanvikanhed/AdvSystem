import { useEffect, useState } from "react";
import "./app.css";

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

      const response = await fetch(
        `${API_URL}/scan-history`
      );

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
      const response = await fetch(
        `${API_URL}/dashboard-summary`
      );

      if (!response.ok) {
        throw new Error(
          "Unable to load dashboard summary."
        );
      }

      const data = await response.json();

      setSummary(data);
    } catch (err) {
      console.error(
        "Dashboard summary error:",
        err
      );
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
      const response = await fetch(
        `${API_URL}/scan-url`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            url: url.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
          "Unable to scan the website."
        );
      }

      setResult(data);

      await loadHistory();
      await loadSummary();

    } catch (err) {
      setError(err.message);
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
      const response = await fetch(
        `${API_URL}/scan-history`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
          "Unable to clear scan history."
        );
      }

      setHistory([]);
      setSummary(null);

      await loadSummary();

    } catch (err) {
      setError(err.message);
    }
  };

  const openHistoryScan = (item) => {
    setUrl(item.url);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  // ---------------------------------------------
  // Calculate visual risk percentage
  // ---------------------------------------------

  const getRiskPercentage = () => {
    if (!result) {
      return 0;
    }

    return Math.min(
      result.risk_score,
      100
    );
  };

  return (
    <div className="app">

      {/* HEADER */}

      <header className="header">

        <div>

          <h1>
            AdvSystem
          </h1>

          <p>
            Web Advertisement & Tracker
            Security Scanner
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

              <h2>
                Security Overview
              </h2>

              <p>
                Overall statistics from your
                website scans
              </p>

            </div>

          </div>


          {summary && (

            <div className="dashboard-stats">

              <div className="dashboard-card">

                <span>
                  Total Scans
                </span>

                <strong>
                  {summary.total_scans}
                </strong>

              </div>


              <div className="dashboard-card">

                <span>
                  Advertisements
                </span>

                <strong>
                  {summary.total_ads}
                </strong>

              </div>


              <div className="dashboard-card">

                <span>
                  Trackers
                </span>

                <strong>
                  {summary.total_trackers}
                </strong>

              </div>


              <div className="dashboard-card">

                <span>
                  Resources
                </span>

                <strong>
                  {summary.total_resources}
                </strong>

              </div>


              <div className="dashboard-card">

                <span>
                  Average Risk
                </span>

                <strong>
                  {summary.average_risk_score}
                </strong>

              </div>


              <div className="dashboard-card">

                <span>
                  High-Risk Scans
                </span>

                <strong>
                  {summary.high_risk_scans}
                </strong>

              </div>

            </div>

          )}

        </section>


        {/* SCANNER */}

        <section className="hero">

          <h2>
            Scan a Website
          </h2>

          <p>
            Analyze a webpage for advertisements,
            trackers, external resources, and
            security risk.
          </p>


          <div className="scan-box">

            <input
              type="text"
              placeholder="https://example.com"
              value={url}
              onChange={(e) =>
                setUrl(e.target.value)
              }
              onKeyDown={(e) => {

                if (e.key === "Enter") {
                  scanWebsite();
                }

              }}
            />


            <button
              onClick={scanWebsite}
              disabled={loading}
            >

              {loading
                ? "Scanning..."
                : "Scan Website"}

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

                <h2>
                  Scan Results
                </h2>

                <p className="scanned-url">
                  {result.url}
                </p>

              </div>


              <div
                className={`risk-badge ${result.risk_level.toLowerCase()}`}
              >
                {result.risk_level}
              </div>

            </div>


            {/* RISK SCORE */}

            <div className="score-card">

              <div className="score-main">

                <p>
                  Risk Score
                </p>

                <h3>
                  {result.risk_score} / 100
                </h3>

              </div>


              <div className="score-description">

                <div className="risk-meter">

                  <div
                    className={`risk-meter-fill ${result.risk_level.toLowerCase()}`}
                    style={{
                      width: `${getRiskPercentage()}%`,
                    }}
                  ></div>

                </div>


                <p>

                  {result.risk_level === "LOW" &&
                    "The webpage has a low detected privacy/security risk."
                  }

                  {result.risk_level === "MEDIUM" &&
                    "The webpage contains some potentially risky resources."
                  }

                  {result.risk_level === "HIGH" &&
                    "The webpage contains a high number of detected risky resources."
                  }

                </p>

              </div>

            </div>


            {/* RISK BREAKDOWN */}

            <div className="risk-breakdown">

              <h3>
                Risk Breakdown
              </h3>


              <div className="breakdown-row">

                <span>
                  Advertisements
                </span>

                <strong>
                  {result.detection.ads.length}
                  {" × 10 = "}
                  {result.detection.ads.length * 10}
                </strong>

              </div>


              <div className="breakdown-row">

                <span>
                  Trackers
                </span>

                <strong>
                  {result.detection.trackers.length}
                  {" × 20 = "}
                  {result.detection.trackers.length * 20}
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
                  {result.detection.ads.length}
                </strong>

              </div>


              <div className="stat-card">

                <span>
                  Trackers
                </span>

                <strong>
                  {result.detection.trackers.length}
                </strong>

              </div>


              <div className="stat-card">

                <span>
                  Normal Resources
                </span>

                <strong>
                  {result.detection.normal_resources.length}
                </strong>

              </div>


              <div className="stat-card">

                <span>
                  Total Resources
                </span>

                <strong>
                  {result.detection.total_resources}
                </strong>

              </div>

            </div>


            {/* DETAILS */}

            <div className="details">

              {/* ADS */}

              <div className="detail-card">

                <h3>
                  Detected Advertisements
                </h3>


                {result.detection.ads.length === 0 ? (

                  <p className="empty">
                    No advertisements detected.
                  </p>

                ) : (

                  result.detection.ads.map(
                    (ad, index) => (

                      <div
                        className="resource"
                        key={index}
                      >

                        <strong>
                          {ad.domain}
                        </strong>

                        <span>
                          {ad.url}
                        </span>

                        <small>
                          Evidence:{" "}
                          {ad.matches.join(", ")}
                        </small>

                      </div>

                    )
                  )

                )}

              </div>


              {/* TRACKERS */}

              <div className="detail-card">

                <h3>
                  Detected Trackers
                </h3>


                {result.detection.trackers.length === 0 ? (

                  <p className="empty">
                    No trackers detected.
                  </p>

                ) : (

                  result.detection.trackers.map(
                    (tracker, index) => (

                      <div
                        className="resource"
                        key={index}
                      >

                        <strong>
                          {tracker.domain}
                        </strong>

                        <span>
                          {tracker.url}
                        </span>

                        <small>
                          Evidence:{" "}
                          {tracker.matches.join(", ")}
                        </small>

                      </div>

                    )
                  )

                )}

              </div>

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
                Previous website security scans
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
                Loading history...
              </p>

            </div>

          ) : history.length === 0 ? (

            <div className="history-empty">

              <p>
                No scans yet.
              </p>

              <span>
                Your previous scans will appear here.
              </span>

            </div>

          ) : (

            <div className="history-list">

              {history.map((item) => (

                <div
                  className="history-item"
                  key={item.id}
                >

                  <div className="history-info">

                    <strong>
                      {item.url}
                    </strong>

                    <span>
                      {item.scan_date}
                    </span>

                  </div>


                  <div className="history-stats">

                    <span>
                      Ads: {item.ads_count}
                    </span>

                    <span>
                      Trackers: {item.trackers_count}
                    </span>

                    <span>
                      Resources: {item.total_resources}
                    </span>

                  </div>


                  <div className="history-risk">

                    <strong>
                      {item.risk_score}
                    </strong>

                    <span
                      className={`history-level ${item.risk_level.toLowerCase()}`}
                    >
                      {item.risk_level}
                    </span>

                  </div>


                  <button
                    className="view-button"
                    onClick={() =>
                      openHistoryScan(item)
                    }
                  >
                    Use URL
                  </button>

                </div>

              ))}

            </div>

          )}

        </section>

      </main>


      <footer>
        AdvSystem AI Security Scanner
      </footer>

    </div>
  );
}

export default App;