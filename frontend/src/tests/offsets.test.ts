import { describe, it, expect } from 'vitest'
import { buildHighlightedSegments } from '../lib/offsets'
import type { ClaimFinding } from '../api/client'

describe('buildHighlightedSegments', () => {
  it('handles empty findings by returning whole text as unhighlighted', () => {
    const text = 'This is a sample answer.'
    const segments = buildHighlightedSegments(text, [])
    expect(segments).toHaveLength(1)
    expect(segments[0].text).toBe(text)
    expect(segments[0].isClaim).toBe(false)
  })

  it('correctly slices text before, during, and after claim spans', () => {
    const text = 'Prefix text. Highlighted claim. Suffix text.'
    const findings: ClaimFinding[] = [
      {
        claim_id: 'c1',
        claim_text: 'Highlighted claim.',
        start_char: 13,
        end_char: 31,
        verdict: 'SUPPORTED_BY_SOURCE',
        explanation: 'Supported',
        evidence: [],
        logic_concerns: [],
        safety_concerns: [],
        review_priority: 'low',
        evidence_strength: 0.9,
        warnings: [],
      },
    ]

    const segments = buildHighlightedSegments(text, findings)
    expect(segments).toHaveLength(3)

    expect(segments[0].text).toBe('Prefix text. ')
    expect(segments[0].isClaim).toBe(false)

    expect(segments[1].text).toBe('Highlighted claim.')
    expect(segments[1].isClaim).toBe(true)
    expect(segments[1].finding?.claim_id).toBe('c1')

    expect(segments[2].text).toBe(' Suffix text.')
    expect(segments[2].isClaim).toBe(false)
  })

  it('handles overlapping finding ranges without duplicating text', () => {
    const text = 'First claim text here.'
    const findings: ClaimFinding[] = [
      {
        claim_id: 'c1',
        claim_text: 'First claim',
        start_char: 0,
        end_char: 11,
        verdict: 'SUPPORTED_BY_SOURCE',
        explanation: 'Supported',
        evidence: [],
        logic_concerns: [],
        safety_concerns: [],
        review_priority: 'low',
        evidence_strength: 0.9,
        warnings: [],
      },
      {
        claim_id: 'c2',
        claim_text: 'claim text',
        start_char: 6,
        end_char: 16,
        verdict: 'CONTRADICTED_BY_SOURCE',
        explanation: 'Contradicted',
        evidence: [],
        logic_concerns: [],
        safety_concerns: [],
        review_priority: 'high',
        evidence_strength: 0.8,
        warnings: [],
      },
    ]

    const segments = buildHighlightedSegments(text, findings)
    const reconstructed = segments.map((s) => s.text).join('')
    expect(reconstructed).toBe(text)
  })
})
