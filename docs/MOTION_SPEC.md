# Second Opinion — Motion Spec

**Status:** Step 1 memory document. The confirmed story and constraints below guide later phases; this file does not authorize replacing existing UI or animations.

## Source of truth and product

Second Opinion audits an AI-written answer against user-provided source documents. It extracts source text, splits sources into chunks, segments the answer into claims, retrieves evidence, assesses claims with deterministic rules and optional local NLI, and returns findings with evidence and a report export.

The project context records the canonical verdicts as `SUPPORTED_BY_SOURCE`, `CONTRADICTED_BY_SOURCE`, `NOT_ESTABLISHED_BY_SOURCE`, and `AMBIGUOUS_OR_CONFLICTING` (`PROJECT_CONTEXT.md`, §20.3, lines 861–864). It records Markdown and JSON export (`PROJECT_CONTEXT.md`, §20.4, lines 866–868). Its implementation addendum identifies the current stack and implementation; the older baseline sections that describe an empty repository are superseded for this work by that addendum and the checked-in source, per the user’s instruction to ignore stale evidence tags and mentions.

## Preservation rule

- **KEEP** the approved Scene 1 page, CloudFront video, poster fallback, two mist planes, pointer parallax, hero, composer/workspace modal, glass surfaces, existing shimmer, and existing loading/results motion.
- Add the scene journey as a full-screen overlay started by the existing Run action. On completion, return to the existing results view. Only small, clearly marked start/finish hooks may be added to existing code.
- Do not rewrite, rename, reformat, delete, or replace existing files, styles, or animations. Do not regenerate `frontend/index.html` or change locked design tokens, typography, video, or stack.
- No existing animation is marked `REPLACE`. Existing animations remain `KEEP`; new scene animation is additive.

## Approved Step 2 decisions

- Door opening: CSS transform on the existing video plate plus separate overlays. Do not choose a transform origin until the actual door has been measured in a video frame.
- Door measurement (phase 3(c)): a decoded frame from the unchanged CloudFront video at 2.51 s, 1664×1248, places the doorway center at approximately 50.0% x / 50.5% y (bounds about 43.5–56.3% x / 30.6–70.4% y). The camera push uses that measured origin. The existing inline poster places its doorway center at 50.0% x / 42.7% y, so the additive transition uses that origin only when the existing poster fallback is mounted.
- Space: Canvas 2D with CSS focal movement for the first version. No WebGL in the first version; optional WebGL is recorded in `IDEAS_FOR_APPROVAL.md` for later review.
- Side swap: one scene state drives `data-side` and CSS variables. Do not use the View Transitions API for the journey.
- Results: keep the viewport-locked page and the existing inner results container as the scroller, with the evidence panel sticky inside it. This approves the architecture only; scroll-linked motion remains a later phase and is not yet approved.
- The future scene overlay has focusable Skip and Cancel controls and does not trap focus. Once the audit is ready, the overlay does not intercept pointer events outside its controls.

## Confirmed story and beats

| Beat | Real pipeline work grouped into the beat | Text side | Graphic focal side | Space visual | Timing rule |
|---|---|---|---|---|---|
| Scene 1 — IDLE | No audit in progress | Existing page | Existing video composition | Existing CloudFront video, mist and pointer parallax | Unchanged; this is the approved baseline |
| Scene 2 — START | Begins on the existing Run action | Neutral activity wording only | Door light / focal point begins near the door | Slit grows; camera push toward the door | Door transition about 700 ms; one smooth white flash with a 700 ms total ramp-up/ramp-down; exactly one flash |
| Scene 3A — THINKING A | Validate request; ingest supplied text/files; parse and chunk sources | RIGHT | LEFT | Fly through doorway into restrained star streaks | Beat is driven by `getStageEvents()`; any timing used by the fallback is explicitly estimated |
| Scene 3B — THINKING B | Segment answer into claims; retrieve candidate evidence with BM25 | LEFT | RIGHT | Pass sparse planet/asteroid silhouettes | Same event/fallback rule; side swap eases for 700–900 ms |
| Scene 3C — THINKING C | Map evidence using deterministic rules and optional NLI; aggregate findings | RIGHT | LEFT | Approach a restrained black hole and accretion disk | Same event/fallback rule; side swap eases for 700–900 ms |
| Scene 4 — ARRIVAL / RESULTS | Audit response and findings are ready | Existing results view | Full-screen space settles behind the transition | Black hole recedes; stars drift slowly | Never delay ready results for scene playback; results remain the existing workspace result view |
| RESET | No pipeline work | Existing form/view | Reverse the focal movement | Journey reverses toward the man and door | New Audit returns through the story in reverse |
| CANCEL / ERROR | Audit is cancelled or request fails | Existing form and error handling | Calmly retreats | Return to Scene 1 | No abrupt flash; error text comes from the existing request error |

### Stage text and event adapter

The current endpoint is one synchronous `POST /api/audits` request; it does not stream stage events. Therefore:

