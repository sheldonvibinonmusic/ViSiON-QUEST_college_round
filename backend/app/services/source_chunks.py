"""
Source chunking service.
Splits document text into paragraph-aware chunks of ~120-220 words with ~40 words overlap,
preserving exact character offsets and page metadata.
"""
from typing import List, Optional
from backend.app.schemas import SourceChunk
from backend.app.services.document_parser import ParsedResult
from backend.app.util.hashes import generate_id

def determine_page_for_offset(parsed: ParsedResult, char_offset: int) -> Optional[int]:
    """Find the 1-based page number covering the given character offset."""
    for page in parsed.pages:
        if page.start_char <= char_offset < page.end_char:
            return page.page_number
    # Fallback to the last page if at the boundary
    if parsed.pages and parsed.pages[-1].end_char == char_offset:
        return parsed.pages[-1].page_number
    return None

def chunk_document(
    parsed: ParsedResult,
    target_words: int = 160,
    overlap_words: int = 40,
    min_words: int = 20
) -> List[SourceChunk]:
    """
    Split extracted text into overlapping chunks, tracking exact character offsets.
    If the document has fewer words than target_words, returns a single chunk.
    """
    full_text = parsed.full_text
    doc_id = parsed.document.source_id
    chunks: List[SourceChunk] = []

    if not full_text.strip():
        return chunks

    # We tokenize words while preserving character positions
    # A token is (word_str, start_char, end_char)
    tokens = []
    i = 0
    text_len = len(full_text)
    while i < text_len:
        if full_text[i].isspace():
            i += 1
            continue
        start_pos = i
        while i < text_len and not full_text[i].isspace():
            i += 1
        end_pos = i
        tokens.append((full_text[start_pos:end_pos], start_pos, end_pos))

    if not tokens:
        return chunks

    total_tokens = len(tokens)
    
    # If smaller than target words, produce one single chunk
    if total_tokens <= target_words + min_words:
        start_char = tokens[0][1]
        end_char = tokens[-1][2]
        chunk_text = full_text[start_char:end_char]
        page_num = determine_page_for_offset(parsed, start_char)
        
        return [
            SourceChunk(
                chunk_id=generate_id("chk"),
                source_id=doc_id,
                text=chunk_text,
                start_char=start_char,
                end_char=end_char,
                page_number=page_num,
                section=None,
                retrieval_score=None
            )
        ]

    step = max(1, target_words - overlap_words)
    token_idx = 0

    while token_idx < total_tokens:
        chunk_token_end = min(token_idx + target_words, total_tokens)
        
        # Don't leave a tiny orphaned tail
        remaining = total_tokens - chunk_token_end
        if 0 < remaining < min_words:
            chunk_token_end = total_tokens

        start_char = tokens[token_idx][1]
        end_char = tokens[chunk_token_end - 1][2]
        chunk_text = full_text[start_char:end_char]
        page_num = determine_page_for_offset(parsed, start_char)

        chunks.append(
            SourceChunk(
                chunk_id=generate_id("chk"),
                source_id=doc_id,
                text=chunk_text,
                start_char=start_char,
                end_char=end_char,
                page_number=page_num,
                section=None,
                retrieval_score=None
            )
        )

        if chunk_token_end == total_tokens:
            break

        token_idx += step

    return chunks
