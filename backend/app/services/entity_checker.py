"""
Exact-Entity and Citation verification module for Second Opinion.
Extracts proper nouns, quoted strings, citation patterns, and acronyms from claims,
ensuring that made-up or hallucinated entities are strictly prevented from passing as SUPPORTED (F3).
"""
import re
from typing import Dict, List, Optional, Set, Tuple

COMMON_SENTENCE_STARTERS = {
    "the", "this", "that", "these", "those", "there", "here", "it",
    "in", "on", "at", "for", "with", "according", "however", "furthermore",
    "moreover", "meanwhile", "additionally", "first", "second", "finally"
}

GENERIC_ORGANIZATION_TERMS = {
    "organization", "company", "corporation", "department", "agency",
    "ministry", "court", "tribunal", "committee", "commission", "board",
    "university", "college", "school", "institute", "center", "centre",
    "hospital", "system", "group", "association", "foundation"
}


def extract_claim_entities(text: str) -> Set[str]:
    """
    Extract specific proper nouns, legal/academic citations, quoted strings, and acronyms.
    """
    entities: Set[str] = set()

    # 1. Quoted names and titles (e.g. "Magna Carta", 'General Relativity')
    for m in re.finditer(r'["\']([^"\']{3,50})["\']', text):
        entities.add(m.group(1).strip().lower())

    # 2. Legal case citations (e.g. 'Smith v. Jones', 'Brown v. Board of Education')
    for m in re.finditer(r'\b[A-Z][a-zA-Z0-9_\'-]+\s+(?:v\.|vs\.|versus)\s+[A-Z][a-zA-Z0-9_\'-]+(?:\s+[A-Z][a-zA-Z0-9_\'-]+)*\b', text):
        entities.add(m.group(0).strip().lower())

    # 3. Document, standard, or statutory citations (e.g. 'RFC 2616', 'Section 12(b)', '42 U.S.C.')
    for m in re.finditer(r'\b(?:RFC|ISO|IEEE|NIST|Section|Article|Act of)\s+[A-Za-z0-9_.-]+\b', text, re.IGNORECASE):
        entities.add(m.group(0).strip().lower())

    # 4. Multi-word capitalized proper noun sequences (e.g. 'Albert Einstein', 'Hubble Space Telescope')
    matches = re.findall(r'\b[A-Z][a-zA-Z0-9_-]+(?:\s+[A-Z][a-zA-Z0-9_-]+)+\b', text)
    for m in matches:
        words = m.split()
        if len(words) == 1 and words[0].lower() in COMMON_SENTENCE_STARTERS:
            continue
        # Filter if the first word is a common sentence starter (e.g. 'According to Dr. Smith')
        if words[0].lower() in COMMON_SENTENCE_STARTERS:
            trimmed = " ".join(words[1:])
            if trimmed:
                entities.add(trimmed.strip().lower())
        else:
            entities.add(m.strip().lower())

    # 5. Distinctive acronyms (e.g. 'NASA', 'CERN', 'UNICEF', 'HIPAA', 'FERPA')
    for m in re.finditer(r'\b[A-Z]{3,8}\b', text):
        acronym = m.group(0).lower()
        if acronym not in ("the", "and", "for", "not", "any", "all"):
            entities.add(acronym)

    return entities


class EntityCheckResult:
    def __init__(
        self,
        all_entities_present: bool = True,
        missing_entities: Optional[List[str]] = None,
        verified_entities: Optional[List[str]] = None,
        reason: str = ""
    ):
        self.all_entities_present = all_entities_present
        self.missing_entities = missing_entities or []
        self.verified_entities = verified_entities or []
        self.reason = reason


def check_exact_entities(
    claim_text: str,
    evidence_quote: str,
    full_source_text: Optional[str] = None
) -> EntityCheckResult:
    """
    Ensure every specific named entity or citation asserted in the claim is grounded
    in the candidate evidence quote or the parent source document.
    """
    claim_entities = extract_claim_entities(claim_text)
    if not claim_entities:
        return EntityCheckResult(all_entities_present=True, reason="No specific named entities or citations in claim.")

    quote_lower = evidence_quote.lower()
    full_source_lower = full_source_text.lower() if full_source_text else quote_lower

    missing: List[str] = []
    verified: List[str] = []

    for ent in claim_entities:
        # Check if full entity or key distinctive words appear in quote or full source
        ent_words = [w for w in ent.split() if len(w) >= 3 and w not in COMMON_SENTENCE_STARTERS]
        distinctive_words = [w for w in ent_words if w not in GENERIC_ORGANIZATION_TERMS]
        check_words = distinctive_words if distinctive_words else ent_words

        # Check direct string match
        if ent in quote_lower or ent in full_source_lower:
            verified.append(ent)
        # Check surname / principal head noun for multi-word entities (e.g. 'Albert Einstein' matched by 'Einstein' / 'Einstein\'s')
        elif len(ent_words) > 1 and len(ent_words[-1]) >= 4 and not any(p in ent for p in ("rfc", "iso", "section", "article", " v.", " vs.")) and (ent_words[-1] in quote_lower or ent_words[-1] in full_source_lower):
            verified.append(ent)
        elif check_words and all(w in quote_lower or w in full_source_lower for w in check_words):
            verified.append(ent)
        else:
            missing.append(ent)

    if missing:
        reason = f"Asserted named entity or citation not found in source evidence: {', '.join(missing[:3])}"
        return EntityCheckResult(
            all_entities_present=False,
            missing_entities=missing,
            verified_entities=verified,
            reason=reason
        )

    return EntityCheckResult(
        all_entities_present=True,
        missing_entities=[],
        verified_entities=verified,
        reason=f"Verified grounded entities: {', '.join(verified[:3])}"
    )
