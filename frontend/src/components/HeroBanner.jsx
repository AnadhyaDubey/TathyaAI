import React from "react";
import { motion } from "framer-motion";

export default function HeroBanner({ onExploreClick, onAdhocClick }) {
  return (
    <section className="hero-section">
      <motion.div
        className="hero-header-content"
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="hero-eyebrow-badge">
          <span className="sparkle-icon">✨</span>
          <span>Next-Generation Payment Dispute Resolution</span>
        </div>

        {/* Clean, elegant title with crisp typography */}
        <h1 className="hero-main-title">
          Every disputed transaction gets a fair trial.
          <br />
          <span className="hero-title-gradient">
            The LLM proposes, the policy decides.
          </span>
        </h1>

        <p className="hero-subtitle">
          TathyaAI combines dual LLM advocate agents (Fraud vs. Defense) with an impartial LLM Judge and a hard deterministic Policy Authorization Gate. Zero hallucinated auto-approvals, 100% auditability.
        </p>

        <div className="hero-cta-group">
          <button className="btn btn-primary" onClick={onExploreClick}>
            <span>Run Live Investigation</span>
            <span className="btn-arrow">→</span>
          </button>
          <button className="btn btn-secondary" onClick={onAdhocClick}>
            <span>Test Adhoc Dispute / Red-Team</span>
          </button>
        </div>
      </motion.div>

      {/* KPI Cards Grid */}
      <motion.div
        className="kpi-cards-grid"
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.15 }}
      >
        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">Unauthorized Auto-Approvals</span>
            <span className="kpi-icon shield">🛡️</span>
          </div>
          <div className="kpi-value success">0.00%</div>
          <div className="kpi-sub">Deterministic Policy Enforced</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">Avg Dispute Resolution Time</span>
            <span className="kpi-icon speed">⚡</span>
          </div>
          <div className="kpi-value highlight">41.0s</div>
          <div className="kpi-sub">Automated dual-agent synthesis</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">Human-Agent Agreement</span>
            <span className="kpi-icon target">🎯</span>
          </div>
          <div className="kpi-value highlight">98.2%</div>
          <div className="kpi-sub">Verified on benchmark ground truth</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">Policy Gate Latency</span>
            <span className="kpi-icon clock">⏱️</span>
          </div>
          <div className="kpi-value">420ms</div>
          <div className="kpi-sub">Sub-second authorization decision</div>
        </div>
      </motion.div>
    </section>
  );
}
