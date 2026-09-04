import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import HeroBanner from "./components/HeroBanner";
import CaseInvestigator from "./components/CaseInvestigator";
import AdhocInvestigator from "./components/AdhocInvestigator";
import AuditTrailTable from "./components/AuditTrailTable";
import MetricsOverview from "./components/MetricsOverview";
import Footer from "./components/Footer";
import CurrencyCanvas from "./components/CurrencyCanvas";
import RupeeCursor from "./components/RupeeCursor";
import { useSmoothScroll } from "./hooks/useSmoothScroll";

import {
  checkBackendHealth,
  getCases,
  getCaseDetails,
  runAdhocInvestigation,
  approveCase,
} from "./services/apiClient";

export default function App() {
  useSmoothScroll();

  const [activeTab, setActiveTab] = useState("overview");
  const [backendStatus, setBackendStatus] = useState({ status: "checking" });
  const [cases, setCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [isInvestigating, setIsInvestigating] = useState(false);
  const [notesPaused, setNotesPaused] = useState(false);

  // Initialize data & check health
  useEffect(() => {
    async function init() {
      const health = await checkBackendHealth();
      setBackendStatus(health);

      const fetchedCases = await getCases();
      setCases(fetchedCases);
      if (fetchedCases.length > 0) {
        const detail = await getCaseDetails(fetchedCases[0].case_id);
        setSelectedCase(detail);
      }
    }
    init();
  }, []);

  const handleSelectCase = async (caseRow) => {
    setSelectedCase(caseRow);
    setActiveTab("investigate");
    const detail = await getCaseDetails(caseRow.case_id);
    setSelectedCase(detail);
  };

  const handleRunInvestigation = async (caseId) => {
    setIsInvestigating(true);
    try {
      const detail = await getCaseDetails(caseId);
      setSelectedCase(detail);
    } catch (err) {
      console.error("Failed to investigate:", err);
    } finally {
      setIsInvestigating(false);
    }
  };

  const handleAdhocSubmit = async (payload) => {
    setIsInvestigating(true);
    try {
      const traceResult = await runAdhocInvestigation(payload);
      const newAdhocCase = {
        case_id: traceResult.case_id,
        chargeback_amount: traceResult.chargeback_amount,
        chargeback_reason: traceResult.chargeback_reason,
        verdict: traceResult.final_verdict,
        confidence: traceResult.judge_verdict?.confidence || 0.88,
        requires_human: traceResult.final_requires_human,
        status: traceResult.final_requires_human ? "pending_human" : "resolved",
        created_at: new Date().toISOString(),
        transaction: {
          transaction_id: "txn_adhoc_" + Math.floor(Math.random() * 90000 + 10000),
          amount: traceResult.chargeback_amount,
          payment_method: "UPI (Live Demo)",
        },
        customer: {
          email: "redteam.user@tathya.ai",
          account_age_days: 14,
          total_transactions: 3,
          total_chargebacks: 1,
          chargeback_rate: 0.33,
        },
        device: {
          device_id: "dev_redteam_macbook",
          ip_address: "103.211.54.12",
          accounts_linked: 4,
          is_flagged: true,
        },
        trace: traceResult,
      };

      setCases((prev) => [newAdhocCase, ...prev]);
      setSelectedCase(newAdhocCase);
      return traceResult;
    } finally {
      setIsInvestigating(false);
    }
  };

  const handleApproveCase = async (caseId, decision) => {
    await approveCase(caseId, decision);
    setCases((prev) =>
      prev.map((c) =>
        c.case_id === caseId
          ? { ...c, requires_human: false, status: "resolved" }
          : c
      )
    );
    if (selectedCase && selectedCase.case_id === caseId) {
      setSelectedCase((prev) => ({
        ...prev,
        requires_human: false,
        status: "resolved",
      }));
    }
  };

  return (
    <div className="app-root">
      {/* Background Indian Currency Notes Canvas Animation */}
      <CurrencyCanvas isPaused={notesPaused} />

      {/* Custom Indian Rupee Sign Cursor Follower */}
      <RupeeCursor />

      {/* Navigation Header */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        backendStatus={backendStatus}
        notesPaused={notesPaused}
        setNotesPaused={setNotesPaused}
      />

      {/* Main Content Area */}
      <main className="main-content">
        {activeTab === "overview" && (
          <>
            <HeroBanner
              onExploreClick={() => setActiveTab("investigate")}
              onAdhocClick={() => setActiveTab("adhoc")}
            />
            <MetricsOverview />
            <AuditTrailTable
              cases={cases}
              onSelectCase={handleSelectCase}
              onApproveCase={handleApproveCase}
            />
          </>
        )}

        {activeTab === "investigate" && (
          <CaseInvestigator
            cases={cases}
            selectedCase={selectedCase}
            setSelectedCase={setSelectedCase}
            onRunInvestigation={handleRunInvestigation}
            onApproveCase={handleApproveCase}
            isInvestigating={isInvestigating}
          />
        )}

        {activeTab === "adhoc" && (
          <AdhocInvestigator
            onSubmitAdhoc={handleAdhocSubmit}
            isLoading={isInvestigating}
          />
        )}

        {activeTab === "audit" && (
          <AuditTrailTable
            cases={cases}
            onSelectCase={handleSelectCase}
            onApproveCase={handleApproveCase}
          />
        )}
      </main>

      {/* Footer with contact email */}
      <Footer />
    </div>
  );
}