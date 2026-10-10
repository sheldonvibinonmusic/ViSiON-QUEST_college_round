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
