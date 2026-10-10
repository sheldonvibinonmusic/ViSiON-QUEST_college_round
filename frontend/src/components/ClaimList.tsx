import { ChevronRight, FileSearch, ShieldAlert } from 'lucide-react'
import type { ClaimFinding } from '../api/client'
import { VerdictBadge, PriorityBadge } from './VerdictBadge'

interface ClaimListProps {
  findings: ClaimFinding[]
  selectedClaimId: string | null
  onSelectClaim: (claimId: string) => void
}

export function ClaimList({ findings, selectedClaimId, onSelectClaim }: ClaimListProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
          Claim-by-Claim Audit Findings ({findings.length})
        </h3>
        <span className="text-xs text-slate-400">Select a claim to view source passages</span>
      </div>

      <div className="space-y-2.5">
        {findings.map((finding, idx) => {
          const isSelected = finding.claim_id === selectedClaimId

          return (
            <div
              key={finding.claim_id}
              onClick={() => onSelectClaim(finding.claim_id)}
              className={`p-4 rounded-xl border transition-all cursor-pointer ${
                isSelected
                  ? 'bg-indigo-50/40 border-indigo-400 shadow-xs ring-1 ring-indigo-400'
                  : 'bg-white border-slate-200 hover:border-slate-300 shadow-2xs'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-bold text-slate-500">#{idx + 1}</span>
                    <VerdictBadge verdict={finding.verdict} />
                    <PriorityBadge priority={finding.review_priority} />
                  </div>

                  <p className="text-sm font-semibold text-slate-900 leading-snug">
                    "{finding.claim_text}"
                  </p>

                  <p className="text-xs text-slate-600 leading-relaxed">
                    {finding.explanation}
                  </p>

                  {/* High-Stakes or Logic Warning Tags */}
                  {finding.safety_concerns.length > 0 && (
                    <div className="flex items-center gap-1.5 text-[11px] text-amber-700 font-medium pt-1">
                      <ShieldAlert className="w-3.5 h-3.5 shrink-0" />
                      <span>{finding.safety_concerns[0]}</span>
                    </div>
                  )}

                  <div className="flex items-center gap-3 text-[11px] text-slate-400 pt-1">
                    <span className="flex items-center gap-1">
                      <FileSearch className="w-3 h-3" />
                      {finding.evidence.length} evidence passage(s) retrieved
                    </span>
                  </div>
                </div>

                <ChevronRight
                  className={`w-5 h-5 transition-transform mt-1 ${
                    isSelected ? 'text-indigo-600 translate-x-0.5' : 'text-slate-300'
                  }`}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
