import { useEffect, useRef, useState } from 'react'
import type { SceneMachineState } from '../scene/sceneMachine'
import { sceneMachine } from '../scene/sceneMachine'
import { SCENE_TIMING } from '../scene/timing'
import { SpaceField } from './SpaceField'
import { SpacecraftCraft } from './SpacecraftCraft'
import './scene.css'

/** Phase 3(d): additive space journey layer; the approved workspace remains underneath. */
export function SceneOverlay({
  state,
  onSceneStateChange,
  onFinished,
}: {
  state: SceneMachineState
  onSceneStateChange: (state: SceneMachineState) => void
  onFinished: () => void
}) {
  const [isRetreating, setIsRetreating] = useState(false)
  const [isDoorComplete, setIsDoorComplete] = useState(false)
  const [elapsedMs, setElapsedMs] = useState(0)
  const isEstimate = state.activitySource === 'ESTIMATED_BEATS'
  const activity = state.currentActivity ?? 'Starting your audit'
  const activityWords = activity.split(/\s+/)
  const isJourneyActive = state.scene.startsWith('THINKING_') || state.scene === 'ARRIVAL'
  const dataSide = state.currentBeat === 'B' ? 'left' : 'right'
  const finishedRef = useRef(false)
  const onFinishedRef = useRef(onFinished)
  const fallbackTimerRef = useRef<number | null>(null)
  const retreatTimerRef = useRef<number | null>(null)

  useEffect(() => {
    onFinishedRef.current = onFinished
  }, [onFinished])

  useEffect(() => {
    const startedAt = performance.now()
    const ticker = window.setInterval(() => {
      if (!document.hidden) setElapsedMs(Math.floor(performance.now() - startedAt))
    }, 100)
    return () => window.clearInterval(ticker)
  }, [])

  const finishOverlay = () => {
    if (finishedRef.current) return
    finishedRef.current = true
    onFinishedRef.current()
  }

  useEffect(() => {
    const stage = document.querySelector('.stage')
    stage?.classList.add('is-door-opening')
    if (document.querySelector('.plate-video') instanceof HTMLImageElement) {
      stage?.classList.add('is-door-poster')
    }

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const mobileViewport = window.matchMedia('(max-aspect-ratio: 11/10)').matches
    fallbackTimerRef.current = window.setTimeout(
      () => setIsDoorComplete(true),
      reducedMotion || mobileViewport ? SCENE_TIMING.CANCEL_RETREAT : SCENE_TIMING.DOOR_OPEN_AND_FLASH,
    )

    return () => {
      stage?.classList.remove('is-door-opening', 'is-door-poster', 'is-door-retreating')
      if (fallbackTimerRef.current !== null) window.clearTimeout(fallbackTimerRef.current)
      if (retreatTimerRef.current !== null) window.clearTimeout(retreatTimerRef.current)
    }
  }, [])

  const handleSkip = () => {
    sceneMachine.dispatch({ type: 'SKIP_REQUESTED' })
    onSceneStateChange(sceneMachine.getState())
    finishOverlay()
  }

  const handleCancel = () => {
    if (isRetreating) return
    setIsRetreating(true)
    document.querySelector('.stage')?.classList.add('is-door-retreating')
    sceneMachine.dispatch({ type: 'CANCEL_REQUESTED' })
    retreatTimerRef.current = window.setTimeout(() => {
      sceneMachine.dispatch({ type: 'SCENE_RETURNED_TO_IDLE' })
      onSceneStateChange(sceneMachine.getState())
      finishOverlay()
    }, SCENE_TIMING.CANCEL_RETREAT)
  }

  return (
    <div
      className={`scene-door-overlay${isRetreating ? ' is-retreating' : ''}`}
      data-scene={state.scene.toLowerCase()}
      data-side={dataSide}
      data-beat={state.currentBeat?.toLowerCase() ?? 'none'}
      data-journey-active={isJourneyActive}
      data-door-complete={isDoorComplete}
    >
      <div className="scene-space-layer" aria-hidden="true">
        <SpaceField active={isJourneyActive} />
        <div className="scene-space-focal">
          <SpacecraftCraft />
        </div>
        <div className="scene-evidence-fragments">
          <span />
          <span />
          <span />
        </div>
      </div>
      <div className="scene-door-light" aria-hidden="true" />
      <div className="scene-door-flash" aria-hidden="true" />

      <div className="scene-door-status">
        {isJourneyActive && (
          <span className="scene-thinking-heading">
            <span className="scene-thinking-kicker">Evidence Audit In Progress</span>
            <span className="scene-ticker" aria-hidden="true">{elapsedMs} ms</span>
          </span>
        )}
        <span className="scene-activity-label" role="status" aria-live="polite" aria-atomic="true">
          {activityWords.map((word, index) => (
            <span
              className="scene-activity-word"
              key={`${state.currentBeat ?? 'start'}-${index}-${word}`}
              style={{ animationDelay: `${index * 35}ms` }}
            >
              {word}{index < activityWords.length - 1 ? ' ' : ''}
            </span>
          ))}
          <span className="scene-stage-shimmer" aria-hidden="true" />
        </span>
        {isJourneyActive && (
          <div className="scene-beat-rail" aria-hidden="true">
            <span className="scene-beat-track" />
            <span className="scene-beat-node scene-beat-node-a" />
            <span className="scene-beat-node scene-beat-node-b" />
            <span className="scene-beat-node scene-beat-node-c" />
            <span className="scene-beat-pulse" />
          </div>
        )}
        {isEstimate && <span className="scene-door-estimate">Estimated activity</span>}
      </div>

      <div className="scene-door-controls" role="group" aria-label="Audit animation controls">
        <button type="button" onClick={handleSkip} disabled={isRetreating} aria-label="Skip animation">
          Skip
        </button>
        <button
          type="button"
          onClick={handleCancel}
          disabled={isRetreating}
          aria-label="Cancel animation and return to the idle view"
          aria-describedby="scene-cancel-note"
        >
          Cancel
        </button>
        <span id="scene-cancel-note" className="scene-screen-reader-only">
          The audit request may continue after leaving the animation.
        </span>
      </div>
    </div>
  )
}