1. The scene reads progress through an adapter named `getStageEvents()`.
2. Until an approved event-stream phase provides actual backend events, the adapter returns a clearly labelled `ESTIMATED_BEATS` source. The on-screen status must say **Estimated activity** and use neutral wording such as “Preparing your sources,” “Comparing claims with sources,” or “Organizing findings.” It must not present these as exact backend stage names or imply measured progress.
3. When real stage events are available, their stage text comes from those events. Do not invent stages or relabel a backend event as a different stage.
4. If the audit completes before a beat sequence finishes, show the existing results immediately. A roughly three-second UX floor may keep the scene moving while a request is still pending; it is never a progress claim and never delays ready results.
5. If the request is still pending after the expected story, hold the current beat with gentle motion. A delay note and cancel control must be truthful and calm.

## State names

The proposed scene-state value is one of:

`IDLE` → `DOOR_OPENING` → `THINKING_A` → `THINKING_B` → `THINKING_C` → `ARRIVAL` → `RESULTS`

Supported exits are `CANCELLED` → `IDLE`, `ERROR` → existing form/error view, and `RESETTING` → `IDLE`. Scene state is separate from backend audit status. A ready audit may jump to `ARRIVAL`/`RESULTS` at any time; visual playback cannot hold the result hostage.

The phase 3(a) state machine also records `skipRequested`, `cancelRequested`, backend request status, and the latest activity event. Skip suppresses scene playback and shows the existing thinking view while a request is pending; once its result is ready, the existing result view appears immediately. Cancel exits the scene journey; the current backend has no server-side cancellation protocol, so this must not be described as stopping backend work until a separate cancellation capability exists.

Phase 3(d) mirrors state-machine events into the additive overlay. The single Canvas 2D star layer keeps drifting during the approved A/B/C side changes; a CSS focal cluster moves opposite the status panel. Its panel includes a silver text sweep, word fades, an estimated-beat rail, elapsed-millisecond ticker, and abstract moving evidence fragments. These are visual cues; they do not imply measured progress or alter the neutral estimated activity labels. Planet, asteroid, black-hole, and accretion-disk visuals remain in Phase 3(e).

For the side swap, one state drives `data-side="left|right"` and CSS variables. Only transforms and opacity animate; space motion continues during swaps. The whole journey uses only the planned A/B/C side layout changes, not repeated decorative swaps.

## Timing, motion, and safety rules

- Preserve the existing video and Scene 1 motion exactly. Door alignment must use a measured video frame before implementation; the fallback poster coordinates are not a substitute.
- Exactly one white flash in Scene 2. It is a smooth ~700 ms ramp up and down, never a strobe. No other scene flashes.
- Side swaps take 700–900 ms, ease as a camera turn, and never pause the space layer.
- Keep the video or space moving behind the panel. Use one full-screen graphic layer and move its focal point, rather than swapping/remounting the graphic.
- Keep panels legible over scenes with a dark scrim and blur. `backdrop-filter: blur(18px)` applies only to panels over video, never stacked. Mobile uses lighter effects and no heavy blur.
- `prefers-reduced-motion`: no camera push, flash, black hole, or side swap. Cross-fade between calm static scenes while stage text continues to update.
- Stage changes are announced through an `aria-live` region. Controls remain keyboard and screen-reader accessible.
- Mobile stacks text above the graphic and does not side-swap.
- High/medium/low quality tiers use automatic selection plus a manual override. Low tier uses a static CSS starfield and simple fades; it uses no WebGL.
- Animate transform and opacity only for the scene; target 60 fps. Cap device-pixel ratio, scale shader resolution if a shader is chosen, pause while the tab is hidden, and use one `requestAnimationFrame` loop.
- Do not alter, compress, replace, or regenerate the existing video. Do not introduce paid assets/APIs or unapproved libraries.

## Scroll architecture gate

The scroll architecture was approved in Step 2: retain the viewport-locked stage and existing inner results scroller with its sticky evidence panel. Scroll-linked motion itself is not yet approved and remains reserved for a later phase. Preserve the current composer/workspace interaction meanwhile.

## Provisional file locations

These are additive locations to evaluate in Step 2; no implementation is authorized by listing them.

- New overlay and scene presentation: `frontend/src/components/SceneOverlay.tsx`.
- New scene state and `getStageEvents()` adapter: `frontend/src/scene/sceneState.ts` and `frontend/src/scene/stageEvents.ts`.
- New scene-only styles: `frontend/src/scene/scene.css`.
- Potential small mount/start/finish hooks, only if needed: `frontend/src/App.tsx` and `frontend/src/components/AuditorWorkspace.tsx`.
- Motion record: `docs/MOTION_SPEC.md`.
- Unapproved proposals: `IDEAS_FOR_APPROVAL.md`.

## Existing motion inventory status

Every existing animation remains **KEEP**: looping video; deep and near mist drift (58 s / 38 s); pointer-driven parallax; hero/nav/logo entrances (0.8–1.1 s, with current delays); active thinking shimmer (2.5 s); thinking spinner, ping and progress rail; claim stagger (0.45 s plus 0.08 s per item); selected-claim sweep (0.8 s); mobile-menu transition (300 ms). The `animate-fadeIn` class has no matching keyframes in the inspected frontend source and must not be represented as verified motion. See the Step 0 inventory for component-level details.

## Future approved phase order

1. Motion memory (this document).
2. Technical approach comparison; no code.
3. Build phases in the user’s prescribed order, stopping after each phase for “next,” with a pre-phase commit or backup, diff summary, and before/after Scene 1 proof.
