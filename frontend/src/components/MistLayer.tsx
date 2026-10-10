interface MistLayerProps {
  mouseX?: number // normalized -1 to +1
  mouseY?: number // normalized -1 to +1
  enabled?: boolean
}

export function MistLayer({ mouseX = 0, mouseY = 0, enabled = true }: MistLayerProps) {
  if (!enabled) return null

  // Parallax offsets: transform-only, zero reflow
  const p1X = mouseX * 16
  const p1Y = mouseY * 10
  const p2X = mouseX * 8
  const p2Y = mouseY * 6

  return (
    <div
      className="mist-layer absolute inset-0 pointer-events-none overflow-hidden select-none z-[8]"
      aria-hidden="true"
    >
      {/* Background Mist Plane 2 (Slower, deeper depth) */}
      <div
        className="mist-plane mist-plane-deep absolute inset-0 will-change-transform"
        style={{
          transform: `translate3d(${p2X}px, ${p2Y}px, 0)`,
        }}
      >
        <div className="mist-cloud mist-drift-slow" />
      </div>

      {/* Foreground Mist Plane 1 (Slightly faster, closer depth) */}
      <div
        className="mist-plane mist-plane-near absolute inset-0 will-change-transform"
        style={{
          transform: `translate3d(${p1X}px, ${p1Y}px, 0)`,
        }}
      >
        <div className="mist-cloud mist-drift-fast" />
      </div>
    </div>
  )
}
