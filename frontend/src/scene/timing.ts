/**
 * Authoritative Timing Configuration for Second Opinion Scene Journey.
 *
 * Requirements:
 * - Single source of truth for all scene animations, dwell times, and transitions.
 * - No timing constant may be hard-coded anywhere else in the application.
 * - Tunable centrally from this file.
 */
export const SCENE_TIMING = {
  /** First-load intro: brand mark assembling, words popping in, background moving (shown once per session) */
  INTRO_LOADING: 4500,

  /** Scene 2 START: doorway light slit grows, camera pushes toward door, single soft white flash */
  DOOR_OPEN_AND_FLASH: 3000,

  /** Scene 3A THINKING A: source ingestion, parsing, chunking */
  BEAT_A: 4500,

  /** Scene 3B THINKING B: claim segmentation, candidate BM25 retrieval */
  BEAT_B: 4500,

  /** Scene 3C THINKING C: rules/NLI verification, findings organization */
  BEAT_C: 4500,

  /** Real pipeline stage: checking source domain fitness */
  CHECKING_SOURCE_FIT: 4500,

  /** Real pipeline stage: searching the web for evidence */
  SEARCHING_WEB: 4500,

  /** Scene 4 ARRIVAL: calm space settle before results view handover */
  ARRIVAL: 3000,

  /** Smooth side swap transition duration between graphic focal point and text panel */
  SIDE_SWAP_TRANSITION: 1200,

  /** Stagger delay between graphic start and text panel start during side swap (100-150 ms) */
  SIDE_SWAP_TEXT_DELAY: 120,

  /** Minimum dwell time under prefers-reduced-motion (bypassed) */
  REDUCED_MOTION_DWELL: 0,

  /** Calm crossfade duration under prefers-reduced-motion (under 600 ms) */
  REDUCED_MOTION_CROSSFADE: 500,

  /** Door retreat animation duration upon Cancel */
  CANCEL_RETREAT: 260,
} as const

export type SceneTiming = typeof SCENE_TIMING

/**
 * Returns the configured minimum dwell duration in milliseconds for a given beat or phase.
 */
export function getBeatDwellMs(beat: string, reducedMotion: boolean = false): number {
  if (reducedMotion) {
    return SCENE_TIMING.REDUCED_MOTION_DWELL
  }
  switch (beat) {
    case 'A':
    case 'THINKING_A':
      return SCENE_TIMING.BEAT_A
    case 'B':
    case 'THINKING_B':
      return SCENE_TIMING.BEAT_B
    case 'C':
    case 'THINKING_C':
      return SCENE_TIMING.BEAT_C
    case 'checking_source_fit':
      return SCENE_TIMING.CHECKING_SOURCE_FIT
    case 'searching_web':
      return SCENE_TIMING.SEARCHING_WEB
    case 'door':
    case 'DOOR_OPENING':
      return SCENE_TIMING.DOOR_OPEN_AND_FLASH
    case 'arrival':
    case 'ARRIVAL':
      return SCENE_TIMING.ARRIVAL
    default:
      return SCENE_TIMING.BEAT_A
  }
}
