import { SCENE_TIMING } from './timing'

/**
 * Temporary scene beat source. The audit API currently returns one completed
 * response and does not emit backend stage events. Keep these labels neutral
 * and expose their estimated source so the UI can identify them honestly.
 */
export const ESTIMATED_BEATS = [
  { beat: 'A', activity: 'Preparing your sources', afterMs: SCENE_TIMING.BEAT_A },
  { beat: 'B', activity: 'Comparing claims with sources', afterMs: SCENE_TIMING.BEAT_B },
  { beat: 'C', activity: 'Organizing findings', afterMs: SCENE_TIMING.BEAT_C },
] as const

export type BeatId = (typeof ESTIMATED_BEATS)[number]['beat']

export interface StageEvent {
  beat: BeatId
  activity: string
  source: 'ESTIMATED_BEATS' | 'BACKEND'
}

export interface GetStageEventsOptions {
  signal?: AbortSignal
}

function waitForDelay(delayMs: number, signal?: AbortSignal): Promise<boolean> {
  return new Promise((resolve) => {
    if (signal?.aborted) {
      resolve(false)
      return
    }

    const finish = (elapsed: boolean) => {
      clearTimeout(timeoutId)
      signal?.removeEventListener('abort', onAbort)
      resolve(elapsed)
    }

    const onAbort = () => finish(false)
    const timeoutId = setTimeout(() => finish(true), delayMs)
    signal?.addEventListener('abort', onAbort, { once: true })

    if (signal?.aborted) onAbort()
  })
}

/**
 * Adapter consumed by the scene state machine. Replace this implementation
 * with a backend event stream in the separately approved SSE/polling phase;
 * callers keep the same async-iterable contract.
 */
export async function* getStageEvents(
  options: GetStageEventsOptions = {},
): AsyncGenerator<StageEvent> {
  const { signal } = options

  for (const beat of ESTIMATED_BEATS) {
    const elapsed = await waitForDelay(beat.afterMs, signal)
    if (!elapsed) return

    yield {
      beat: beat.beat,
      activity: beat.activity,
      source: 'ESTIMATED_BEATS',
    }
  }
}
