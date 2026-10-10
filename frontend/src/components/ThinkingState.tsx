import { useState, useEffect, useRef } from 'react'
import { Check, Loader2 } from 'lucide-react'

// Note: Backend currently runs audit in a single synchronous POST /api/audits.
// The client-side stage progression below estimates stage transitions during the HTTP call.
// In accordance with instructions, this is flagged as:
const MOCK_PIPELINE_TRANSITIONS = true
void MOCK_PIPELINE_TRANSITIONS

const PIPELINE_STAGES = [
  { id: 'ingest', label: 'Ingesting & Validating Source Documents' },
  { id: 'extract', label: 'Extracting Text & Deterministic Chunking' },
  { id: 'claims', label: 'Segmenting Claims & Anchoring Character Offsets' },
  { id: 'retrieve', label: 'BM25 Evidence Indexing & Ranking' },
  { id: 'evaluate', label: 'Evaluating Evidence Support & Contradictions' },
  { id: 'synthesize', label: 'Synthesizing Verdicts & Calibrating Report' },
]

interface ThinkingStateProps {
  failed?: boolean
  errorMessage?: string | null
}

export function ThinkingState({ failed = false, errorMessage }: ThinkingStateProps) {
  const [activeStageIndex, setActiveStageIndex] = useState(0)
  const [elapsedMs, setElapsedMs] = useState(0)
  const startTimeRef = useRef<number>(0)
  const rafRef = useRef<number | null>(null)

  // Subtle Monospace ms Runtime Ticker (Borrowed from Direction 2)
  useEffect(() => {
    startTimeRef.current = Date.now()

    const updateTicker = () => {
      const now = Date.now()
      const diff = now - startTimeRef.current
      setElapsedMs(diff)

      // Advance through pipeline stages over time
      if (!failed) {
        if (diff > 4500) setActiveStageIndex(5)
        else if (diff > 3200) setActiveStageIndex(4)
        else if (diff > 2000) setActiveStageIndex(3)
        else if (diff > 1200) setActiveStageIndex(2)
        else if (diff > 500) setActiveStageIndex(1)
        else setActiveStageIndex(0)
      }

      rafRef.current = requestAnimationFrame(updateTicker)
    }

    rafRef.current = requestAnimationFrame(updateTicker)
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
    }
  }, [failed])

  const progressPercent = failed
    ? Math.min(100, (activeStageIndex / PIPELINE_STAGES.length) * 100)
    : Math.min(95, ((activeStageIndex + 0.6) / PIPELINE_STAGES.length) * 100)

  return (
    <div className="py-8 px-4 max-w-xl mx-auto space-y-8 text-[var(--ink)] animate-fadeIn">
      {/* Ticker & Status Header */}
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <div>
          <span className="text-[11px] font-mono uppercase tracking-widest text-neutral-400">
            Pipeline Execution
          </span>
          <h3 className="text-base font-medium text-white flex items-center gap-2 mt-0.5">
            {!failed ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-neutral-300" />
                Auditing Answer Against Sources
              </>
            ) : (
              <span className="text-rose-400">Pipeline Stage Failed</span>
            )}
          </h3>
        </div>

        {/* Monospace ms Runtime Ticker */}
        <div className="text-right">
          <span className="font-mono text-xs text-neutral-300 bg-white/5 border border-white/10 px-2.5 py-1 rounded-full">
            {elapsedMs} ms
          </span>
        </div>
      </div>

      {/* Minimal Progress Gauge */}
      <div className="space-y-2">
        <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden border border-white/10">
          <div
            className={`h-full transition-all duration-300 ${
              failed ? 'bg-rose-500' : 'bg-gradient-to-r from-neutral-400 via-white to-neutral-300'
            }`}
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        <div className="flex justify-between text-[10px] font-mono text-neutral-500">
          <span>Stage {activeStageIndex + 1} of {PIPELINE_STAGES.length}</span>
          <span>{Math.round(progressPercent)}% Complete</span>
        </div>
      </div>

      {/* Pipeline Stages Stepper with Metallic Shimmer */}
      <div className="space-y-3">
        {PIPELINE_STAGES.map((stage, idx) => {
          const isDone = idx < activeStageIndex && !failed
          const isActive = idx === activeStageIndex && !failed
          const isFailedStage = idx === activeStageIndex && failed

          return (
            <div
              key={stage.id}
              className={`flex items-center gap-3 p-3 rounded-xl border transition-all ${
                isActive
                  ? 'bg-white/10 border-white/30 shadow-md shadow-white/5'
                  : isDone
                  ? 'bg-white/[0.02] border-white/10 text-neutral-400'
                  : isFailedStage
                  ? 'bg-rose-950/40 border-rose-500/40 text-rose-300'
                  : 'bg-transparent border-transparent text-neutral-600'
              }`}
            >
              {/* Status Indicator Icon */}
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 border text-xs font-mono ${
                  isDone
                    ? 'bg-emerald-500/10 border-emerald-400/40 text-emerald-400'
                    : isActive
                    ? 'bg-white border-white text-black font-semibold'
                    : isFailedStage
                    ? 'bg-rose-500/20 border-rose-400 text-rose-300'
                    : 'border-white/10 text-neutral-600'
                }`}
              >
                {isDone ? (
                  <Check className="w-3.5 h-3.5" />
                ) : isActive ? (
                  <span className="w-2 h-2 rounded-full bg-black animate-ping" />
                ) : (
                  <span>{idx + 1}</span>
                )}
              </div>

              {/* Stage Label with Prismatic Shimmer Sweep */}
              <div className="flex-1 min-w-0">
                <p
                  className={`text-xs font-medium truncate ${
                    isActive
                      ? 'text-white font-semibold prismatic-shimmer'
                      : isDone
                      ? 'text-neutral-300'
                      : isFailedStage
                      ? 'text-rose-200'
                      : 'text-neutral-500'
                  }`}
                >
                  {stage.label}
                </p>
              </div>

              {/* Subtle status tag */}
              <div className="text-[10px] font-mono text-neutral-500 shrink-0">
                {isDone ? 'done' : isActive ? 'running...' : isFailedStage ? 'error' : 'queued'}
              </div>
            </div>
          )
        })}
      </div>

      {failed && errorMessage && (
        <div className="p-3 bg-rose-950/40 border border-rose-500/30 rounded-xl text-xs text-rose-300 font-mono">
          {errorMessage}
        </div>
      )}
    </div>
  )
}
