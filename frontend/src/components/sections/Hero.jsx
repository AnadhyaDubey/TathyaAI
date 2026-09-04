import { motion } from "framer-motion";

export default function Hero() {
  return (
    <div className="section" style={{ position: "relative", paddingTop: 120 }}>
      
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: "easeOut" }}
      >
        <div className="eyebrow">TathyaAI</div>
        <h1>Every disputed transaction<br />gets a fair trial</h1>
        <p className="lead">
          Two AI agents argue opposite sides of every chargeback. A judge weighs
          both. A policy engine — not the model — has the final word.
        </p>
        <div className="btn-row">
          <button className="btn btn-primary">See a live investigation →</button>
          <button className="btn btn-secondary">View on GitHub</button>
        </div>
      </motion.div>

      <motion.div
        className="stat-grid"
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 0.6, delay: 0.1 }}
      >
        <div className="stat-card">
          <p className="stat-label">Escalation rate</p>
          <p className="stat-value">82%</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">Fraud auto-approved</p>
          <p className="stat-value success">0%</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">Judge accuracy</p>
          <p className="stat-value">68%</p>
        </div>
      </motion.div>
    </div>
  );
}