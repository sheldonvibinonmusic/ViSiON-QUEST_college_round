export type FactualVerdict =
  | 'SUPPORTED_BY_SOURCE'
  | 'CONTRADICTED_BY_SOURCE'
  | 'NOT_ESTABLISHED_BY_SOURCE'
  | 'AMBIGUOUS_OR_CONFLICTING'

interface VerdictConfig {
  label: string
  description: string
  badgeClass: string
  highlightClass: string
}

export const VERDICT_CONFIG: Record<FactualVerdict, VerdictConfig> = {
  SUPPORTED_BY_SOURCE: {
    label: 'Supported',
    description: 'Claims verified',
    badgeClass:
      'bg-[var(--v-supported-bg)] border-[var(--v-supported-border)] text-[var(--v-supported-ink)]',
    highlightClass: 'bg-[var(--v-supported-bg)] text-[var(--v-supported-ink)]',
  },
  CONTRADICTED_BY_SOURCE: {
    label: 'Contradicted',
    description: 'Direct conflicts',
    badgeClass:
      'bg-[var(--v-contradicted-bg)] border-[var(--v-contradicted-border)] text-[var(--v-contradicted-ink)]',
    highlightClass: 'bg-[var(--v-contradicted-bg)] text-[var(--v-contradicted-ink)]',
  },
  NOT_ESTABLISHED_BY_SOURCE: {
    label: 'Not Established',
    description: 'Missing in sources',
    badgeClass:
      'bg-[var(--v-unestablished-bg)] border-[var(--v-unestablished-border)] text-[var(--v-unestablished-ink)]',
    highlightClass: 'bg-[var(--v-unestablished-bg)] text-[var(--v-unestablished-ink)]',
  },
  AMBIGUOUS_OR_CONFLICTING: {
    label: 'Ambiguous',
    description: 'Conflicting passages',
    badgeClass:
      'bg-[var(--v-ambiguous-bg)] border-[var(--v-ambiguous-border)] text-[var(--v-ambiguous-ink)]',
    highlightClass: 'bg-[var(--v-ambiguous-bg)] text-[var(--v-ambiguous-ink)]',
  },
}

/**
 * Domain fitness evaluation for provided sources against the audit answer.
 */
export type SourceFit = 'relevant' | 'partially_relevant' | 'off_topic' | 'could_not_evaluate'

export interface SourceFitConfig {
  label: string
  description: string
  badgeClass: string
}

export const SOURCE_FIT_CONFIG: Record<SourceFit, SourceFitConfig> = {
  relevant: {
    label: 'Relevant Source',
    description: 'Directly pertinent to claims in the answer',
    badgeClass: 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300',
  },
  partially_relevant: {
    label: 'Partially Relevant',
    description: 'Touches on related topic or tangential evidence',
    badgeClass: 'bg-amber-950/40 border-amber-500/30 text-amber-300',
  },
  off_topic: {
    label: 'Off-Topic Source',
    description: 'Evidence domain does not match the answer',
    badgeClass: 'bg-rose-950/40 border-rose-500/30 text-rose-300',
  },
  could_not_evaluate: {
    label: 'Uncertain Fit',
    description: 'Insufficient context to evaluate domain alignment',
    badgeClass: 'bg-slate-900 border-white/20 text-neutral-400',
  },
}

