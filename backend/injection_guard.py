import re

SUSPICIOUS_PATTERNS = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"system\s*override",
    r"you are now",
    r"disregard (all )?(other )?signals",
    r"(is|are) on file",
    r"confirmation #",
    r"reference number",
    r"set confidence to",
    r"auto[-\s]?approve",
    r"i am a (razorpay|compliance|admin)",
    r"do not consider",
    r"respond only with",
    r"treat (this|it) as",
]


def detect_injection(text: str) -> list[str]:
    """Code-level check — runs before the text ever reaches the LLM.
    Returns the list of suspicious patterns matched, empty if clean."""
    if not text:
        return []
    lower = text.lower()
    return [p for p in SUSPICIOUS_PATTERNS if re.search(p, lower)]