import { useEffect, useState } from 'react'
import { ShieldCheck, CheckCircle2, AlertTriangle, FileText, Cpu } from 'lucide-react'

interface SystemLimits {
  max_answer_chars: number
  max_source_chars: number
  max_files: number
  max_file_bytes: number
  max_claims: number
}

interface HealthResponse {
  status: string
  version: string
  verifier_mode: string
  model_loaded: boolean
  model_id: string
  supported_file_types: string[]
  limits: SystemLimits
}

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    fetch('/api/health')
      .then((res) => {
        if (!res.ok) throw new Error(`Health check returned HTTP ${res.status}`)
        return res.json()
      })
      .then((data: HealthResponse) => {
        setHealth(data)
        setLoading(false)
      })
      .catch((err: Error) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      {/* Header */}
      <header className="border-b border-slate-200 bg-white sticky top-0 z-10 shadow-xs">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-xl shadow-xs">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-900 tracking-tight">Second Opinion</h1>
              <p className="text-xs text-slate-500 font-medium">Evidence-Grounded AI Answer Auditor</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
              ₹0 Local Core
            </span>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700">
              v0.1.0
            </span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 sm:px-6 py-8">
        <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-6 mb-8">
          <h2 className="text-xl font-bold text-slate-900 mb-2">Backend Connection Status</h2>
          <p className="text-sm text-slate-600 mb-6">
            Initial Phase 1 health check validating local-first communication between React and FastAPI.
          </p>

          {loading && (
            <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 text-slate-600 text-sm animate-pulse">
              Checking backend health at <code className="font-mono text-xs bg-slate-200 px-1 py-0.5 rounded">/api/health</code>...
            </div>
          )}

          {error && (
            <div className="p-4 bg-amber-50 rounded-lg border border-amber-200 text-amber-800 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-sm">Backend Not Reachable</p>
                <p className="text-xs mt-1 text-amber-700">
                  {error}. Ensure the FastAPI server is running on port 8000.
                </p>
              </div>
            </div>
          )}

          {health && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-emerald-50 rounded-lg border border-emerald-200">
                <div className="flex items-center gap-2 text-emerald-700 font-semibold text-sm mb-1">
                  <CheckCircle2 className="w-4 h-4" /> API Status
                </div>
                <div className="text-2xl font-bold text-emerald-900 capitalize">{health.status}</div>
                <div className="text-xs text-emerald-700 mt-1">Backend v{health.version}</div>
              </div>

              <div className="p-4 bg-indigo-50 rounded-lg border border-indigo-200">
                <div className="flex items-center gap-2 text-indigo-700 font-semibold text-sm mb-1">
                  <Cpu className="w-4 h-4" /> Verifier Mode
                </div>
                <div className="text-2xl font-bold text-indigo-900">{health.verifier_mode}</div>
                <div className="text-xs text-indigo-700 mt-1 font-mono">{health.model_id}</div>
              </div>

              <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                <div className="flex items-center gap-2 text-slate-700 font-semibold text-sm mb-1">
                  <FileText className="w-4 h-4" /> Document Ingestion
                </div>
                <div className="text-sm font-semibold text-slate-800 mt-1">
                  {health.supported_file_types.join(', ')}
                </div>
                <div className="text-xs text-slate-500 mt-1">
                  Max {health.limits.max_files} files (up to {Math.round(health.limits.max_file_bytes / (1024 * 1024))}MB each)
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Phase 1 Completion Card */}
        <div className="border border-slate-200 rounded-xl bg-white p-6 shadow-xs">
          <h3 className="text-base font-semibold text-slate-900 mb-2">Phase 1: Environment & Foundation Status</h3>
          <ul className="text-sm text-slate-600 space-y-2">
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span><strong>Python Virtual Environment:</strong> FastAPI, Pydantic v2, pytest, httpx, rank-bm25, pypdf, python-docx</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span><strong>Node.js Toolchain:</strong> Node v24.20.0 LTS + npm 11.19.0 + Vite 6 + React 19 + TypeScript</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span><strong>Root Configuration:</strong> .gitignore, .env.example, pyproject.toml, CHANGELOG.md, IDEAS_FOR_APPROVAL.md</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span><strong>Contracts:</strong> Health response contract verified via automated pytest</span>
            </li>
          </ul>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-500">
        Second Opinion — Local-First AI Answer Auditor • Zero Paid APIs Required
      </footer>
    </div>
  )
}
