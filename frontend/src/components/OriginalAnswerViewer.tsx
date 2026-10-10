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
    <div className="bg-[#0e0e0e] rounded-2xl border border-white/10 p-6 space-y-3 silver-rim">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-mono uppercase tracking-wider text-neutral-300">
          Original Answer Text &amp; Evidence Spans
        </h3>
        <span className="text-xs text-[var(--muted)]">Click highlighted claim to inspect source</span>
      </div>

      <div className="p-4 rounded-xl bg-[#080808] border border-white/10 text-sm leading-relaxed text-neutral-200 font-sans select-text">
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
              className={`cursor-pointer transition-all rounded px-1.5 py-0.5 font-medium ${config.highlightClass} ${
                isSelected ? 'ring-1 ring-white/70 ring-offset-1 ring-offset-black font-semibold claim-active-sweep' : ''
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
