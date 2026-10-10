import { useEffect, useState, useRef } from 'react'
import type { AuditResponse, HealthResponse } from './api/client'
import { fetchHealth } from './api/client'
import { VideoPlate } from './components/VideoPlate'
import { MistLayer } from './components/MistLayer'
import { TopBar } from './components/TopBar'
import { HeroContent } from './components/HeroContent'
import { PartnerLogos } from './components/PartnerLogos'
import { MobileMenu } from './components/MobileMenu'
import { AuditorWorkspace } from './components/AuditorWorkspace'

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [activeAudit, setActiveAudit] = useState<AuditResponse | null>(null)
  const [selectedClaimId, setSelectedClaimId] = useState<string | null>(null)
  const [isWorkspaceOpen, setIsWorkspaceOpen] = useState(() => {
    return typeof window !== 'undefined' && (window.location.hash === '#workspace' || window.location.search.includes('workspace=true'))
  })
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [prefillSample, setPrefillSample] = useState(false)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const rafRef = useRef<number | null>(null)

  useEffect(() => {
    fetchHealth()
      .then((data) => setHealth(data))
      .catch((err) => console.warn('Could not reach backend health check:', err.message))
  }, [])

  // Keyboard navigation: Escape key closes modal/menu
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (isMenuOpen) setIsMenuOpen(false)
        if (isWorkspaceOpen) setIsWorkspaceOpen(false)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isMenuOpen, isWorkspaceOpen])

  // Cursor Parallax (Direction 1: GPU transform only, throttled via requestAnimationFrame)
  useEffect(() => {
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const isTouch = window.matchMedia('(pointer: coarse)').matches
    if (prefersReduced || isTouch) return

    const handleMouseMove = (e: MouseEvent) => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
      rafRef.current = requestAnimationFrame(() => {
        // Normalized coordinates between -1 and +1
        const nx = (e.clientX / window.innerWidth) * 2 - 1
        const ny = (e.clientY / window.innerHeight) * 2 - 1
        setMousePos({ x: nx, y: ny })
      })
    }

    window.addEventListener('mousemove', handleMouseMove, { passive: true })
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      if (rafRef.current) cancelAnimationFrame(rafRef.current)
    }
  }, [])

  const handleOpenAuditor = () => {
    setPrefillSample(false)
    setIsWorkspaceOpen(true)
    setIsMenuOpen(false)
  }

  const handleLoadSample = () => {
    setPrefillSample(true)
    setIsWorkspaceOpen(true)
    setIsMenuOpen(false)
  }

  const handleResetAudit = () => {
    setActiveAudit(null)
    setSelectedClaimId(null)
    setPrefillSample(false)
    setIsWorkspaceOpen(false)
  }

  return (
    <div className={`stage ${isMenuOpen ? 'is-open' : ''}`}>
      {/* Edge-to-edge looping CloudFront video background with dual fade overlays */}
      <VideoPlate />

      {/* Subtle Dark Scrim for Typography Legibility Over Video */}
      <div className="hero-scrim" aria-hidden="true" />

      {/* Dual-Plane Left-to-Right Prismatic Mist with Cursor Parallax (Direction 1) */}
      <MistLayer mouseX={mousePos.x} mouseY={mousePos.y} />

      {/* Top Header: Brand mark, Nav links, White pill CTA, and Mobile burger */}
      <TopBar
        onOpenAuditor={handleOpenAuditor}
        onToggleMenu={() => setIsMenuOpen((prev) => !prev)}
        isMenuOpen={isMenuOpen}
        hasActiveAudit={Boolean(activeAudit)}
        onResetAudit={handleResetAudit}
      />

      {/* Mobile Menu Overlay */}
      <MobileMenu
        isOpen={isMenuOpen}
        onClose={() => setIsMenuOpen(false)}
        onOpenAuditor={handleOpenAuditor}
      />

      {/* Hero: Headline, Subcopy, Primary White Pill CTA, and Ghost Link */}
      <HeroContent
        onOpenAuditor={handleOpenAuditor}
        onLoadSample={handleLoadSample}
      />

      {/* Bottom Partner Strip: 4 Logoipsum marks */}
      <PartnerLogos />

      {/* Obsidian Frosted Glass Workspace Modal Overlay */}
      <AuditorWorkspace
        isOpen={isWorkspaceOpen}
        onClose={() => setIsWorkspaceOpen(false)}
        health={health}
        activeAudit={activeAudit}
        setActiveAudit={setActiveAudit}
        selectedClaimId={selectedClaimId}
        setSelectedClaimId={setSelectedClaimId}
        prefillSample={prefillSample}
      />
    </div>
  )
}
