interface MobileMenuProps {
  isOpen: boolean
  onClose: () => void
  onOpenAuditor: () => void
}

export function MobileMenu({ isOpen, onClose, onOpenAuditor }: MobileMenuProps) {
  if (!isOpen) return null

  return (
    <nav
      id="menu"
      className="menu fixed inset-0 z-40 flex flex-col justify-between p-8 bg-[#050505]/95 backdrop-blur-2xl transition-all duration-300 md:hidden"
      aria-label="Mobile Navigation"
    >
      <div className="menu-inner mt-16 space-y-8">
        <p className="menu-eyebrow text-xs uppercase tracking-widest text-[var(--muted)] font-mono">
          Menu
        </p>
        <ul className="menu-list space-y-6 text-2xl font-light text-[var(--ink)]">
          <li>
            <button
              type="button"
              onClick={() => {
                onClose()
                onOpenAuditor()
              }}
              className="flex items-center justify-between w-full hover:text-white transition-colors"
            >
              Auditor <span>&rarr;</span>
            </button>
          </li>
          <li>
            <button
              type="button"
              onClick={() => {
                onClose()
                onOpenAuditor()
              }}
              className="flex items-center justify-between w-full hover:text-white transition-colors"
            >
              Evidence <span>&rarr;</span>
            </button>
          </li>
          <li>
            <a
              href="#architecture"
              onClick={() => onClose()}
              className="flex items-center justify-between w-full hover:text-white transition-colors"
            >
              Architecture <span>&rarr;</span>
            </a>
          </li>
          <li>
            <a
              href="#about"
              onClick={() => onClose()}
              className="flex items-center justify-between w-full hover:text-white transition-colors"
            >
              About <span>&rarr;</span>
            </a>
          </li>
        </ul>
      </div>

      <div className="menu-foot space-y-4 pt-8 border-t border-white/10">
        <button
          type="button"
          onClick={() => {
            onClose()
            onOpenAuditor()
          }}
          className="w-full py-3.5 rounded-full bg-white text-[#050505] font-semibold text-center text-sm shadow-lg hover:bg-neutral-200 transition-colors"
        >
          Open Auditor
        </button>
        <button
          type="button"
          onClick={() => {
            onClose()
            alert('Second Opinion Architecture: 100% Local-first deterministic token-level offsets, BM25 retrieval, and optional DeBERTa NLI cross-examination without external paid APIs.')
          }}
          className="w-full py-2.5 text-center text-sm text-[var(--muted)] hover:text-white transition-colors"
        >
          View Architecture
        </button>
      </div>
    </nav>
  )
}
