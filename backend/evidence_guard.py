"""
Catches hallucinated evidence: if an agent cites a 'signal' that doesn't
correspond to any real field we actually provided, that citation is
fabricated. Zero API cost — pure keyword matching against known fields.
"""

KNOWN_FIELD_KEYWORDS = [
    "account_age", "age", "transaction", "chargeback", "flag",
    "linked", "device", "ip_address", "ip", "payment_method",
    "upi", "card", "netbanking", "amount", "reason",
    "product_not_as_described", "unauthorized_transaction",
    "duplicate_charge", "subscription_cancelled", "item_not_received",
]


def find_unverifiable_signals(cited_signals: list[str]) -> list[str]:
    """Returns cited signals that match none of our real data fields —
    these are likely hallucinated and must not be trusted."""
    unverifiable = []
    for signal in cited_signals:
        signal_lower = signal.lower()
        if not any(kw in signal_lower for kw in KNOWN_FIELD_KEYWORDS):
            unverifiable.append(signal)
    return unverifiable