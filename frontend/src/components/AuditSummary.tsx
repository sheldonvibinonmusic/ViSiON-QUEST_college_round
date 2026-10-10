import { useState } from 'react'
import {
  CheckCircle2,
  XCircle,
  HelpCircle,
  AlertTriangle,
  Download,
  Copy,
  Check,
  FileCode,
  ShieldAlert,
  Search,
  Globe,
  Info,
} from 'lucide-react'
import type { AuditResponse } from '../api/client'
import { downloadJsonReport, downloadMarkdownReport } from '../api/client'

interface AuditSummaryProps {
  audit: AuditResponse
}

export function AuditSummary({ audit }: AuditSummaryProps) {
  const [copied, setCopied] = useState(false)
  const { summary } = audit

  const handleCopyMarkdown = async () => {
    try {
      const res = await fetch('/api/audits/export/markdown', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(audit),
      })
      if (!res.ok) throw new Error()
      const text = await res.text()
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Fallback
      navigator.clipboard.writeText(JSON.stringify(audit, null, 2))
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const isSevere = summary.contradicted_claims > 0
  const isClean = summary.contradicted_claims === 0 && summary.not_established_claims === 0

  return (
    <div className="bg-[#0e0e0e] rounded-2xl border border-white/10 p-6 space-y-6 text-[var(--ink)] silver-rim">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2.5 flex-wrap">
            <h2 className="text-xl font-medium tracking-tight text-white">{summary.assessment}</h2>
            {isSevere ? (
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono tracking-wider uppercase bg-rose-950/60 text-rose-300 border border-rose-500/40">
                ACTION REQUIRED
              </span>
            ) : isClean ? (
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono tracking-wider uppercase bg-emerald-950/60 text-emerald-300 border border-emerald-500/40">
                VERIFIED
              </span>
            ) : (
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono tracking-wider uppercase bg-zinc-800 text-zinc-300 border border-white/15">
                REVIEW NEEDED
              </span>
            )}

            {/* Source Fit Badge (§4A, UI_HANDOFF_NEEDS #1) */}
            {audit.source_fit && (
              <span
                className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-mono uppercase tracking-wider border silver-rim ${
                  audit.source_fit.overall_fit === 'RELEVANT'
                    ? 'bg-emerald-950/40 text-emerald-300 border-emerald-500/30'
                    : audit.source_fit.overall_fit === 'PARTIALLY_RELEVANT'
                    ? 'bg-amber-950/40 text-amber-300 border-amber-500/30'
                    : 'bg-rose-950/40 text-rose-300 border-rose-500/30'
                }`}
                title={`Average lexical coverage score: ${(audit.source_fit.average_fit_score * 100).toFixed(0)}%`}
              >
                {audit.source_fit.overall_fit === 'RELEVANT' ? (
                  <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
                ) : audit.source_fit.overall_fit === 'PARTIALLY_RELEVANT' ? (
                  <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0" />
                ) : (
                  <XCircle className="w-3 h-3 text-rose-400 shrink-0" />
                )}
                Fit: {audit.source_fit.overall_fit.replace('_', ' ')}
              </span>
            )}
          </div>
          <p className="text-xs text-[var(--muted)] mt-1.5 max-w-2xl leading-relaxed">
            {summary.review_recommendation}
          </p>
        </div>

        {/* Export Buttons */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={handleCopyMarkdown}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium text-neutral-300 bg-white/5 hover:bg-white/10 border border-white/15 transition-all cursor-pointer"
            title="Copy Markdown report to clipboard"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" /> Copied!
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5 text-neutral-400" /> Copy MD
              </>
            )}
          </button>

          <button
            type="button"
            onClick={() => downloadMarkdownReport(audit)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium text-neutral-300 bg-white/5 hover:bg-white/10 border border-white/15 transition-all cursor-pointer"
            title="Download formatted Markdown report file"
          >
            <Download className="w-3.5 h-3.5 text-neutral-400" /> Export .md
          </button>

          <button
            type="button"
            onClick={() => downloadJsonReport(audit)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium text-white bg-white/10 hover:bg-white/20 border border-white/25 transition-all cursor-pointer"
            title="Download full JSON audit report"
          >
            <FileCode className="w-3.5 h-3.5 text-zinc-300" /> Export JSON
          </button>
        </div>
      </div>

      {/* Transparent Claim Counts Grid (§3.2, §9.8) - No purple */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/25">
          <div className="flex items-center gap-1.5 text-xs font-medium text-emerald-400">
            <CheckCircle2 className="w-4 h-4 shrink-0" /> Supported
          </div>
          <div className="text-2xl font-mono font-medium text-emerald-200 mt-1">
            {summary.supported_claims}
          </div>
          <div className="text-[11px] text-emerald-400/80 mt-0.5">Claims verified</div>
        </div>

        <div className="p-3.5 rounded-xl bg-rose-950/20 border border-rose-500/25">
          <div className="flex items-center gap-1.5 text-xs font-medium text-rose-400">
            <XCircle className="w-4 h-4 shrink-0" /> Contradicted
          </div>
          <div className="text-2xl font-mono font-medium text-rose-200 mt-1">
            {summary.contradicted_claims}
          </div>
          <div className="text-[11px] text-rose-400/80 mt-0.5">Direct conflicts</div>
        </div>

        <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/25">
          <div className="flex items-center gap-1.5 text-xs font-medium text-amber-400">
            <HelpCircle className="w-4 h-4 shrink-0" /> Not Established
          </div>
          <div className="text-2xl font-mono font-medium text-amber-200 mt-1">
            {summary.not_established_claims}
          </div>
          <div className="text-[11px] text-amber-400/80 mt-0.5">Missing in sources</div>
        </div>

        <div className="p-3.5 rounded-xl bg-sky-950/20 border border-sky-500/25">
          <div className="flex items-center gap-1.5 text-xs font-medium text-sky-400">
            <AlertTriangle className="w-4 h-4 shrink-0" /> Ambiguous
          </div>
          <div className="text-2xl font-mono font-medium text-sky-200 mt-1">
            {summary.ambiguous_claims}
          </div>
          <div className="text-[11px] text-sky-400/80 mt-0.5">Conflicting passages</div>
        </div>
      </div>

      {/* Domain Mismatch Advisory Banner (UI_HANDOFF_NEEDS #1) */}
      {audit.source_fit?.all_sources_off_topic && (
        <div className="flex items-start gap-2.5 p-3.5 bg-amber-950/40 border border-amber-500/40 rounded-xl text-amber-200 text-xs">
          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-amber-300">Domain Mismatch Detected:</span>{' '}
            The provided sources appear off-topic for this answer ({audit.source_fit.explanation}).
            {audit.source_fit.documents.some((d) => d.missing_topics.length > 0) && (
              <span className="block mt-1 text-amber-200/90 font-mono text-[11px]">
                Missing topics in source: {audit.source_fit.documents.flatMap((d) => d.missing_topics).slice(0, 6).join(', ')}
              </span>
            )}
            <span className="block mt-1 text-amber-300/80">
              Claims not established in the source are reported as unverified, never as false.
            </span>
          </div>
        </div>
      )}

      {/* Safety Concerns Banner */}
      {summary.safety_concerns_count > 0 && (
        <div className="flex items-start gap-2.5 p-3.5 bg-amber-950/30 border border-amber-500/30 rounded-xl text-amber-300 text-xs">
          <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-amber-200">
              {summary.safety_concerns_count} High-Stakes Domain Advisory Flag(s) Raised:
            </span>{' '}
            Answer touches health, legal, or financial assertions. Second Opinion provides
            transparent source comparison, not certified advice.
          </div>
        </div>
      )}

      {/* Web Evidence & Audit Metadata Strip (UI_HANDOFF_NEEDS #4, #6) */}
      {(Boolean(audit.engine_metadata?.web_queries_used) || audit.source_mode.includes('web') || (audit.warnings && audit.warnings.length > 0)) && (
        <div className="p-3 bg-white/[0.02] border border-white/10 rounded-xl space-y-2 text-xs font-mono text-neutral-400">
          <div className="flex items-center justify-between flex-wrap gap-2 text-[11px]">
            <span className="flex items-center gap-1.5 text-neutral-300">
              <Globe className="w-3.5 h-3.5 text-sky-400" />
              Source Mode: <span className="text-white font-medium">{audit.source_mode.replace('_', ' ')}</span>
            </span>
            {audit.engine_metadata?.web_queries_used !== undefined && (
              <span className="flex items-center gap-1.5 text-neutral-300">
                <Search className="w-3.5 h-3.5 text-emerald-400" />
                Web Search Budget:{' '}
                <span className="text-emerald-300 font-medium">
                  {String(audit.engine_metadata.web_queries_used)} query/queries used
                </span>
              </span>
            )}
          </div>

          {/* Warnings & Incomplete Notices */}
          {audit.warnings && audit.warnings.length > 0 && (
            <div className="pt-1.5 border-t border-white/5 space-y-1 text-[11px] text-neutral-400">
              {audit.warnings.map((w, idx) => (
                <div key={idx} className="flex items-start gap-1.5 text-neutral-300">
                  <Info className="w-3 h-3 text-neutral-500 shrink-0 mt-0.5" />
                  <span>{w}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
