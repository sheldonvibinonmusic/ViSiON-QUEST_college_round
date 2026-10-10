import type { ClaimFinding } from '../api/client'

export interface HighlightedSegment {
  text: string
  isClaim: boolean
  finding?: ClaimFinding
}

export function buildHighlightedSegments(
  originalAnswer: string,
  findings: ClaimFinding[],
): HighlightedSegment[] {
  if (!originalAnswer || findings.length === 0) {
    return [{ text: originalAnswer, isClaim: false }]
  }

  // Backend offsets count Unicode code points; String.slice indexes UTF-16 code units.
  const codePointToUtf16 = [0]
  let utf16Offset = 0
  for (const codePoint of originalAnswer) {
    utf16Offset += codePoint.length
    codePointToUtf16.push(utf16Offset)
  }

  const orderedFindings = findings
    .map((finding, index) => ({ finding, index }))
    .sort(
      (left, right) =>
        left.finding.start_char - right.finding.start_char ||
        left.finding.end_char - right.finding.end_char ||
        left.index - right.index,
    )

  const segments: HighlightedSegment[] = []
  let cursor = 0

  for (const { finding } of orderedFindings) {
    const { start_char: startCodePoint, end_char: endCodePoint } = finding
    if (
      !Number.isInteger(startCodePoint) ||
      !Number.isInteger(endCodePoint) ||
      startCodePoint < 0 ||
      endCodePoint <= startCodePoint ||
      endCodePoint >= codePointToUtf16.length
    ) {
      continue
    }

    const start = codePointToUtf16[startCodePoint]
    const end = codePointToUtf16[endCodePoint]
    if (start < cursor) continue

    if (start > cursor) {
      segments.push({ text: originalAnswer.slice(cursor, start), isClaim: false })
    }
    segments.push({ text: originalAnswer.slice(start, end), isClaim: true, finding })
    cursor = end
  }

  if (cursor < originalAnswer.length) {
    segments.push({ text: originalAnswer.slice(cursor), isClaim: false })
  }

  return segments.length > 0 ? segments : [{ text: originalAnswer, isClaim: false }]
}
