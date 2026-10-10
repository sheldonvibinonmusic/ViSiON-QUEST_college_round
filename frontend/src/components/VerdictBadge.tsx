import { CheckCircle2, XCircle, HelpCircle, AlertTriangle } from 'lucide-react'
import type { FactualVerdict } from '../lib/labels'
import { VERDICT_CONFIG } from '../lib/labels'

interface VerdictBadgeProps {
  verdict: FactualVerdict
  showIcon?: boolean
}

export function VerdictBadge({ verdict, showIcon = true }: VerdictBadgeProps) {
  const config = VERDICT_CONFIG[verdict] || VERDICT_CONFIG.NOT_ESTABLISHED_BY_SOURCE

  const getIcon = () => {
    switch (verdict) {
      case 'SUPPORTED_BY_SOURCE':
        return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
      case 'CONTRADICTED_BY_SOURCE':
        return <XCircle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
      case 'NOT_ESTABLISHED_BY_SOURCE':
        return <HelpCircle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
      case 'AMBIGUOUS_OR_CONFLICTING':
        return <AlertTriangle className="w-3.5 h-3.5 text-purple-600 shrink-0" />
      default:
        return null
    }
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${config.badgeClass}`}
      title={config.description}
    >
      {showIcon && getIcon()}
      {config.label}
    </span>
  )
}

export function PriorityBadge({ priority }: { priority: 'low' | 'medium' | 'high' }) {
  const styles = {
    high: 'bg-rose-100 text-rose-800 border-rose-300',
    medium: 'bg-amber-100 text-amber-800 border-amber-300',
    low: 'bg-slate-100 text-slate-700 border-slate-300',
  }

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold tracking-wider uppercase border ${styles[priority]}`}
    >
      {priority} Review
    </span>
  )
}
