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
        <h3 className="text-xs font-mono uppercase tracking-wider text-neutral-300">
          Claim-Level Audit Findings ({findings.length})
        </h3>
        <span className="text-xs text-[var(--muted)]">Select claim to inspect evidence</span>
      </div>

      <div className="space-y-2.5">
        {findings.map((finding, idx) => {
          const isSelected = finding.claim_id === selectedClaimId

          return (
            <div
              key={finding.claim_id}
              onClick={() => onSelectClaim(finding.claim_id)}
              style={{ animationDelay: `${idx * 0.08}s` }}
              className={`p-4 rounded-xl border transition-all cursor-pointer stagger-item ${
                isSelected
                  ? 'bg-white/10 border-white/40 shadow-lg shadow-white/5 ring-1 ring-white/30 claim-active-sweep'
                  : 'bg-[#0a0a0a] border-white/10 hover:border-white/20'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-mono text-neutral-400">#{idx + 1}</span>
                    <VerdictBadge verdict={finding.verdict} />
                    <PriorityBadge priority={finding.review_priority} />
                  </div>

                  <p className="text-sm font-medium text-neutral-100 leading-snug">
                    "{finding.claim_text}"
                  </p>

                  <p className="text-xs text-[var(--muted)] leading-relaxed">
                    {finding.explanation}
                  </p>

                  {/* High-Stakes Advisory Warnings */}
                  {finding.safety_concerns.length > 0 && (
                    <div className="flex items-center gap-1.5 text-[11px] text-amber-300/90 font-medium pt-1">
                      <ShieldAlert className="w-3.5 h-3.5 shrink-0 text-amber-400" />
                      <span>{finding.safety_concerns[0]}</span>
                    </div>
                  )}

                  <div className="flex items-center gap-3 text-[11px] text-neutral-500 pt-1 font-mono flex-wrap">
                    <span className="flex items-center gap-1">
                      <FileSearch className="w-3 h-3 text-neutral-400" />
                      {finding.evidence.length} evidence passage(s) retrieved
                    </span>
                    {Boolean(finding.independent_sources_agreeing && finding.independent_sources_agreeing > 1) && (
                      <span className="flex items-center gap-1 text-emerald-300 bg-emerald-950/40 border border-emerald-500/30 px-1.5 py-0.5 rounded text-[10px]">
                        {finding.independent_sources_agreeing} independent sources agree
                      </span>
                    )}
                  </div>
                </div>

                <ChevronRight
                  className={`w-5 h-5 transition-transform mt-1 ${
                    isSelected ? 'text-white translate-x-0.5' : 'text-neutral-600'
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
