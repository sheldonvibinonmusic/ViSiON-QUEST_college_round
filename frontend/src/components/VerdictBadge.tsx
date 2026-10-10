import { CheckCircle2, XCircle, HelpCircle, AlertTriangle } from 'lucide-react'
import type { FactualVerdict } from '../lib/labels'
import { VERDICT_CONFIG } from '../lib/labels'

/**
 * Props for rendering a factual verdict badge.
 */
interface VerdictBadgeProps {
  /** The evaluated factual outcome for this finding. */
  verdict: FactualVerdict
  /** Whether to render the visual verdict icon. Defaults to true. */
  showIcon?: boolean
}

/**
 * Renders a color-coded status badge with icon and label for an audit claim verdict.
 */
export function VerdictBadge({ verdict, showIcon = true }: VerdictBadgeProps) {
  const config = VERDICT_CONFIG[verdict] || VERDICT_CONFIG.NOT_ESTABLISHED_BY_SOURCE

  const getIcon = () => {
    switch (verdict) {
      case 'SUPPORTED_BY_SOURCE':
        return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" aria-hidden="true" />
      case 'CONTRADICTED_BY_SOURCE':
        return <XCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" aria-hidden="true" />
      case 'NOT_ESTABLISHED_BY_SOURCE':
        return <HelpCircle className="w-3.5 h-3.5 text-amber-400 shrink-0" aria-hidden="true" />
      case 'AMBIGUOUS_OR_CONFLICTING':
        return <AlertTriangle className="w-3.5 h-3.5 text-sky-400 shrink-0" aria-hidden="true" />
      default:
        return null
    }
  }

  return (
    <span
      role="status"
      aria-label={`${config.label}: ${config.description}`}
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.badgeClass} silver-rim`}
      title={config.description}
    >
      {showIcon && getIcon()}
      {config.label}
    </span>
  )
}

/**
 * Renders an auditor triage priority indicator (low, medium, or high).
 */
export function PriorityBadge({ priority }: { priority: 'low' | 'medium' | 'high' }) {
  const styles = {
    high: 'bg-rose-950/40 text-rose-300 border-rose-500/30',
    medium: 'bg-amber-950/40 text-amber-300 border-amber-500/30',
    low: 'bg-zinc-900 text-zinc-300 border-white/10',
  }

  return (
    <span
      role="status"
      aria-label={`${priority} review priority`}
      className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono tracking-wider uppercase border ${styles[priority]}`}
    >
      {priority} Review
    </span>
  )
}

