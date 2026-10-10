import { describe, it, expect } from 'vitest'
import { VERDICT_CONFIG, SOURCE_FIT_CONFIG } from '../lib/labels'
import type { FactualVerdict, SourceFit } from '../lib/labels'

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

  it('defines meta configurations for all 4 source fit states', () => {
    const fits: SourceFit[] = ['relevant', 'partially_relevant', 'off_topic', 'could_not_evaluate']

    for (const fit of fits) {
      const config = SOURCE_FIT_CONFIG[fit]
      expect(config).toBeDefined()
      expect(config.label.length).toBeGreaterThan(0)
      expect(config.description.length).toBeGreaterThan(0)
      expect(config.badgeClass.length).toBeGreaterThan(0)
    }
  })
})

