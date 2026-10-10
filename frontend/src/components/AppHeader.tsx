import { ShieldCheck, PlusCircle } from 'lucide-react'

interface AppHeaderProps {
  onNewAudit?: () => void
  hasActiveAudit?: boolean
  verifierMode?: string
}

export function AppHeader({ onNewAudit, hasActiveAudit, verifierMode }: AppHeaderProps) {
  return (
    <header className="border-b border-slate-200 bg-white sticky top-0 z-20 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white font-bold text-xl shadow-xs">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-slate-900 tracking-tight">Second Opinion</h1>
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                Auditor
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium">Evidence-Grounded AI Answer Auditor</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              ₹0 Local Core
            </span>
            {verifierMode && (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 font-mono text-[11px]">
                {verifierMode}
              </span>
            )}
          </div>

          {hasActiveAudit && onNewAudit && (
            <button
              type="button"
              onClick={onNewAudit}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-xs transition-all cursor-pointer"
            >
              <PlusCircle className="w-3.5 h-3.5" /> New Audit
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
