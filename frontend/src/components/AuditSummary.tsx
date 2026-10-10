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
          <div className="flex items-center gap-2.5">
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
    </div>
  )
}
