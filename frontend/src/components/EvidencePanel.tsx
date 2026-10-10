import { FileText, Bookmark, Hash, AlertCircle } from 'lucide-react'
import type { ClaimFinding } from '../api/client'
import { VerdictBadge } from './VerdictBadge'

interface EvidencePanelProps {
  finding: ClaimFinding | null
}

export function EvidencePanel({ finding }: EvidencePanelProps) {
  if (!finding) {
    return (
      <div className="bg-[#0e0e0e] rounded-2xl border border-white/10 p-8 text-center text-neutral-400 space-y-2 silver-rim">
        <FileText className="w-8 h-8 mx-auto text-neutral-600" />
        <p className="text-sm font-medium">Select a claim to inspect its evidence passages.</p>
      </div>
    )
  }

  return (
    <div className="bg-[#0e0e0e] rounded-2xl border border-white/10 p-6 space-y-5 sticky top-6 silver-rim">
      {/* Header */}
      <div className="space-y-2 pb-4 border-b border-white/10">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono uppercase tracking-wider text-neutral-400">
            Evidence Inspector
          </span>
          <VerdictBadge verdict={finding.verdict} />
        </div>
        <p className="text-sm font-medium text-white leading-snug">
          "{finding.claim_text}"
        </p>
        <p className="text-xs text-[var(--muted)]">{finding.explanation}</p>
      </div>

      {/* Evidence Passages */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-mono uppercase tracking-wider text-neutral-300">
            Source Passages ({finding.evidence.length})
          </h4>
          <span className="text-[11px] font-mono text-neutral-500">BM25 Retrieval</span>
        </div>

        {finding.evidence.length === 0 ? (
          <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-500/30 text-amber-200 text-xs flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-amber-200">No candidate passages found in sources.</p>
              <p className="text-amber-300/80 mt-0.5">
                The provided sources do not mention the topic of this claim. This claim is unverified, but not automatically false.
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-3 max-h-[460px] overflow-y-auto pr-1 custom-scrollbar">
            {finding.evidence.map((evi, idx) => (
              <div
                key={evi.evidence_id || idx}
                className="p-3.5 rounded-xl border border-white/10 bg-[#080808] space-y-2 text-xs"
              >
                {/* Source Provenance Metadata (§5.1, §9.2) */}
                <div className="flex items-center justify-between text-[11px] text-neutral-400 font-mono">
                  <span className="flex items-center gap-1 text-white font-medium truncate max-w-[180px]">
                    <FileText className="w-3 h-3 shrink-0 text-neutral-400" />
                    {evi.source_name}
                  </span>
                  <div className="flex items-center gap-2 shrink-0">
                    {evi.page_number && (
                      <span className="flex items-center gap-0.5 bg-white/10 px-1.5 py-0.5 rounded text-neutral-200 text-[10px]">
                        <Bookmark className="w-2.5 h-2.5" /> Page {evi.page_number}
                      </span>
                    )}
                    <span className="flex items-center gap-0.5 bg-white/10 px-1.5 py-0.5 rounded text-neutral-200 text-[10px]">
                      <Hash className="w-2.5 h-2.5" /> Rank {evi.retrieval_rank}
                    </span>
                  </div>
                </div>

                {/* Exact Quote */}
                <blockquote className="p-2.5 bg-white/[0.03] border-l-2 border-white/40 rounded text-neutral-200 italic leading-relaxed text-[12px]">
                  "{evi.quote.trim()}"
                </blockquote>

                <div className="text-[10px] font-mono text-neutral-500 flex items-center justify-between">
                  <span>
                    Offsets: [{evi.start_char}..{evi.end_char}]
                  </span>
                  <span className="uppercase text-neutral-400 font-medium">
                    Relation: {evi.relation}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
