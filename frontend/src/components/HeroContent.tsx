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
    <main className="hero pointer-events-none select-none z-20">
      {/* Headline */}
      <h1
        className="headline anim-rise-headline text-[var(--ink)] font-normal tracking-[0.3px]"
        aria-live="polite"
        aria-atomic="true"
      >
        <span className={`headline-cycle-item phase-${phase} block`}>
          {HEADLINE_MESSAGES[index]}
        </span>
      </h1>

      {/* Subcopy */}
      <p className="sub anim-rise-sub text-[var(--muted)] font-normal">
        <span className="block whitespace-normal md:whitespace-nowrap">
          An evidence-grounded auditor that verifies AI-generated answers
        </span>
        <span className="block whitespace-normal md:whitespace-nowrap">
          against your textbooks, reports, and source documents.
        </span>
      </p>

      {/* Actions: Primary CTA and Ghost Button */}
      <div className="actions anim-rise-actions pointer-events-auto">
        <button
          type="button"
          onClick={onOpenAuditor}
          className="pill pill-cta flex items-center justify-center font-medium transition-all hover:bg-[#ededed] active:scale-[0.98] cursor-pointer"
        >
          <span>Open Auditor</span>
        </button>

        <button
          type="button"
          onClick={onLoadSample}
          className="ghost flex items-center font-medium transition-opacity hover:opacity-80 active:opacity-60 cursor-pointer"
        >
          Load Sample Policy
        </button>
      </div>
    </main>
  )
}
