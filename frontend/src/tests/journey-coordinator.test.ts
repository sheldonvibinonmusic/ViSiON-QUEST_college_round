import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { JourneyCoordinator } from '../scene/journeyQueue'
import { SCENE_TIMING } from '../scene/timing'
import { createSceneMachine } from '../scene/sceneMachine'
import type { SceneMachineState } from '../scene/sceneMachine'

describe('JourneyCoordinator Logic & Timing', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.clearAllTimers()
  })

  it('audit finishing in 20 ms still shows every beat for its minimum dwell', async () => {
    const states: SceneMachineState[] = []
    let overlayVisible = false
    let successResult: string | null = null

    // Audit resolves in 20 ms
    const auditPromise = new Promise<string>((resolve) => {
      setTimeout(() => resolve('Audit findings ready'), 20)
    })

    const machine = createSceneMachine()
    const coordinator = new JourneyCoordinator<string>({
      auditPromise,
      sceneMachine: machine,
      onStateChange: (s) => states.push(s),
      onOverlayVisibilityChange: (v) => {
        overlayVisible = v
      },
      onSuccess: (res) => {
        successResult = res
      },
      onError: () => {},
    })

    coordinator.start()
    expect(overlayVisible).toBe(true)
    expect(machine.getState().scene).toBe('DOOR_OPENING')

    // At t = 20 ms, audit promise resolves in background, but door still dwells
    await vi.advanceTimersByTimeAsync(20)
    expect(machine.getState().scene).toBe('DOOR_OPENING')
    expect(successResult).toBeNull()

    // Doorway dwells for DOOR_OPEN_AND_FLASH (3000 ms)
    await vi.advanceTimersByTimeAsync(2979)
    expect(machine.getState().scene).toBe('DOOR_OPENING')

    await vi.advanceTimersByTimeAsync(1)
    expect(machine.getState().scene).toBe('THINKING_A')
    expect(machine.getState().currentBeat).toBe('A')

    // Beat A dwells for BEAT_A (4500 ms) -> t = 7500 ms
    await vi.advanceTimersByTimeAsync(4499)
    expect(machine.getState().scene).toBe('THINKING_A')

    await vi.advanceTimersByTimeAsync(1)
    expect(machine.getState().scene).toBe('THINKING_B')
    expect(machine.getState().currentBeat).toBe('B')

    // Beat B dwells for BEAT_B (4500 ms) -> t = 12000 ms
    await vi.advanceTimersByTimeAsync(4500)
    expect(machine.getState().scene).toBe('THINKING_C')
    expect(machine.getState().currentBeat).toBe('C')

    // Beat C dwells for BEAT_C (4500 ms) -> t = 16500 ms
    await vi.advanceTimersByTimeAsync(4500)
    expect(machine.getState().scene).toBe('ARRIVAL')

    // Arrival dwells for ARRIVAL (3000 ms) -> t = 19500 ms
    await vi.advanceTimersByTimeAsync(2999)
    expect(machine.getState().scene).toBe('ARRIVAL')
    expect(successResult).toBeNull()

    await vi.advanceTimersByTimeAsync(1)
    expect(machine.getState().scene).toBe('RESULTS')
    expect(successResult).toBe('Audit findings ready')
    expect(overlayVisible).toBe(false)
  })

  it('a slow audit extends the last beat until completion', async () => {
    let resolveAudit!: (val: string) => void
    const auditPromise = new Promise<string>((resolve) => {
      resolveAudit = resolve
    })

    const machine = createSceneMachine()
    let successResult: string | null = null

    const coordinator = new JourneyCoordinator<string>({
      auditPromise,
      sceneMachine: machine,
      onStateChange: () => {},
      onOverlayVisibilityChange: () => {},
      onSuccess: (res) => {
        successResult = res
      },
      onError: () => {},
    })

    coordinator.start()

    // Advance through Door (3000ms), Beat A (4500ms), Beat B (4500ms), Beat C (4500ms) = 16500ms
    await vi.advanceTimersByTimeAsync(16500)
    expect(machine.getState().scene).toBe('THINKING_C')

    // Advance further 10 seconds: audit is still pending, so it holds on THINKING_C
    await vi.advanceTimersByTimeAsync(10000)
    expect(machine.getState().scene).toBe('THINKING_C')
    expect(successResult).toBeNull()

    // Resolve audit now
    resolveAudit('Delayed audit complete')
    await vi.advanceTimersByTimeAsync(0)

    // Transitions to ARRIVAL
    expect(machine.getState().scene).toBe('ARRIVAL')

    // Advance ARRIVAL (3000ms)
    await vi.advanceTimersByTimeAsync(3000)
    expect(machine.getState().scene).toBe('RESULTS')
    expect(successResult).toBe('Delayed audit complete')
  })

  it('an error mid-journey stops all timers and reports error immediately', async () => {
    let rejectAudit!: (err: Error) => void
    const auditPromise = new Promise<string>((_, reject) => {
      rejectAudit = reject
    })

    const machine = createSceneMachine()
    let reportedError: Error | null = null
    let overlayVisible = false

    const coordinator = new JourneyCoordinator<string>({
      auditPromise,
      sceneMachine: machine,
      onStateChange: () => {},
      onOverlayVisibilityChange: (v) => {
        overlayVisible = v
      },
      onSuccess: () => {},
      onError: (err) => {
        reportedError = err
      },
    })

    coordinator.start()
    expect(overlayVisible).toBe(true)

    // Advance 1000 ms into door opening, then reject
    await vi.advanceTimersByTimeAsync(1000)
    rejectAudit(new Error('Network connection dropped'))
    await vi.advanceTimersByTimeAsync(0)

    expect(reportedError).not.toBeNull()
    expect((reportedError as unknown as Error)?.message).toBe('Network connection dropped')
    expect(machine.getState().scene).toBe('ERROR')
    expect(overlayVisible).toBe(false)

    // Advance timers by 50 seconds: no further beats run
    await vi.advanceTimersByTimeAsync(50000)
    expect(machine.getState().scene).toBe('ERROR')
  })

  it('skip jumps straight to results when audit is already ready', async () => {
    const auditPromise = Promise.resolve('Immediate response')
    const machine = createSceneMachine()
    let successResult: string | null = null
    let overlayVisible = false

    const coordinator = new JourneyCoordinator<string>({
      auditPromise,
      sceneMachine: machine,
      onStateChange: () => {},
      onOverlayVisibilityChange: (v) => {
        overlayVisible = v
      },
      onSuccess: (res) => {
        successResult = res
      },
      onError: () => {},
    })

    coordinator.start()
    await vi.advanceTimersByTimeAsync(500) // in DOOR_OPENING
    expect(machine.getState().scene).toBe('DOOR_OPENING')

    // User presses Skip
    coordinator.skip()
    await vi.advanceTimersByTimeAsync(0)

    expect(machine.getState().scene).toBe('RESULTS')
    expect(successResult).toBe('Immediate response')
    expect(overlayVisible).toBe(false)
  })

  it('cancel stops all timers and returns to IDLE view', async () => {
    const auditPromise = new Promise<string>(() => {}) // hangs
    const machine = createSceneMachine()
    let overlayVisible = false
    let successResult: string | null = null

    const coordinator = new JourneyCoordinator<string>({
      auditPromise,
      sceneMachine: machine,
      onStateChange: () => {},
      onOverlayVisibilityChange: (v) => {
        overlayVisible = v
      },
      onSuccess: (res) => {
        successResult = res
      },
      onError: () => {},
    })

    coordinator.start()
    await vi.advanceTimersByTimeAsync(4000) // in THINKING_A
    expect(machine.getState().scene).toBe('THINKING_A')

    coordinator.cancel()
    expect(machine.getState().scene).toBe('IDLE')
    expect(overlayVisible).toBe(false)

    await vi.advanceTimersByTimeAsync(30000)
    expect(successResult).toBeNull()
  })

  it('unmount clears all timers and prevents callbacks', async () => {
    const auditPromise = new Promise<string>((resolve) => {
      setTimeout(() => resolve('Done'), 5000)
    })

    const machine = createSceneMachine()
    let successCalled = false

    const coordinator = new JourneyCoordinator<string>({
      auditPromise,
      sceneMachine: machine,
      onStateChange: () => {},
      onOverlayVisibilityChange: () => {},
      onSuccess: () => {
        successCalled = true
      },
      onError: () => {},
    })

    coordinator.start()
    coordinator.dispose()

    await vi.advanceTimersByTimeAsync(50000)
    expect(successCalled).toBe(false)
  })

  it('a double Run click is ignored while journey is active', () => {
    const auditPromise = new Promise<string>(() => {})
    const coordinator = new JourneyCoordinator<string>({
      auditPromise,
      onStateChange: () => {},
      onOverlayVisibilityChange: () => {},
      onSuccess: () => {},
      onError: () => {},
    })

    const firstStarted = coordinator.start()
    expect(firstStarted).toBe(true)

    // Second click on same or concurrent instance
    const secondStarted = coordinator.start()
    expect(secondStarted).toBe(false)

    const anotherCoordinator = new JourneyCoordinator<string>({
      auditPromise,
      onStateChange: () => {},
      onOverlayVisibilityChange: () => {},
      onSuccess: () => {},
      onError: () => {},
    })
    const concurrentStarted = anotherCoordinator.start()
    expect(concurrentStarted).toBe(false)

    coordinator.dispose()
  })

  it('prefers-reduced-motion bypasses dwell times directly to results', async () => {
    const auditPromise = Promise.resolve('Quick response')
    const machine = createSceneMachine()
    let successResult: string | null = null

    const coordinator = new JourneyCoordinator<string>({
      auditPromise,
      sceneMachine: machine,
      isReducedMotion: true,
      onStateChange: () => {},
      onOverlayVisibilityChange: () => {},
      onSuccess: (res) => {
        successResult = res
      },
      onError: () => {},
    })

    coordinator.start()
    await vi.advanceTimersByTimeAsync(0)

    expect(machine.getState().scene).toBe('RESULTS')
    expect(successResult).toBe('Quick response')
  })

  it('bursts and out-of-order events are processed in strict order', async () => {
    const auditPromise = Promise.resolve('Burst complete')
    const machine = createSceneMachine()
    const visitedBeats: string[] = []

    const customEvents = [
      { beat: 'B', activity: 'Comparing claims', source: 'BACKEND' as const, minDwellMs: 100 },
      { beat: 'A', activity: 'Preparing sources', source: 'BACKEND' as const, minDwellMs: 100 },
      { beat: 'C', activity: 'Organizing findings', source: 'BACKEND' as const, minDwellMs: 100 },
    ]

    const coordinator = new JourneyCoordinator<string>({
      auditPromise,
      sceneMachine: machine,
      customEvents,
      onStateChange: (s) => {
        if (s.currentBeat && !visitedBeats.includes(s.currentBeat)) {
          visitedBeats.push(s.currentBeat)
        }
      },
      onOverlayVisibilityChange: () => {},
      onSuccess: () => {},
      onError: () => {},
    })

    coordinator.start()
    // Skip door dwell
    await vi.advanceTimersByTimeAsync(SCENE_TIMING.DOOR_OPEN_AND_FLASH)

    // Process event 1 (B)
    await vi.advanceTimersByTimeAsync(100)
    // Process event 2 (A)
    await vi.advanceTimersByTimeAsync(100)
    // Process event 3 (C)
    await vi.advanceTimersByTimeAsync(100)

    expect(visitedBeats).toEqual(['B', 'A', 'C'])
    coordinator.dispose()
  })
})
