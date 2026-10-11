export function SpacecraftCraft() {
  return (
    <div
      className="spacecraft-container relative flex items-center justify-center w-full h-full select-none pointer-events-none"
      aria-label="Auditing exploration spacecraft"
      role="img"
    >
      {/* Thruster Particle Glow / Plasma Exhaust Trailing to the Right */}
      <div className="thruster-exhaust absolute right-[-24px] top-1/2 -translate-y-1/2 w-28 h-8 pointer-events-none">
        <div className="exhaust-plume" />
        <div className="exhaust-particles">
          <span className="particle p1" />
          <span className="particle p2" />
          <span className="particle p3" />
        </div>
      </div>

      {/* Sleek Vector Spacecraft heading Leftward */}
      <svg
        viewBox="0 0 160 80"
        className="spacecraft-svg w-52 h-26 filter drop-shadow-[0_0_24px_rgba(56,189,248,0.4)]"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="hullGradient" x1="160" y1="40" x2="0" y2="40" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#0f172a" />
            <stop offset="40%" stopColor="#1e293b" />
            <stop offset="80%" stopColor="#334155" />
            <stop offset="100%" stopColor="#e2e8f0" />
          </linearGradient>
          <linearGradient id="cockpitGlow" x1="50" y1="40" x2="20" y2="40" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#0284c7" />
            <stop offset="100%" stopColor="#38bdf8" />
          </linearGradient>
          <linearGradient id="thrusterGradient" x1="120" y1="40" x2="160" y2="40" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#38bdf8" />
            <stop offset="50%" stopColor="#0ea5e9" stopOpacity="0.85" />
            <stop offset="100%" stopColor="#0284c7" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="wingGradient" x1="130" y1="40" x2="30" y2="40" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#0b1329" />
            <stop offset="60%" stopColor="#1e293b" />
            <stop offset="100%" stopColor="#475569" />
          </linearGradient>
        </defs>

        {/* Wing Upper */}
        <path
          d="M125 18 L75 32 L35 38 L115 15 Z"
          fill="url(#wingGradient)"
          stroke="rgba(255,255,255,0.25)"
          strokeWidth="0.8"
        />
        {/* Wing Upper Highlight Rim */}
        <path d="M125 18 L35 38" stroke="#38bdf8" strokeWidth="1.2" strokeOpacity="0.85" />

        {/* Wing Lower */}
        <path
          d="M125 62 L75 48 L35 42 L115 65 Z"
          fill="url(#wingGradient)"
          stroke="rgba(255,255,255,0.25)"
          strokeWidth="0.8"
        />
        {/* Wing Lower Highlight Rim */}
        <path d="M125 62 L35 42" stroke="#38bdf8" strokeWidth="1.2" strokeOpacity="0.85" />

        {/* Central Fuselage / Command Module heading Left (nose at x=10, y=40) */}
        <path
          d="M10 40 L35 32 L130 31 L142 35 L142 45 L130 49 L35 48 Z"
          fill="url(#hullGradient)"
          stroke="rgba(255,255,255,0.4)"
          strokeWidth="1"
        />

        {/* Cockpit / Sensor Glass visor */}
        <path
          d="M22 40 L38 35 L48 35 L42 40 L48 45 L38 45 Z"
          fill="url(#cockpitGlow)"
          opacity="0.95"
        />

        {/* Longitudinal Hull Spine & Details */}
        <line x1="35" y1="40" x2="135" y2="40" stroke="rgba(255,255,255,0.5)" strokeWidth="1" strokeDasharray="16 4" />
        <line x1="60" y1="35" x2="60" y2="45" stroke="rgba(56,189,248,0.5)" strokeWidth="0.8" />
        <line x1="95" y1="35" x2="95" y2="45" stroke="rgba(56,189,248,0.5)" strokeWidth="0.8" />

        {/* Sensor Node Beacon */}
        <circle cx="14" cy="40" r="2.2" fill="#7dd3fc" />

        {/* Twin Engine Bells (Rear, at x=142) */}
        <rect x="140" y="33" width="6" height="5" rx="1" fill="#475569" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />
        <rect x="140" y="42" width="6" height="5" rx="1" fill="#475569" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" />

        {/* Ion Engine Exhaust Cones */}
        <path d="M146 35.5 L175 32 L175 39 Z" fill="url(#thrusterGradient)" />
        <path d="M146 44.5 L175 41 L175 48 Z" fill="url(#thrusterGradient)" />
      </svg>
    </div>
  )
}
