import type { BeatId, StageEvent } from './stageEvents'

export type ScenePhase =
  | 'IDLE'
  | 'DOOR_OPENING'
  | 'THINKING_A'
  | 'THINKING_B'
  | 'THINKING_C'
  | 'ARRIVAL'
  | 'RESULTS'
  | 'SKIPPED'
  | 'CANCELLED'
  | 'RESETTING'
  | 'ERROR'

export type AuditRequestStatus = 'idle' | 'running' | 'succeeded' | 'failed'

export interface SceneMachineState {
  scene: ScenePhase
  audit: AuditRequestStatus
  currentBeat: BeatId | null
  currentActivity: string | null
  activitySource: StageEvent['source'] | null
  skipRequested: boolean
  cancelRequested: boolean
}

export type SceneMachineEvent =
  | { type: 'AUDIT_STARTED' }
  | { type: 'STAGE_EVENT'; event: StageEvent }
  | { type: 'AUDIT_COMPLETED' }
  | { type: 'AUDIT_FAILED' }
  | { type: 'ARRIVAL_FINISHED' }
  | { type: 'SKIP_REQUESTED' }
  | { type: 'CANCEL_REQUESTED' }
  | { type: 'SCENE_RETURNED_TO_IDLE' }
  | { type: 'RESET_REQUESTED' }
  | { type: 'RESET_COMPLETED' }
  | { type: 'RESET' }

export const INITIAL_SCENE_STATE: SceneMachineState = {
  scene: 'IDLE',
  audit: 'idle',
  currentBeat: null,
  currentActivity: null,
  activitySource: null,
  skipRequested: false,
  cancelRequested: false,
}

const BEAT_PHASE: Record<BeatId, ScenePhase> = {
  A: 'THINKING_A',
  B: 'THINKING_B',
  C: 'THINKING_C',
}

export function reduceSceneState(
  state: SceneMachineState,
  event: SceneMachineEvent,
): SceneMachineState {
  switch (event.type) {
    case 'AUDIT_STARTED':
      return {
        ...INITIAL_SCENE_STATE,
        scene: 'DOOR_OPENING',
        audit: 'running',
      }

    case 'STAGE_EVENT':
      if (state.audit !== 'running' || state.skipRequested || state.cancelRequested) {
        return state
      }
      return {
        ...state,
        scene: BEAT_PHASE[event.event.beat],
        currentBeat: event.event.beat,
        currentActivity: event.event.activity,
        activitySource: event.event.source,
      }

    case 'AUDIT_COMPLETED':
      return {
        ...state,
        audit: 'succeeded',
        scene: state.cancelRequested
          ? 'IDLE'
          : state.skipRequested
            ? 'RESULTS'
            : 'ARRIVAL',
      }

    case 'AUDIT_FAILED':
      return {
        ...state,
        audit: 'failed',
        scene: state.cancelRequested ? 'IDLE' : 'ERROR',
      }

    case 'ARRIVAL_FINISHED':
      return state.audit === 'succeeded' && !state.cancelRequested
        ? { ...state, scene: 'RESULTS' }
        : state

    case 'SKIP_REQUESTED':
      return {
        ...state,
        scene: state.audit === 'succeeded' ? 'RESULTS' : 'SKIPPED',
        skipRequested: true,
      }

    case 'CANCEL_REQUESTED':
      return {
        ...state,
        scene: 'CANCELLED',
        cancelRequested: true,
      }

    case 'SCENE_RETURNED_TO_IDLE':
      return state.scene === 'CANCELLED' ? { ...state, scene: 'IDLE' } : state

    case 'RESET_REQUESTED':
      return {
        ...INITIAL_SCENE_STATE,
        scene: 'RESETTING',
      }

    case 'RESET_COMPLETED':
      return state.scene === 'RESETTING' ? INITIAL_SCENE_STATE : state

    case 'RESET':
      return INITIAL_SCENE_STATE
  }
}

export interface SceneMachine {
  dispatch: (event: SceneMachineEvent) => void
  getState: () => SceneMachineState
  subscribe: (listener: () => void) => () => void
}

export function createSceneMachine(): SceneMachine {
  let state = INITIAL_SCENE_STATE
  const listeners = new Set<() => void>()

  return {
    dispatch(event) {
      const nextState = reduceSceneState(state, event)
      if (nextState === state) return
      state = nextState
      listeners.forEach((listener) => listener())
    },
    getState() {
      return state
    },
    subscribe(listener) {
      listeners.add(listener)
      return () => listeners.delete(listener)
    },
  }
}

/** Shared state source for the later scene overlay; no visual is mounted here. */
export const sceneMachine = createSceneMachine()
