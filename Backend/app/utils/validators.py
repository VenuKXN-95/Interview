"""
Shared validation helpers used across service layers.
"""
import re

# Anchored pattern for validating a standalone email string
EMAIL_VALIDATE_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
# Non-anchored pattern for searching email in text
EMAIL_SEARCH_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"[\+\d][\d\s\-\(\)]{7,20}")

# Keep legacy alias for backward compat
EMAIL_RE = EMAIL_VALIDATE_RE


def is_valid_email(email: str) -> bool:
    return bool(EMAIL_VALIDATE_RE.match(email.strip()))


def extract_email(text: str) -> str | None:
    """Extract the first email address found in a block of text."""
    match = EMAIL_SEARCH_RE.search(text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    """Extract the first phone number found in a block of text."""
    match = PHONE_RE.search(text)
    return match.group(0).strip() if match else None


def is_meaningful_text(text: str, min_chars: int = 50) -> bool:
    """Return True if the text has enough content to be processed."""
    return len(text.strip()) >= min_chars


def clamp_score(score: float, lo: float = 0.0, hi: float = 10.0) -> float:
    """Clamp a score to [lo, hi]."""
    return max(lo, min(hi, score))
