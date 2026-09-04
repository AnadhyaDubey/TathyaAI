import React from "react";

export default function Navbar({
  activeTab,
  setActiveTab,
  backendStatus,
  notesPaused,
  setNotesPaused,
}) {
  return (
    <header className="navbar-container">
      <div className="navbar-inner">
        {/* Left: Brand Identity */}
        <div className="brand-logo-group">
          <div className="logo-symbol">
            <span className="logo-rupee">₹</span>
            <span className="logo-pulse" />
          </div>
          <div className="brand-titles">
            <span className="brand-name">TathyaAI</span>
            <span className="brand-tagline">Autonomous AI Dispute Resolution Engine</span>
          </div>
        </div>

        {/* Center: Clean Navigation Tabs */}
        <nav className="nav-tabs">
          <button
            className={`nav-tab-btn ${activeTab === "overview" ? "active" : ""}`}
            onClick={() => setActiveTab("overview")}
          >
            Overview & Metrics
          </button>
          <button
            className={`nav-tab-btn ${activeTab === "investigate" ? "active" : ""}`}
            onClick={() => setActiveTab("investigate")}
          >
            LLM Investigation Arena
          </button>
          <button
            className={`nav-tab-btn ${activeTab === "adhoc" ? "active" : ""}`}
            onClick={() => setActiveTab("adhoc")}
          >
            Red-Team Adhoc Simulator
          </button>
          <button
            className={`nav-tab-btn ${activeTab === "audit" ? "active" : ""}`}
            onClick={() => setActiveTab("audit")}
          >
            Audit Trail & Transactions
          </button>
        </nav>

        {/* Right: Actions, Contact Info & Status Indicator */}
        <div className="navbar-right-group">
          {/* Notes canvas animation toggle */}
          <button
            className="notes-toggle-btn"
            onClick={() => setNotesPaused(!notesPaused)}
            title="Toggle Indian Rupee notes background animation"
          >
            {notesPaused ? "▶ Currency Notes Floating" : "⏸ Pause Notes Floating"}
          </button>

          {/* Backend API Connection status badge */}
          <div className="status-badge-container">
            <span
              className={`status-dot ${
                backendStatus.status === "ok" ? "online" : "simulation"
              }`}
            />
            <span className="status-text">
              {backendStatus.status === "ok" ? "FastAPI Live" : "Simulation Mode"}
            </span>
          </div>

          {/* Contact email display per user request */}
          <a
            href="mailto:anadhyadubey16@gmail.com"
            className="contact-pill-link"
            title="Contact Lead Developer: anadhyadubey16@gmail.com"
          >
            ✉️ anadhyadubey16@gmail.com
          </a>
        </div>
      </div>
    </header>
  );
}
