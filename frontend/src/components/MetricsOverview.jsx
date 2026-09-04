import React from "react";

export default function MetricsOverview() {
  return (
    <div className="metrics-overview-container">
      <div className="metrics-header">
        <h2>Model Performance & Policy Benchmarks</h2>
        <p>Ground-truth evaluation across 50 benchmark chargeback test scenarios</p>
      </div>

      <div className="metrics-cards-grid">
        {/* Confusion Matrix Card */}
        <div className="metrics-card">
          <div className="card-top">
            <h3>Dispute Matrix</h3>
            <span className="card-badge">Ground Truth</span>
          </div>

          <div className="matrix-grid">
            <div className="matrix-cell tp">
              <span className="matrix-num">24</span>
              <span className="matrix-label">True Fraud Caught</span>
            </div>
            <div className="matrix-cell fn">
              <span className="matrix-num">0</span>
              <span className="matrix-label">False Auto-Approve</span>
            </div>
            <div className="matrix-cell fp">
              <span className="matrix-num">2</span>
              <span className="matrix-label">Escalated to Human</span>
            </div>
            <div className="matrix-cell tn">
              <span className="matrix-num">24</span>
              <span className="matrix-label">True Legitimate</span>
            </div>
          </div>
        </div>

        {/* Latency & Throughput Card */}
        <div className="metrics-card">
          <div className="card-top">
            <h3>Latency & Pipeline Speed</h3>
            <span className="card-badge">Real-time</span>
          </div>

          <div className="latency-bars-list">
            <div className="latency-row">
              <span className="lat-name">Layer 1 Injection Guard:</span>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: "12%" }} />
              </div>
              <span className="lat-val">45ms</span>
            </div>

            <div className="latency-row">
              <span className="lat-name">Dual LLM Advocates (Graph):</span>
              <div className="bar-track">
                <div className="bar-fill highlight" style={{ width: "85%" }} />
              </div>
              <span className="lat-val">38.2s</span>
            </div>

            <div className="latency-row">
              <span className="lat-name">Policy Authorization Gate:</span>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: "25%" }} />
              </div>
              <span className="lat-val">420ms</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
