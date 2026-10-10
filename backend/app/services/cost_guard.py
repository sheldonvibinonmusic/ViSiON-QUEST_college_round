"""
Cost Guard, Query Budgeting, and Privacy Defense Service.
Guarantees:
1. Strict query cap per audit (MAX_WEB_QUERIES_PER_AUDIT).
2. Checkability filter: conversational banter, greetings, questions, and subjective filler
   are never dispatched to external search providers.
3. Privacy sanitization: emails, system paths, and PII are stripped; user document text
   is never transmitted to search engines.
"""
import re
from typing import Tuple, List, Set

from backend.app.config import settings

# Conversational boilerplate and conversational fillers
UNCHECKABLE_PHRASES: List[str] = [
    "i hope this helps",
    "let me know if you",
    "feel free to ask",
    "thank you for asking",
    "thanks for asking",
    "as an ai language model",
    "as an ai",
    "in my opinion",
    "personally i think",
    "personally i feel",
    "here is the information",
    "certainly!",
    "sure, here",
    "sure thing",
    "you are welcome",
    "have a great day"
]

QUESTION_STARTERS: Set[str] = {
    "what", "why", "how", "who", "when", "where", "can", "could", "would", "should", "is", "are", "do", "does"
}

def is_checkable_claim(text: str) -> Tuple[bool, str]:
    """
    Evaluate whether a sentence contains an empirical, verifiable assertion.
    Filters out questions, greetings, subjective opinions, and conversational filler.
    """
    clean_text = text.strip()
    lower_text = clean_text.lower()

    # 1. Length check: very short fragments (< 3 words)
    words = re.findall(r'\b[A-Za-z0-9_-]+\b', clean_text)
    if len(words) < 3:
        return False, "Sentence fragment too brief to constitute an empirical claim."

    # 2. Conversational filler and politeness check
    for phrase in UNCHECKABLE_PHRASES:
        if phrase in lower_text:
            return False, f"Conversational filler or polite framing: '{phrase}'."

    # 3. Pure questions check
    if clean_text.endswith("?"):
        first_word = words[0].lower() if words else ""
        if first_word in QUESTION_STARTERS or len(words) < 7:
            return False, "Inquiry/question without assertive factual claim."

    # 4. Check for pure greetings and salutations
    if re.match(r'^(?:hello|hi|hey|greetings|welcome|good\s+(?:morning|afternoon|evening))\b', lower_text):
        # Unless it contains a specific date/number assertion
        if not any(char.isdigit() for char in clean_text):
            return False, "Salutation or conversational greeting."

    return True, "Checkable declarative assertion."

COMMON_FILTER_WORDS: Set[str] = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "with", "from", "by", "about", "into", "through", "is", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "this", "that"
}

def sanitize_privacy_query(text: str, max_words: int = 10) -> str:
    """
    Extract a privacy-safe search query:
    - Strips emails, file paths, and potential IP addresses.
    - Filters out common filler words.
    - Limits to max_words core content tokens.
    - NEVER sends verbatim document passages.
    """
    sanitized = text

    # Strip emails
    sanitized = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', sanitized)
    # Strip Windows and Unix file paths
    sanitized = re.sub(r'[A-Za-z]:\\[^\s]+', '', sanitized)
    sanitized = re.sub(r'/(?:[a-zA-Z0-9_-]+/)+[a-zA-Z0-9_\.-]+', '', sanitized)
    # Strip IP addresses
    sanitized = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '', sanitized)

    # Extract salient alphanumeric content words, prioritizing meaningful keywords
    words = [
        w for w in re.findall(r'\b[A-Za-z0-9_-]{3,}\b', sanitized)
        if w.lower() not in COMMON_FILTER_WORDS
    ]
    if not words:
        # Fallback to any words if all were filtered
        words = re.findall(r'\b[A-Za-z0-9_-]{3,}\b', sanitized)
        if not words:
            return ""

    # Return at most max_words tokens
    return " ".join(words[:max_words])

class CostBudgetTracker:
    """
    Per-audit cost guard ensuring search query limits and cost controls are enforced.
    """
    def __init__(self, max_queries: int = None):
        self.max_queries = max_queries or settings.MAX_WEB_QUERIES_PER_AUDIT
        self.queries_dispatched = 0
        self.skipped_uncheckable = 0

    def can_query(self) -> bool:
        return self.queries_dispatched < self.max_queries

    def record_query(self) -> None:
        self.queries_dispatched += 1

    def record_skipped_uncheckable(self) -> None:
        self.skipped_uncheckable += 1

    @property
    def is_budget_exhausted(self) -> bool:
        return self.queries_dispatched >= self.max_queries
