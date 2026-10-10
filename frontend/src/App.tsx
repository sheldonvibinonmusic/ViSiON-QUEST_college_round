import { useEffect, useState } from 'react'
import { AlertCircle } from 'lucide-react'
import type { AuditResponse, HealthResponse } from './api/client'
import { fetchHealth, submitAudit } from './api/client'
import { AppHeader } from './components/AppHeader'
import { AuditForm } from './components/AuditForm'
import { AuditSummary } from './components/AuditSummary'
import { OriginalAnswerViewer } from './components/OriginalAnswerViewer'
import { ClaimList } from './components/ClaimList'
import { EvidencePanel } from './components/EvidencePanel'

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [activeAudit, setActiveAudit] = useState<AuditResponse | null>(null)
  const [selectedClaimId, setSelectedClaimId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchHealth()
      .then((data) => setHealth(data))
      .catch((err) => console.warn('Could not reach backend health check:', err.message))
  }, [])

  const handleAuditSubmit = async (
    answer: string,
    sourceText?: string,
    files?: File[]
  ) => {
    setLoading(true)
    setError(null)

    try {
      const response = await submitAudit(answer, sourceText, files)
      setActiveAudit(response)
      if (response.findings.length > 0) {
        setSelectedClaimId(response.findings[0].claim_id)
      }
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('An unexpected error occurred during the audit.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setActiveAudit(null)
    setSelectedClaimId(null)
    setError(null)
  }

  const selectedFinding =
    activeAudit?.findings.find((f) => f.claim_id === selectedClaimId) ||
    activeAudit?.findings[0] ||
    null

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <AppHeader
        onNewAudit={handleReset}
        hasActiveAudit={Boolean(activeAudit)}
        verifierMode={health?.verifier_mode}
      />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-8">
        {error && (
          <div className="mb-6 flex items-start gap-3 p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm shadow-xs">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-bold">Audit Request Error</p>
              <p className="text-xs text-rose-700 mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {!activeAudit ? (
          <div className="max-w-3xl mx-auto">
            <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 sm:p-8">
              <AuditForm onSubmit={handleAuditSubmit} loading={loading} />
            </div>

            {/* Local-first Info Card */}
            <div className="mt-8 p-4 rounded-xl bg-slate-100/70 border border-slate-200 text-xs text-slate-500 space-y-1 text-center">
              <p className="font-semibold text-slate-700">
                100% Local-First & Zero Paid APIs Required
              </p>
              <p>
                Audits are executed in-memory against your provided documents. No databases or
                third-party LLM cloud services are required.
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Aggregate Summary Card */}
            <AuditSummary audit={activeAudit} />

            {/* Original Answer Viewer with Interactive Highlights */}
            <OriginalAnswerViewer
              originalAnswer={activeAudit.original_answer}
              findings={activeAudit.findings}
              selectedClaimId={selectedClaimId}
              onSelectClaim={setSelectedClaimId}
            />

            {/* 2-Column Findings & Evidence Inspector Workspace */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              <div className="lg:col-span-7">
                <ClaimList
                  findings={activeAudit.findings}
                  selectedClaimId={selectedClaimId}
                  onSelectClaim={setSelectedClaimId}
                />
              </div>

              <div className="lg:col-span-5">
                <EvidencePanel finding={selectedFinding} />
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-500">
        Second Opinion — Evidence-Grounded AI Answer Auditor • Built for Hackathon
      </footer>
    </div>
  )
}
