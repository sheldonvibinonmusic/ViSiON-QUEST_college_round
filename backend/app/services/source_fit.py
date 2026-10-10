"""
Source Fit Check Service.
Evaluates topical and domain alignment between the answer/claims and supplied sources
before detailed auditing, preventing domain-mismatched sources from producing false contradictions.
"""
import re
from typing import List, Set, Dict, Optional, Tuple
from collections import Counter

from backend.app.config import settings
from backend.app.schemas import (
    Claim,
    SourceChunk,
    SourceDocument,
    SourceFitLevel,
    SourceFitDocument,
    SourceFitSummary,
)

# Standard common English stopwords
STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
    "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "also", "many", "well", "much"
}

def extract_salient_terms(text: str) -> List[str]:
    """
    Extract salient content words and bigrams from text, discarding stopwords and punctuation.
    """
    words = re.findall(r"\b[A-Za-z0-9_-]{3,}\b", text.lower())
    content_words = [w for w in words if w not in STOPWORDS and not w.isdigit()]
    
    # Extract high-value bigrams for domain specificity (e.g., 'quantum mechanics', 'cell division')
    bigrams = []
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        if w1 not in STOPWORDS and w2 not in STOPWORDS and not w1.isdigit() and not w2.isdigit():
            bigrams.append(f"{w1} {w2}")
    
    # Prioritize terms by frequency while preserving uniqueness
    term_counts = Counter(content_words + bigrams)
    # Sort by frequency descending
    salient = [term for term, _ in term_counts.most_common()]
    return salient

