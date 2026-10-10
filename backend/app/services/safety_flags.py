"""
Safety and high-stakes domain warning service.
Keeps potential safety, medical, legal, and financial concerns strictly separated
from factual support verdicts in dedicated concern arrays.
"""
import re
from typing import List

MEDICAL_PATTERNS = [
    r'\b(?:diagnos(?:e|is|ed)|prescrib(?:e|ed|ing)|cure|dosage|symptoms\s+indicate)\b',
    r'\b(?:take\s+\d+\s*mg|stop\s+taking\s+medication)\b'
]

LEGAL_PATTERNS = [
    r'\b(?:legally\s+binding\s+guarantee|admissible\s+in\s+court|waives\s+all\s+rights)\b',
    r'\b(?:guaranteed\s+verdict|attorney-client\s+privilege)\b'
]

FINANCIAL_PATTERNS = [
    r'\b(?:guaranteed\s+(?:return|profit|roi)|risk-free\s+investment)\b',
    r'\b(?:100%\s+certain\s+market|foolproof\s+trading)\b'
]

def check_safety_concerns(claim_text: str) -> List[str]:
    """
    Check if a claim touches high-stakes domains with prescriptive language.
    Returns advisory warning strings; does NOT alter factual verification verdict.
    """
    concerns: List[str] = []
    text_lower = claim_text.lower()

    for pat in MEDICAL_PATTERNS:
        if re.search(pat, text_lower):
            concerns.append(
                "Health/Medical advisory: Claim contains prescriptive health language. Second Opinion is not certified medical software."
            )
            break

    for pat in LEGAL_PATTERNS:
        if re.search(pat, text_lower):
            concerns.append(
                "Legal advisory: Claim touches legal enforceability. Second Opinion is not a legal decision-making tool."
            )
            break

    for pat in FINANCIAL_PATTERNS:
        if re.search(pat, text_lower):
            concerns.append(
                "Financial advisory: Claim asserts guaranteed financial returns. Verify with certified financial disclosures."
            )
            break

    return concerns
