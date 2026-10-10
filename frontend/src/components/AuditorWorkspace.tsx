import { useRef, useState } from 'react'
import { X, ShieldCheck, AlertCircle, PlusCircle } from 'lucide-react'
import type { AuditResponse, HealthResponse } from '../api/client'
import { submitAudit } from '../api/client'
import { AuditForm, SAMPLE_ANSWER, SAMPLE_SOURCE } from './AuditForm'
import { AuditSummary } from './AuditSummary'
import { OriginalAnswerViewer } from './OriginalAnswerViewer'
import { ClaimList } from './ClaimList'
import { EvidencePanel } from './EvidencePanel'
import { ThinkingState } from './ThinkingState'
// Scene machine hook (phase 3a): lifecycle and estimated events only; no visuals.
import { sceneMachine } from '../scene/sceneMachine'
import type { SceneMachineState } from '../scene/sceneMachine'
import { getStageEvents } from '../scene/stageEvents'

interface AuditorWorkspaceProps {
  isOpen: boolean
  onClose: () => void
  setSceneOverlayVisible: (visible: boolean) => void
  onSceneStateChange: (state: SceneMachineState) => void
  health: HealthResponse | null
  activeAudit: AuditResponse | null
  setActiveAudit: (audit: AuditResponse | null) => void
  selectedClaimId: string | null
  setSelectedClaimId: (id: string | null) => void
  prefillSample?: boolean
}

export function AuditorWorkspace({
  isOpen,
  onClose,
  setSceneOverlayVisible,
  onSceneStateChange,
  health,
  activeAudit,
  setActiveAudit,
  selectedClaimId,
  setSelectedClaimId,
  prefillSample = false,
}: AuditorWorkspaceProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const stageEventsAbortRef = useRef<AbortController | null>(null)

  if (!isOpen) return null

  const handleAuditSubmit = async (
    answer: string,
    sourceText?: string,
    files?: File[],
    urls?: string[],
    enableWebSearch?: boolean
  ) => {
    stageEventsAbortRef.current?.abort()
    const stageEventsAbort = new AbortController()
    stageEventsAbortRef.current = stageEventsAbort
    sceneMachine.dispatch({ type: 'AUDIT_STARTED' })
    onSceneStateChange(sceneMachine.getState())
    setSceneOverlayVisible(true)

    void (async () => {
      for await (const event of getStageEvents({ signal: stageEventsAbort.signal })) {
        sceneMachine.dispatch({ type: 'STAGE_EVENT', event })
        onSceneStateChange(sceneMachine.getState())
      }
    })()

    setLoading(true)
    setError(null)

    try {
      const response = await submitAudit(answer, sourceText, files, urls, enableWebSearch)
      sceneMachine.dispatch({ type: 'AUDIT_COMPLETED' })
      onSceneStateChange(sceneMachine.getState())
      setActiveAudit(response)
      if (response.findings.length > 0) {
        setSelectedClaimId(response.findings[0].claim_id)
      }
    } catch (err: unknown) {
      sceneMachine.dispatch({ type: 'AUDIT_FAILED' })
      onSceneStateChange(sceneMachine.getState())
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('An unexpected error occurred during the audit.')
      }
    } finally {
      stageEventsAbort.abort()
      if (stageEventsAbortRef.current === stageEventsAbort) {
        stageEventsAbortRef.current = null
      }
      setLoading(false)
      setSceneOverlayVisible(false)
    }
  }

  const handleReset = () => {
    stageEventsAbortRef.current?.abort()
    stageEventsAbortRef.current = null
    setSceneOverlayVisible(false)
    sceneMachine.dispatch({ type: 'RESET_REQUESTED' })
    // Phase 3a has no visuals; later reset motion can delay this completion.
    sceneMachine.dispatch({ type: 'RESET_COMPLETED' })
    setActiveAudit(null)
    setSelectedClaimId(null)
    setError(null)
  }

  const selectedFinding =
    activeAudit?.findings.find((f) => f.claim_id === selectedClaimId) ||
    activeAudit?.findings[0] ||
    null

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center p-3 sm:p-6 bg-black/70 backdrop-blur-md animate-fadeIn">
      <div className="obsidian-glass rounded-2xl w-full max-w-6xl max-h-[90vh] flex flex-col overflow-hidden silver-rim">
        {/* Workspace Top Bar */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-[#0d0d0d]/80 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center text-white border border-white/15">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-semibold text-white tracking-tight">
                  Auditor Workspace
                </h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono uppercase bg-white/5 text-neutral-300 border border-white/10">
                  {health?.verifier_mode || 'Local BM25'}
                </span>
              </div>
              <p className="text-[11px] text-[var(--muted)]">
                Evidence-Grounded AI Answer Verification
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {activeAudit && (
              <button
                type="button"
                onClick={handleReset}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium text-white/90 bg-white/5 hover:bg-white/10 border border-white/15 transition-all cursor-pointer"
              >
                <PlusCircle className="w-3.5 h-3.5" /> New Audit
              </button>
            )}
            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded-full text-neutral-400 hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
              aria-label="Close Auditor Workspace"
              title="Close Workspace (Return to Hero)"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Workspace Inner Scroll Container */}
        <div className="p-6 overflow-y-auto custom-scrollbar flex-1 space-y-6">
          {error && (
            <div className="flex items-start gap-3 p-4 bg-rose-950/40 border border-rose-500/30 rounded-xl text-rose-300 text-xs">
              <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-rose-200">Audit Request Error</p>
                <p className="text-rose-300/80 mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {loading ? (
            <div className="max-w-3xl mx-auto">
              <div className="bg-[#0b0b0b] rounded-2xl border border-white/10 p-6 sm:p-8 silver-rim">
                <ThinkingState failed={Boolean(error)} errorMessage={error} />
              </div>
            </div>
          ) : !activeAudit ? (
            <div className="max-w-3xl mx-auto space-y-6">
              <div className="bg-[#0b0b0b] rounded-2xl border border-white/10 p-6 sm:p-8 silver-rim">
                <AuditForm
                  onSubmit={handleAuditSubmit}
                  loading={loading}
                  initialAnswer={prefillSample ? SAMPLE_ANSWER : ''}
                  initialSource={prefillSample ? SAMPLE_SOURCE : ''}
                />
              </div>

              {/* Local-first Info Banner */}
              <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 text-xs text-neutral-400 space-y-1 text-center font-mono">
                <p className="font-medium text-neutral-200">
                  100% Local-First &bull; Zero External Paid API Dependencies
                </p>
                <p className="text-[11px] text-neutral-500 font-sans">
                  Audits execute in-memory against your supplied sources. Verifications preserve
                  distinct supported, contradicted, insufficient-evidence, and ambiguous verdicts.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Summary */}
              <AuditSummary audit={activeAudit} />

              {/* Highlighted original answer */}
              <OriginalAnswerViewer
                originalAnswer={activeAudit.original_answer}
                findings={activeAudit.findings}
                selectedClaimId={selectedClaimId}
                onSelectClaim={setSelectedClaimId}
              />

              {/* 2-Column Findings & Evidence Inspector */}
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
        </div>
      </div>
    </div>
  )
}
