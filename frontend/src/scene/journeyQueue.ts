/**
 * Minimum Dwell Queue and Journey Coordinator.
 *
 * Implements:
 * - Minimum dwell enforcement per beat (stays on screen for at least its configured minimum).
 * - Preservation of scene journey across sub-second audits (eliminates the 22ms race condition).
 * - Holding state on the final beat if the backend is slower than the estimated beats.
 * - Immediate Skip bypass (results are never held hostage).
 * - Instant Cancel retreat and abort handling.
 * - Single-flight audit locking (ignores double Run clicks).
 * - Tab visibility tracking (pauses and resumes remaining dwell).
 * - Bypassed dwell under prefers-reduced-motion.
 */
import { getBeatDwellMs } from './timing'
import { ESTIMATED_BEATS } from './stageEvents'
import type { BeatId } from './stageEvents'
import { sceneMachine as globalSceneMachine } from './sceneMachine'
import type { SceneMachine, SceneMachineState } from './sceneMachine'

export interface StageQueueItem {
  beat: string
  activity: string
  source: 'ESTIMATED_BEATS' | 'BACKEND'
  minDwellMs?: number
}

export interface JourneyCoordinatorOptions<TResult> {
  auditPromise: Promise<TResult>
  customEvents?: StageQueueItem[]
  isReducedMotion?: boolean
  sceneMachine?: SceneMachine
  onStateChange: (state: SceneMachineState) => void
  onOverlayVisibilityChange: (visible: boolean) => void
  onSuccess: (result: TResult) => void
  onError: (error: Error) => void
}

let activeJourneySingleton: JourneyCoordinator<unknown> | null = null

export class JourneyCoordinator<TResult> {
  private active = false
  private isAuditResolved = false
  private resolvedResult: TResult | null = null
  private isAuditFailed = false
  private auditError: Error | null = null
  private isCancelled = false
  private isSkipped = false

  private currentTimerId: ReturnType<typeof setTimeout> | null = null
  private currentDwellResolve: (() => void) | null = null
  private currentDwellStartedAt = 0
  private currentDwellDuration = 0
  private auditWaitResolve: (() => void) | null = null

  private visibilityListener: (() => void) | null = null
  private machineUnsubscribe: (() => void) | null = null

  private machine: SceneMachine
  private options: JourneyCoordinatorOptions<TResult>

  constructor(options: JourneyCoordinatorOptions<TResult>) {
    this.options = options
    this.machine = options.sceneMachine ?? globalSceneMachine
  }

  public getError(): Error | null {
    return this.auditError
  }

  public isActive(): boolean {
    return this.active
  }

  public static isAnyActive(): boolean {
    return activeJourneySingleton !== null && activeJourneySingleton.isActive()
  }

  public start(): boolean {
    // Single-flight guard: ignore double Run clicks
    if (this.active || JourneyCoordinator.isAnyActive()) {
      return false
    }

    this.active = true
    activeJourneySingleton = this as unknown as JourneyCoordinator<unknown>

    // 1. Initialize scene state to DOOR_OPENING and show overlay
    this.machine.dispatch({ type: 'AUDIT_STARTED' })
    this.options.onStateChange(this.machine.getState())
    this.options.onOverlayVisibilityChange(true)

    // 2. Attach visibility change tracking
    if (typeof document !== 'undefined') {
      this.visibilityListener = () => this.handleVisibilityChange()
      document.addEventListener('visibilitychange', this.visibilityListener)
    }

    // 3. Listen to external skip/cancel actions dispatched to the state machine
    this.machineUnsubscribe = this.machine.subscribe(() => {
      const state = this.machine.getState()
      if (state.skipRequested && !this.isSkipped) {
        this.skip()
      } else if (state.cancelRequested && !this.isCancelled) {
        this.cancel()
      }
    })

    // 4. Track background audit promise execution without terminating the journey
    this.options.auditPromise
      .then((res) => {
        this.resolvedResult = res
        this.isAuditResolved = true
        if (this.auditWaitResolve) {
          const resolve = this.auditWaitResolve
          this.auditWaitResolve = null
          resolve()
        }
        if (this.isSkipped) {
          this.completeToResults()
        }
      })
      .catch((err: unknown) => {
        const error = err instanceof Error ? err : new Error(String(err))
        this.auditError = error
        this.isAuditFailed = true
        this.fail(error)
      })

    // 5. Run the asynchronous dwell sequence
    void this.executeJourneyFlow()
    return true
  }

