import { describe, it, expect } from 'vitest'
import { VERDICT_CONFIG } from '../lib/labels'
import type { FactualVerdict } from '../lib/labels'

describe('VERDICT_CONFIG', () => {
  it('defines meta configurations for all 4 required verdicts', () => {
    const verdicts: FactualVerdict[] = [
      'SUPPORTED_BY_SOURCE',
      'CONTRADICTED_BY_SOURCE',
      'NOT_ESTABLISHED_BY_SOURCE',
      'AMBIGUOUS_OR_CONFLICTING',
    ]

    for (const v of verdicts) {
      const config = VERDICT_CONFIG[v]
      expect(config).toBeDefined()
      expect(config.label.length).toBeGreaterThan(0)
      expect(config.badgeClass.length).toBeGreaterThan(0)
      expect(config.highlightClass.length).toBeGreaterThan(0)
    }
  })
})
