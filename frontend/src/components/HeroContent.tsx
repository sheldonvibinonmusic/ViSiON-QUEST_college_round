interface HeroContentProps {
  onOpenAuditor: () => void
  onLoadSample: () => void
}

export function HeroContent({ onOpenAuditor, onLoadSample }: HeroContentProps) {
  return (
    <main className="hero pointer-events-none select-none z-20">
      {/* Headline: left 75.5u, top 230.5u */}
      <h1
        className="headline anim-rise-headline absolute text-[var(--ink)] font-normal tracking-[0.3px]"
        style={{
          left: 'calc(75.5 * var(--u))',
          top: 'calc(230.5 * var(--u))',
          fontSize: 'calc(71.6 * var(--h))',
          lineHeight: 'calc(80.5 * var(--h))',
          letterSpacing: 'calc(0.3 * var(--h))',
        }}
      >
        <span className="block whitespace-nowrap">Where AI meets</span>
        <span className="block whitespace-nowrap">absolute truth.</span>
      </h1>

      {/* Subcopy: left 75.5u, top: 230.5u + 189.0h */}
      <p
        className="sub anim-rise-sub absolute text-[var(--muted)] font-normal"
        style={{
          left: 'calc(75.5 * var(--u))',
          top: 'calc(230.5 * var(--u) + 189 * var(--h))',
          fontSize: 'calc(20.7 * var(--h))',
          lineHeight: 'calc(23.5 * var(--h))',
          wordSpacing: 'calc(1.8 * var(--h))',
        }}
      >
        <span className="block whitespace-nowrap">
          An evidence-grounded auditor that verifies AI-generated answers
        </span>
        <span className="block whitespace-nowrap">
          against your textbooks, reports, and source documents.
        </span>
      </p>

      {/* Actions: Primary CTA and Ghost Button */}
      <div className="actions anim-rise-actions pointer-events-auto">
        {/* Primary CTA: left 74.9u, top: 230.5u + 264.5h, size 175.6h x 50h */}
        <button
          type="button"
          onClick={onOpenAuditor}
          className="pill pill-cta absolute flex items-center justify-center font-medium transition-all hover:bg-[#ededed] active:scale-[0.98] cursor-pointer"
          style={{
            left: 'calc(74.9 * var(--u))',
            top: 'calc(230.5 * var(--u) + 264.5 * var(--h))',
            width: 'calc(175.6 * var(--h))',
            height: 'calc(50 * var(--h))',
            fontSize: 'calc(20.6 * var(--h))',
            borderRadius: '999px',
            backgroundColor: 'var(--pill)',
            color: 'var(--pill-ink)',
            boxShadow: '0 8px 30px rgba(255, 255, 255, 0.12)',
          }}
        >
          <span>Open Auditor</span>
        </button>

        {/* Ghost link: left: 74.9u + 220.6h, top: 230.5u + 279.5h */}
        <button
          type="button"
          onClick={onLoadSample}
          className="ghost absolute flex items-center font-medium transition-opacity hover:opacity-80 active:opacity-60 cursor-pointer text-white"
          style={{
            left: 'calc(74.9 * var(--u) + 220.6 * var(--h))',
            top: 'calc(230.5 * var(--u) + 279.5 * var(--h))',
            fontSize: 'calc(20.6 * var(--h))',
            letterSpacing: 'calc(0.12 * var(--h))',
          }}
        >
          Load Sample Policy
        </button>
      </div>
    </main>
  )
}
