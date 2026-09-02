from schemas import JudgeVerdict


class PolicyDecision:
    def __init__(self, final_verdict: str, requires_human: bool, override_reason: str = None):
        self.final_verdict = final_verdict
        self.requires_human = requires_human
        self.override_reason = override_reason


# Hard limits — the LLM cannot override these no matter what it says
AUTO_DECIDE_CONFIDENCE = 0.85
HIGH_VALUE_THRESHOLD = 15000  # ₹ — always human review above this
def apply_policy(verdict: JudgeVerdict, chargeback_amount: float, 
                  fraud_confidence: float, defense_confidence: float) -> PolicyDecision:

    if chargeback_amount > HIGH_VALUE_THRESHOLD:
        return PolicyDecision(
            final_verdict=verdict.verdict,
            requires_human=True,
            override_reason=f"Amount ₹{chargeback_amount} exceeds ₹{HIGH_VALUE_THRESHOLD} auto-limit"
        )

    # Cross-check: if the two advocates were closely matched, the judge's
    # confidence alone isn't trustworthy enough to auto-decide
    confidence_gap = abs(fraud_confidence - defense_confidence)
    if confidence_gap < 0.15:
        return PolicyDecision(
            final_verdict=verdict.verdict,
            requires_human=True,
            override_reason=f"Fraud/defense confidence gap only {confidence_gap:.2f} — too close to auto-decide"
        )

    if verdict.verdict == "insufficient_evidence":
        return PolicyDecision(
            final_verdict=verdict.verdict,
            requires_human=True,
            override_reason="Judge reported insufficient evidence"
        )

    if verdict.confidence < AUTO_DECIDE_CONFIDENCE:
        return PolicyDecision(
            final_verdict=verdict.verdict,
            requires_human=True,
            override_reason=f"Confidence {verdict.confidence} below {AUTO_DECIDE_CONFIDENCE} threshold"
        )

    if verdict.requires_human:
        return PolicyDecision(
            final_verdict=verdict.verdict,
            requires_human=True,
            override_reason="Judge flagged for human review"
        )

    return PolicyDecision(final_verdict=verdict.verdict, requires_human=False, override_reason=None)