  private async executeJourneyFlow(): Promise<void> {
    const isReduced = Boolean(this.options.isReducedMotion)

    // Step A: Door Opening minimum dwell
    const doorDwell = getBeatDwellMs('door', isReduced)
    await this.waitDwell(doorDwell)
    if (this.isExited()) return

    // Step B: Build and process the queue of thinking journey beats
    const queue: StageQueueItem[] = this.options.customEvents
      ? [...this.options.customEvents]
      : ESTIMATED_BEATS.map((b) => ({
          beat: b.beat,
          activity: b.activity,
          source: 'ESTIMATED_BEATS' as const,
          minDwellMs: getBeatDwellMs(b.beat, isReduced),
        }))

    while (queue.length > 0) {
      if (this.isExited()) return
      const currentBeat = queue.shift()!

      // Dispatch stage event to state machine
      this.machine.dispatch({
        type: 'STAGE_EVENT',
        event: {
          beat: currentBeat.beat as BeatId,
          activity: currentBeat.activity,
          source: currentBeat.source,
        },
      })
      this.options.onStateChange(this.machine.getState())

      // Dwell for at least the configured minimum time
      const dwellMs = currentBeat.minDwellMs ?? getBeatDwellMs(currentBeat.beat, isReduced)
      await this.waitDwell(dwellMs)
      if (this.isExited()) return
    }

    // Step C: Ensure audit has completed before advancing to arrival
    if (!this.isAuditResolved && !this.isExited()) {
      // Hold on the final beat with gentle motion until the audit response arrives
      await new Promise<void>((resolve) => {
        this.auditWaitResolve = resolve
      })
      if (this.isExited()) return
    }

    // Step D: Arrival calm space settle
    this.machine.dispatch({ type: 'AUDIT_COMPLETED' })
    this.options.onStateChange(this.machine.getState())

    const arrivalDwell = getBeatDwellMs('arrival', isReduced)
    await this.waitDwell(arrivalDwell)
    if (this.isExited()) return

    // Step E: Handover to results
    this.completeToResults()
  }

  private waitDwell(durationMs: number): Promise<void> {
    if (durationMs <= 0 || this.isExited()) {
      return Promise.resolve()
    }

    return new Promise((resolve) => {
      this.currentDwellResolve = resolve
      this.currentDwellStartedAt = typeof performance !== 'undefined' ? performance.now() : Date.now()
      this.currentDwellDuration = durationMs

      this.currentTimerId = setTimeout(() => {
        this.currentTimerId = null
        this.currentDwellResolve = null
        resolve()
      }, durationMs)
    })
  }

  private handleVisibilityChange(): void {
    if (typeof document === 'undefined' || !this.currentTimerId || !this.currentDwellResolve) {
      return
    }

    const now = typeof performance !== 'undefined' ? performance.now() : Date.now()
    if (document.hidden) {
      // Pause remaining dwell
      clearTimeout(this.currentTimerId)
      this.currentTimerId = null
      const elapsed = now - this.currentDwellStartedAt
      this.currentDwellDuration = Math.max(0, this.currentDwellDuration - elapsed)
    } else {
      // Resume remaining dwell
      this.currentDwellStartedAt = now
      const remaining = Math.max(0, this.currentDwellDuration)
      this.currentTimerId = setTimeout(() => {
        this.currentTimerId = null
        const resolve = this.currentDwellResolve
        this.currentDwellResolve = null
        resolve?.()
      }, remaining)
    }
  }

  public skip(): void {
    if (this.isCancelled) return
    this.isSkipped = true
    this.clearCurrentDwell()

    this.machine.dispatch({ type: 'SKIP_REQUESTED' })
    this.options.onStateChange(this.machine.getState())

    if (this.isAuditResolved && this.resolvedResult !== null) {
      // Result is already ready; jump straight to results
      this.completeToResults()
    } else {
      // Result still pending: hide the overlay immediately so results are never held hostage
      this.options.onOverlayVisibilityChange(false)
    }
  }

  public cancel(): void {
    this.isCancelled = true
    this.clearAllTimers()

    this.machine.dispatch({ type: 'CANCEL_REQUESTED' })
    this.machine.dispatch({ type: 'SCENE_RETURNED_TO_IDLE' })
    this.options.onStateChange(this.machine.getState())
    this.options.onOverlayVisibilityChange(false)

    this.cleanup()
  }

  private fail(error: Error): void {
    this.clearAllTimers()

    this.machine.dispatch({ type: 'AUDIT_FAILED' })
    this.options.onStateChange(this.machine.getState())
    this.options.onOverlayVisibilityChange(false)
    this.options.onError(error)

    this.cleanup()
  }

  private completeToResults(): void {
    if (this.isCancelled) return
    this.clearAllTimers()

    this.machine.dispatch({ type: 'AUDIT_COMPLETED' })
    this.machine.dispatch({ type: 'ARRIVAL_FINISHED' })
    this.options.onStateChange(this.machine.getState())
    this.options.onOverlayVisibilityChange(false)

    if (this.resolvedResult !== null) {
      this.options.onSuccess(this.resolvedResult)
    }

    this.cleanup()
  }

  public dispose(): void {
    this.clearAllTimers()
    this.cleanup()
  }

  private isExited(): boolean {
    return this.isCancelled || this.isSkipped || this.isAuditFailed || !this.active
  }

  private clearCurrentDwell(): void {
    if (this.currentTimerId) {
      clearTimeout(this.currentTimerId)
      this.currentTimerId = null
    }
    if (this.currentDwellResolve) {
      const resolve = this.currentDwellResolve
      this.currentDwellResolve = null
      resolve()
    }
  }

  private clearAllTimers(): void {
    if (this.currentTimerId) {
      clearTimeout(this.currentTimerId)
      this.currentTimerId = null
    }
    this.currentDwellResolve = null
    this.auditWaitResolve = null
  }

  private cleanup(): void {
    this.active = false
    if (activeJourneySingleton === this as unknown as JourneyCoordinator<unknown>) {
      activeJourneySingleton = null
    }
    if (this.visibilityListener && typeof document !== 'undefined') {
      document.removeEventListener('visibilitychange', this.visibilityListener)
      this.visibilityListener = null
    }
    if (this.machineUnsubscribe) {
      this.machineUnsubscribe()
      this.machineUnsubscribe = null
    }
  }
}
