import { FileText, Bookmark, Hash, AlertCircle } from 'lucide-react'
import type { ClaimFinding } from '../api/client'
import { VerdictBadge } from './VerdictBadge'

interface EvidencePanelProps {
  finding: ClaimFinding | null
}

export function EvidencePanel({ finding }: EvidencePanelProps) {
  if (!finding) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-400 space-y-2">
        <FileText className="w-8 h-8 mx-auto text-slate-300" />
        <p className="text-sm font-medium">Select a claim to inspect its evidence passages.</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-5 sticky top-20">
      {/* Header */}
      <div className="space-y-2 pb-4 border-b border-slate-200">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Evidence Inspector
          </span>
          <VerdictBadge verdict={finding.verdict} />
        </div>
        <p className="text-sm font-bold text-slate-900 leading-snug">
          "{finding.claim_text}"
        </p>
        <p className="text-xs text-slate-600">{finding.explanation}</p>
      </div>

      {/* Evidence Passages */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
            Source Passages ({finding.evidence.length})
          </h4>
          <span className="text-[11px] text-slate-400">Ranked by BM25 match</span>
        </div>

        {finding.evidence.length === 0 ? (
          <div className="p-4 rounded-xl bg-amber-50/60 border border-amber-200 text-amber-900 text-xs flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-bold">No candidate passages found in sources.</p>
              <p className="text-amber-700 mt-0.5">
                The provided sources do not mention the topic of this claim. This claim is unverified, but not automatically false.
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
            {finding.evidence.map((evi, idx) => (
              <div
                key={evi.evidence_id || idx}
                className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/60 space-y-2 text-xs"
              >
                {/* Source Provenance Metadata (§5.1, §9.2) */}
                <div className="flex items-center justify-between text-[11px] text-slate-500 font-medium">
                  <span className="flex items-center gap-1 text-indigo-700 font-semibold truncate max-w-[180px]">
                    <FileText className="w-3 h-3 shrink-0" />
                    {evi.source_name}
                  </span>
                  <div className="flex items-center gap-2 shrink-0">
                    {evi.page_number && (
                      <span className="flex items-center gap-0.5 bg-slate-200/80 px-1.5 py-0.5 rounded text-slate-700 text-[10px]">
                        <Bookmark className="w-2.5 h-2.5" /> Page {evi.page_number}
                      </span>
                    )}
                    <span className="flex items-center gap-0.5 bg-slate-200/80 px-1.5 py-0.5 rounded text-slate-700 text-[10px]">
                      <Hash className="w-2.5 h-2.5" /> Rank {evi.retrieval_rank}
                    </span>
                  </div>
                </div>

                {/* Exact Quote */}
                <blockquote className="p-2.5 bg-white border-l-2 border-indigo-500 rounded text-slate-800 italic leading-relaxed text-[12px]">
                  "{evi.quote.trim()}"
                </blockquote>

                <div className="text-[10px] text-slate-400 flex items-center justify-between">
                  <span>
                    Offsets: [{evi.start_char}..{evi.end_char}]
                  </span>
                  <span className="uppercase font-semibold text-slate-500">
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
