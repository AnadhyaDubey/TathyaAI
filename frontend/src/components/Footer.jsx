import React from "react";

export default function Footer() {
  return (
    <footer className="app-footer">
      <div className="footer-content">
        <div className="footer-left">
          <div className="footer-brand">
            <span className="footer-logo">₹</span> TathyaAI Engine
          </div>
          <p className="footer-sub">
            Dual-agent dialectic LLM investigation with deterministic policy authorization gate for high-trust payment disputes.
          </p>
        </div>

        <div className="footer-right">
          <div className="footer-contact-box">
            <span className="contact-label">Lead Developer & Contact:</span>
            <a href="mailto:anadhyadubey16@gmail.com" className="contact-email">
              anadhyadubey16@gmail.com
            </a>
          </div>
          <div className="footer-meta">
            <span>Deterministic Policy Limit: ₹15,000</span>
            <span>•</span>
            <span>Currency: INR (₹)</span>
            <span>•</span>
            <span>System Status: Operational</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
