import React, { useState } from "react";

export default function AuditTrailTable({
  cases = [],
  onSelectCase,
  onApproveCase,
}) {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const filteredCases = cases.filter((c) => {
    const matchSearch =
      c.case_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.chargeback_reason.toLowerCase().includes(searchTerm.toLowerCase());
    const matchStatus =
      statusFilter === "all" ||
      (statusFilter === "pending" && c.requires_human) ||
      (statusFilter === "resolved" && !c.requires_human) ||
      (statusFilter === "fraud" && c.verdict === "fraud") ||
      (statusFilter === "legitimate" && c.verdict === "legitimate");
    return matchSearch && matchStatus;
  });

  return (
    <div className="audit-trail-container">
      <div className="audit-header">
        <div>
          <h2>Disputed Transactions Audit Log</h2>
          <p>Real-time audit trail of all disputes ingested by TathyaAI engine</p>
        </div>

        {/* Filter controls */}
        <div className="audit-filters-group">
          <input
            type="text"
            className="search-input"
            placeholder="Search Case ID or reason..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />

          <select
            className="status-filter-select"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All Cases ({cases.length})</option>
            <option value="pending">Pending Human Ops Review</option>
            <option value="resolved">Auto-Resolved</option>
            <option value="fraud">Fraud Verdict</option>
            <option value="legitimate">Legitimate Verdict</option>
          </select>
        </div>
      </div>

      {/* Audit Table */}
      <div className="table-responsive">
        <table className="audit-table">
          <thead>
            <tr>
              <th>Case ID</th>
              <th>Dispute Amount</th>
              <th>Reason Summary</th>
              <th>Judge Verdict</th>
              <th>Confidence</th>
              <th>Policy Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredCases.map((c) => (
              <tr key={c.case_id} className="case-row">
                <td className="case-id-cell">
                  <button
                    className="case-id-btn"
                    onClick={() => onSelectCase(c)}
                  >
                    {c.case_id}
                  </button>
                </td>
                <td className="amount-cell">
                  ₹{c.chargeback_amount?.toLocaleString("en-IN")}
                </td>
                <td className="reason-cell">{c.chargeback_reason}</td>
                <td>
                  <span className={`verdict-chip ${c.verdict || "fraud"}`}>
                    {(c.verdict || "FRAUD").toUpperCase()}
                  </span>
                </td>
                <td className="confidence-cell">
                  {((c.confidence || 0.88) * 100).toFixed(0)}%
                </td>
                <td>
                  <span
                    className={`policy-pill ${
                      c.requires_human ? "pending" : "resolved"
                    }`}
                  >
                    {c.requires_human
                      ? "⚠️ Pending Human Review"
                      : "✓ Auto Resolved"}
                  </span>
                </td>
                <td>
                  <div className="action-btn-group">
                    <button
                      className="btn btn-xs btn-outline"
                      onClick={() => onSelectCase(c)}
                    >
                      Inspect
                    </button>
                    {c.requires_human && (
                      <button
                        className="btn btn-xs btn-success"
                        onClick={() =>
                          onApproveCase(c.case_id, c.verdict || "resolved")
                        }
                      >
                        Approve
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
