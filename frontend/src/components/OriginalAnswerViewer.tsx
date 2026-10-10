import { buildHighlightedSegments } from '../lib/offsets'
import type { ClaimFinding } from '../api/client'
import { VERDICT_CONFIG } from '../lib/labels'

interface OriginalAnswerViewerProps {
  originalAnswer: string
  findings: ClaimFinding[]
  selectedClaimId: string | null
  onSelectClaim: (claimId: string) => void
}

export function OriginalAnswerViewer({
  originalAnswer,
  findings,
  selectedClaimId,
  onSelectClaim,
}: OriginalAnswerViewerProps) {
  const segments = buildHighlightedSegments(originalAnswer, findings)

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
          Original Answer Text & Evidence Highlights
        </h3>
        <span className="text-xs text-slate-400">Click any highlighted span to inspect evidence</span>
      </div>

      <div className="p-4 rounded-xl bg-slate-50/70 border border-slate-200 text-sm leading-relaxed text-slate-800 font-sans select-text">
        {segments.map((seg, idx) => {
          if (!seg.isClaim || !seg.finding) {
            return <span key={idx}>{seg.text}</span>
          }

          const isSelected = seg.finding.claim_id === selectedClaimId
          const config = VERDICT_CONFIG[seg.finding.verdict] || VERDICT_CONFIG.NOT_ESTABLISHED_BY_SOURCE

          return (
            <mark
              key={idx}
              onClick={() => onSelectClaim(seg.finding!.claim_id)}
              className={`cursor-pointer transition-all rounded px-1 py-0.5 font-medium ${config.highlightClass} ${
                isSelected ? 'ring-2 ring-indigo-600 ring-offset-1 font-bold' : ''
              }`}
              title={`[${config.label}] Click to inspect evidence`}
            >
              {seg.text}
            </mark>
          )
        })}
      </div>
    </div>
  )
}
