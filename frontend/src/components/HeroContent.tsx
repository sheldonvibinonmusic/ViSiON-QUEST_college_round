import { useEffect, useState } from 'react'
import { HEADLINE_MESSAGES } from '../constants/headlines'

interface HeroContentProps {
  onOpenAuditor: () => void
  onLoadSample: () => void
}

export function HeroContent({ onOpenAuditor, onLoadSample }: HeroContentProps) {
  const [index, setIndex] = useState(0)
  const [phase, setPhase] = useState<'entering' | 'holding' | 'exiting'>('holding')

  useEffect(() => {
    const isReduced =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches

    if (isReduced) {
      const interval = window.setInterval(() => {
        setIndex((prev) => (prev + 1) % HEADLINE_MESSAGES.length)
      }, 4000)
      return () => window.clearInterval(interval)
    }

    const enterTimer = window.setTimeout(() => {
      setPhase('holding')
    }, 60)

    const exitTimer = window.setTimeout(() => {
      setPhase('exiting')
    }, 3100)

    const nextTimer = window.setTimeout(() => {
      setPhase('entering')
      setIndex((prev) => (prev + 1) % HEADLINE_MESSAGES.length)
    }, 3950)

    return () => {
      window.clearTimeout(enterTimer)
      window.clearTimeout(exitTimer)
      window.clearTimeout(nextTimer)
    }
  }, [index])

  return (
    <main className="hero relative pointer-events-none select-none z-20">
      {/* Headline: left 75.5u, top 230.5u */}
      <h1
        className="headline anim-rise-headline absolute text-[var(--ink)] font-normal tracking-[0.3px]"
        aria-live="polite"
        aria-atomic="true"
        style={{
          left: 'calc(75.5 * var(--u))',
          top: 'calc(230.5 * var(--u))',
          maxWidth: 'calc(840 * var(--u))',
          minHeight: 'calc(165 * var(--h))',
          fontSize: 'calc(68 * var(--h))',
          lineHeight: 'calc(78 * var(--h))',
          letterSpacing: 'calc(0.2 * var(--h))',
        }}
      >
        <span className={`headline-cycle-item phase-${phase} block`}>
          {HEADLINE_MESSAGES[index]}
        </span>
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
