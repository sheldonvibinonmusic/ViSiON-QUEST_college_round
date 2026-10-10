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
      // Fallback: simple copy
      navigator.clipboard.writeText(JSON.stringify(audit, null, 2))
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const isSevere = summary.contradicted_claims > 0
  const isClean = summary.contradicted_claims === 0 && summary.not_established_claims === 0

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-900">{summary.assessment}</h2>
            {isSevere ? (
              <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-100 text-rose-800 border border-rose-300">
                ACTION REQUIRED
              </span>
            ) : isClean ? (
              <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                VERIFIED
              </span>
            ) : null}
          </div>
          <p className="text-sm text-slate-600 mt-1 max-w-2xl">{summary.review_recommendation}</p>
        </div>

        {/* Export Buttons */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={handleCopyMarkdown}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition-colors cursor-pointer"
            title="Copy Markdown report to clipboard"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-600" /> Copied!
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5 text-slate-500" /> Copy Markdown
              </>
            )}
          </button>

          <button
            type="button"
            onClick={() => downloadMarkdownReport(audit)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition-colors cursor-pointer"
            title="Download formatted Markdown report file"
          >
            <Download className="w-3.5 h-3.5 text-slate-500" /> Download .md
          </button>

          <button
            type="button"
            onClick={() => downloadJsonReport(audit)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 transition-colors cursor-pointer"
            title="Download full JSON audit report"
          >
            <FileCode className="w-3.5 h-3.5 text-indigo-600" /> Download JSON
          </button>
        </div>
      </div>

      {/* Transparent Claim Counts Grid (§3.2, §9.8) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-lg bg-emerald-50 border border-emerald-200">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-700">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" /> Supported
          </div>
          <div className="text-2xl font-bold text-emerald-900 mt-1">
            {summary.supported_claims}
          </div>
          <div className="text-[11px] text-emerald-700/80 mt-0.5">Claims verified</div>
        </div>

        <div className="p-3.5 rounded-lg bg-rose-50 border border-rose-200">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-rose-700">
            <XCircle className="w-4 h-4 text-rose-600 shrink-0" /> Contradicted
          </div>
          <div className="text-2xl font-bold text-rose-900 mt-1">
            {summary.contradicted_claims}
          </div>
          <div className="text-[11px] text-rose-700/80 mt-0.5">Direct conflicts</div>
        </div>

        <div className="p-3.5 rounded-lg bg-amber-50 border border-amber-200">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-amber-700">
            <HelpCircle className="w-4 h-4 text-amber-600 shrink-0" /> Not Established
          </div>
          <div className="text-2xl font-bold text-amber-900 mt-1">
            {summary.not_established_claims}
          </div>
          <div className="text-[11px] text-amber-700/80 mt-0.5">Missing in sources</div>
        </div>

        <div className="p-3.5 rounded-lg bg-purple-50 border border-purple-200">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-purple-700">
            <AlertTriangle className="w-4 h-4 text-purple-600 shrink-0" /> Ambiguous
          </div>
          <div className="text-2xl font-bold text-purple-900 mt-1">
            {summary.ambiguous_claims}
          </div>
          <div className="text-[11px] text-purple-700/80 mt-0.5">Conflicting passages</div>
        </div>
      </div>

      {summary.safety_concerns_count > 0 && (
        <div className="flex items-start gap-2.5 p-3.5 bg-amber-50/70 border border-amber-200 rounded-xl text-amber-900 text-xs">
          <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">
              {summary.safety_concerns_count} High-Stakes Domain Advisory Flag(s) Raised:
            </span>{' '}
            Answer contains health, legal, or financial assertions. Second Opinion is an auditing
            tool, not certified professional advice.
          </div>
        </div>
      )}
    </div>
  )
}
