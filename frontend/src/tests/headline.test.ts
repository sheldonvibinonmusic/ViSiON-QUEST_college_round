import { describe, it, expect } from 'vitest'
import { HEADLINE_MESSAGES } from '../constants/headlines'

describe('Landing Page Headline Sequence', () => {
  it('contains the exact four approved fact-checking messages in correct sequence', () => {
    expect(HEADLINE_MESSAGES).toHaveLength(4)
    expect(HEADLINE_MESSAGES[0]).toBe('Where hallucinations come to an end.')
    expect(HEADLINE_MESSAGES[1]).toBe('Your AI fact-checking copilot.')
    expect(HEADLINE_MESSAGES[2]).toBe(
      'Cross-check AI answers against PDFs, URLs, and source documents.'
    )
    expect(HEADLINE_MESSAGES[3]).toBe(
      "Find the claims supported by evidence—and the ones that aren't."
    )
  })

  it('cycles through all messages in order and loops back to the first', () => {
    let index = 0
    const sequence: string[] = []

    for (let step = 0; step < 8; step++) {
      sequence.push(HEADLINE_MESSAGES[index])
      index = (index + 1) % HEADLINE_MESSAGES.length
    }

    expect(sequence).toEqual([
      'Where hallucinations come to an end.',
      'Your AI fact-checking copilot.',
      'Cross-check AI answers against PDFs, URLs, and source documents.',
      "Find the claims supported by evidence—and the ones that aren't.",
      'Where hallucinations come to an end.',
      'Your AI fact-checking copilot.',
      'Cross-check AI answers against PDFs, URLs, and source documents.',
      "Find the claims supported by evidence—and the ones that aren't.",
    ])
  })
})