def check_source_fit(
    answer: str,
    claims: List[Claim],
    chunks: List[SourceChunk],
    source_documents: List[SourceDocument],
    min_score_override: Optional[float] = None
) -> SourceFitSummary:
    """
    Assess topical fit between the answer/claims and supplied source documents.
    Returns a SourceFitSummary containing document-level scores and overall classification.
    """
    if not source_documents or not chunks:
        return SourceFitSummary(
            overall_fit=SourceFitLevel.OFF_TOPIC,
            average_fit_score=0.0,
            all_sources_off_topic=True,
            documents=[],
            explanation="No source documents or chunks available for fit evaluation."
        )

    # 1. Extract salient terms from answer and claims
    combined_query_text = answer + " " + " ".join([c.text for c in claims])
    salient_terms = extract_salient_terms(combined_query_text)

    # If no salient terms could be extracted (e.g., extreme edge case of stopword-only text), return neutral fit
    if not salient_terms:
        doc_summaries = [
            SourceFitDocument(
                source_id=doc.source_id,
                filename=doc.filename,
                fit_level=SourceFitLevel.PARTIALLY_RELEVANT,
                fit_score=0.5,
                matched_terms=[],
                missing_topics=[],
                reason="Insufficient salient terms in input text to determine domain specificity."
            )
            for doc in source_documents
        ]
        return SourceFitSummary(
            overall_fit=SourceFitLevel.PARTIALLY_RELEVANT,
            average_fit_score=0.5,
            all_sources_off_topic=False,
            documents=doc_summaries,
            explanation="Input text contained insufficient topical terms to gauge domain specificity."
        )

    # Thresholds
    off_topic_threshold = min_score_override if min_score_override is not None else settings.SOURCE_FIT_OFF_TOPIC_THRESHOLD
    relevant_threshold = settings.SOURCE_FIT_RELEVANT_THRESHOLD

    # 2. Group chunks by source_id
    chunks_by_source: Dict[str, List[SourceChunk]] = {}
    for chunk in chunks:
        chunks_by_source.setdefault(chunk.source_id, []).append(chunk)

    doc_summaries: List[SourceFitDocument] = []

    # 3. Score each document
    for doc in source_documents:
        doc_chunks = chunks_by_source.get(doc.source_id, [])
        if not doc_chunks:
            doc_summaries.append(
                SourceFitDocument(
                    source_id=doc.source_id,
                    filename=doc.filename,
                    fit_level=SourceFitLevel.OFF_TOPIC,
                    fit_score=0.0,
                    matched_terms=[],
                    missing_topics=salient_terms[:5],
                    reason=f"Source '{doc.filename}' contained no extractable textual chunks."
                )
            )
            continue

        doc_full_text = " ".join([ch.text.lower() for ch in doc_chunks])
        doc_tokens = set(re.findall(r"\b[A-Za-z0-9_-]{3,}\b", doc_full_text))

        # Check matched vs missing salient terms
        matched_terms = [t for t in salient_terms if (t in doc_tokens or (t in doc_full_text))]
        missing_terms = [t for t in salient_terms if t not in matched_terms]

        # Lexical coverage ratio over salient vocabulary
        coverage_ratio = len(matched_terms) / len(salient_terms)

        # Claim-level coverage: how many individual claims find at least one term match in this doc
        claim_matches = 0
        for claim in claims:
            claim_terms = [w for w in re.findall(r"\b[A-Za-z0-9_-]{3,}\b", claim.text.lower()) if w not in STOPWORDS]
            if claim_terms and any(w in doc_tokens for w in claim_terms):
                claim_matches += 1
        claim_coverage = claim_matches / max(len(claims), 1)

        # Combined fit score (0.0 to 1.0)
        fit_score = round(min(1.0, max(0.0, 0.6 * coverage_ratio + 0.4 * claim_coverage)), 3)

        # Classify fit level
        if fit_score < off_topic_threshold:
            fit_level = SourceFitLevel.OFF_TOPIC
            reason = (
                f"Source '{doc.filename}' has {fit_score:.0%} topic overlap (below threshold {off_topic_threshold:.0%}). "
                f"Lacks key concepts: {', '.join(missing_terms[:5])}."
            )
        elif fit_score < relevant_threshold:
            fit_level = SourceFitLevel.PARTIALLY_RELEVANT
            reason = (
                f"Source '{doc.filename}' has moderate topical overlap ({fit_score:.0%}). "
                f"Covers some terms ({', '.join(matched_terms[:3])}) but lacks others ({', '.join(missing_terms[:3])})."
            )
        else:
            fit_level = SourceFitLevel.RELEVANT
            reason = (
                f"Source '{doc.filename}' demonstrates strong topical alignment ({fit_score:.0%}) "
                f"covering key concepts: {', '.join(matched_terms[:5])}."
            )

        doc_summaries.append(
            SourceFitDocument(
                source_id=doc.source_id,
                filename=doc.filename,
                fit_level=fit_level,
                fit_score=fit_score,
                matched_terms=matched_terms[:10],
                missing_topics=missing_terms[:10],
                reason=reason
            )
        )

    # 4. Compute overall summary
    avg_score = round(sum(d.fit_score for d in doc_summaries) / len(doc_summaries), 3) if doc_summaries else 0.0
    all_off_topic = all(d.fit_level == SourceFitLevel.OFF_TOPIC for d in doc_summaries) if doc_summaries else True
    has_relevant = any(d.fit_level == SourceFitLevel.RELEVANT for d in doc_summaries)

    if all_off_topic:
        overall_fit = SourceFitLevel.OFF_TOPIC
        explanation = (
            f"All supplied sources ({len(doc_summaries)}) appear off-topic for this answer "
            f"(average fit: {avg_score:.0%}). The evidence does not address the requested domain."
        )
    elif has_relevant and avg_score >= relevant_threshold:
        overall_fit = SourceFitLevel.RELEVANT
        explanation = f"Supplied sources show good overall topical coverage ({avg_score:.0%})."
    else:
        overall_fit = SourceFitLevel.PARTIALLY_RELEVANT
        explanation = f"Supplied sources provide partial or mixed coverage for the answer ({avg_score:.0%})."

    return SourceFitSummary(
        overall_fit=overall_fit,
        average_fit_score=avg_score,
        all_sources_off_topic=all_off_topic,
        documents=doc_summaries,
        explanation=explanation
    )
