import { BrandMark } from './BrandMark'

interface TopBarProps {
  onOpenAuditor: () => void
  onToggleMenu: () => void
  isMenuOpen: boolean
  hasActiveAudit: boolean
  onResetAudit: () => void
}

export function TopBar({
  onOpenAuditor,
  onToggleMenu,
  isMenuOpen,
  hasActiveAudit,
  onResetAudit,
}: TopBarProps) {
  return (
    <header className="topbar relative z-30 w-full pointer-events-auto">
      {/* Brand Mark: left 75u, top 27u, size 31.5u x 48.5u */}
      <a
        href="#"
        onClick={(e) => {
          e.preventDefault()
          onResetAudit()
        }}
        className="brand anim-rise-brand absolute focus:outline-none focus-visible:ring-2 focus-visible:ring-white/40 rounded"
        style={{
          left: 'calc(75 * var(--u))',
          top: 'calc(27 * var(--u))',
          width: 'calc(31.5 * var(--u))',
          height: 'calc(48.5 * var(--u))',
        }}
        aria-label="Second Opinion Home"
      >
        <BrandMark className="w-full h-full" />
      </a>

      {/* Nav links: centered at 50%, top 51u, transform translate(-50%, -50%) */}
      <nav
        className="links anim-rise-nav absolute hidden md:flex items-center text-[var(--nav)] font-normal select-none"
        style={{
          left: '50%',
          top: 'calc(51 * var(--u))',
          fontSize: 'calc(19 * var(--u))',
        }}
        aria-label="Primary"
      >
        <button
          type="button"
          onClick={onOpenAuditor}
          className="hover:text-white transition-colors cursor-pointer"
          style={{ marginRight: 'calc(24.5 * var(--u))' }}
        >
          Auditor
        </button>
        <button
          type="button"
          onClick={onOpenAuditor}
          className="hover:text-white transition-colors cursor-pointer"
          style={{ marginRight: 'calc(23.5 * var(--u))' }}
        >
          Evidence
        </button>
        <a
          href="#architecture"
          onClick={(e) => {
            e.preventDefault()
            alert('Second Opinion Architecture: 100% Local-first deterministic token-level offsets, BM25 retrieval, and optional DeBERTa NLI cross-examination without external paid APIs.')
          }}
          className="hover:text-white transition-colors cursor-pointer"
          style={{ marginRight: 'calc(26 * var(--u))' }}
        >
          Architecture
        </a>
        <a
          href="#about"
          onClick={(e) => {
            e.preventDefault()
            alert('Second Opinion: Evidence-Grounded AI Answer Auditor built for students, researchers, and engineers verifying AI outputs against ground-truth source documents.')
          }}
          className="hover:text-white transition-colors cursor-pointer"
        >
          About
        </a>
      </nav>

      {/* Header CTA Pill: right 75.4u, top 27u, size 175u x 49u */}
      <button
        type="button"
        onClick={hasActiveAudit ? onResetAudit : onOpenAuditor}
        className="pill pill-nav anim-rise-pill-nav absolute hidden md:flex items-center justify-center font-medium transition-all hover:bg-[#ededed] active:scale-[0.98] cursor-pointer"
        style={{
          right: 'calc(75.4 * var(--u))',
          top: 'calc(27 * var(--u))',
          width: 'calc(175 * var(--u))',
          height: 'calc(49 * var(--u))',
          borderRadius: '999px',
          backgroundColor: 'var(--pill)',
          color: 'var(--pill-ink)',
          fontSize: 'calc(20.6 * var(--u))',
          boxShadow: '0 4px 20px rgba(255, 255, 255, 0.1)',
        }}
      >
        <span style={{ transform: 'translateY(calc(1 * var(--u)))' }}>
          {hasActiveAudit ? 'New Audit' : 'Open Auditor'}
        </span>
      </button>

      {/* Mobile Burger Button */}
      <button
        type="button"
        id="burger"
        className="burger absolute md:hidden flex flex-col justify-center items-center gap-1.5 cursor-pointer z-50 rounded-full border border-white/20 bg-white/5 backdrop-blur-md"
        style={{
          right: 'calc(20 * var(--u))',
          top: 'calc(20 * var(--u))',
          width: 'calc(44 * var(--u))',
          height: 'calc(44 * var(--u))',
        }}
        onClick={onToggleMenu}
        aria-expanded={isMenuOpen}
        aria-label="Toggle navigation menu"
      >
        <i
          className={`block w-5 h-0.5 bg-white transition-transform duration-300 ${
            isMenuOpen ? 'rotate-45 translate-y-2' : ''
          }`}
        />
        <i
          className={`block w-5 h-0.5 bg-white transition-opacity duration-300 ${
            isMenuOpen ? 'opacity-0' : ''
          }`}
        />
        <i
          className={`block w-5 h-0.5 bg-white transition-transform duration-300 ${
            isMenuOpen ? '-rotate-45 -translate-y-2' : ''
          }`}
        />
      </button>
    </header>
  )
}
