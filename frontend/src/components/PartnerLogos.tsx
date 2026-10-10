export function PartnerLogos() {
  return (
    <div
      className="logos anim-fade-logos absolute pointer-events-none select-none z-10 text-[var(--strip)]"
      style={{
        width: 'calc(741 * var(--u))',
        left: '50%',
        top: 'calc(995 * var(--u))',
        transform: 'translateX(calc(-50% + 20 * var(--u)))',
      }}
      aria-label="Partner organizations"
    >
      {/* Mark 1 */}
      <div
        className="lg lg1 absolute flex items-center"
        style={{
          left: 'calc(-0.5 * var(--u))',
          top: 'calc(-0.3 * var(--u))',
        }}
      >
        <svg
          viewBox="0 0 30 31"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          style={{ width: 'calc(30.5 * var(--u))', height: 'calc(31 * var(--u))' }}
          aria-hidden="true"
        >
          <mask id="lg1-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="30" height="31">
            <rect width="30" height="31" fill="#fff" />
            <circle cx="19.5" cy="10.5" r="5.1" fill="#000" />
          </mask>
          <rect width="30" height="31" rx="4" fill="currentColor" mask="url(#lg1-mask)" />
          <circle cx="19.5" cy="10.5" r="3.2" fill="currentColor" />
        </svg>
        <span
          className="font-ipsum tracking-tight leading-none"
          style={{
            marginLeft: 'calc(6.5 * var(--u))',
            fontSize: 'calc(18.1 * var(--u))',
          }}
        >
          logoipsum
        </span>
      </div>

      {/* Mark 2 */}
      <div
        className="lg lg2 absolute flex items-center"
        style={{
          left: 'calc(206.5 * var(--u))',
          top: 'calc(0.7 * var(--u))',
        }}
      >
        <svg
          viewBox="0 0 25 30"
          fill="currentColor"
          xmlns="http://www.w3.org/2000/svg"
          style={{ width: 'calc(24.5 * var(--u))', height: 'calc(30 * var(--u))' }}
          aria-hidden="true"
        >
          <path d="M0 0h6v30H0zM12.5 0A12.5 12.5 0 0 1 25 12.5a6.25 6.25 0 0 1-6.25 6.25 6.25 6.25 0 0 0-6.25 6.25V0z" />
        </svg>
        <span
          className="font-ipsum tracking-tight leading-none inline-flex items-center"
          style={{
            marginLeft: 'calc(6.5 * var(--u))',
            fontSize: 'calc(18.5 * var(--u))',
          }}
        >
          logoipsum
          <span
            className="inline-block rounded-full bg-current"
            style={{
              width: '0.12em',
              height: '0.12em',
              marginLeft: '0.08em',
              verticalAlign: '0.62em',
            }}
          />
        </span>
      </div>

      {/* Mark 3 */}
      <div
        className="lg lg3 absolute flex items-center"
        style={{
          left: 'calc(416.5 * var(--u))',
          top: 'calc(1.7 * var(--u))',
        }}
      >
        <svg
          viewBox="0 0 28 28"
          fill="none"
          stroke="currentColor"
          strokeWidth="3.1"
          xmlns="http://www.w3.org/2000/svg"
          style={{ width: 'calc(28.5 * var(--u))', height: 'calc(28 * var(--u))' }}
          aria-hidden="true"
        >
          <circle cx="14" cy="14" r="12.35" />
          <path d="M7 14a7 7 0 0 1 7-7" strokeLinecap="round" />
          <path d="M21 14a7 7 0 0 1-7 7" strokeLinecap="round" />
        </svg>
        <span
          className="font-ipsum tracking-tight leading-none"
          style={{
            marginLeft: 'calc(6.5 * var(--u))',
            fontSize: 'calc(16.15 * var(--u))',
          }}
        >
          logoipsum
        </span>
      </div>

      {/* Mark 4 */}
      <div
        className="lg lg4 absolute flex items-center"
        style={{
          left: 'calc(620.5 * var(--u))',
          top: 'calc(3.7 * var(--u))',
        }}
      >
        <svg
          viewBox="0 0 28 25.5"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          style={{ width: 'calc(28.5 * var(--u))', height: 'calc(25.5 * var(--u))' }}
          aria-hidden="true"
        >
          <path d="M0 10c4-4 8-4 14 0s10 4 14 0V0H0v10z" fill="currentColor" />
          <path d="M0 16c4-3 8-3 14 0s10 3 14 0" stroke="currentColor" strokeWidth="3.05" strokeLinecap="round" />
          <path d="M0 22c4-3 8-3 14 0s10 3 14 0" stroke="currentColor" strokeWidth="3.05" strokeLinecap="round" />
        </svg>
        <span
          className="font-ipsum tracking-tight leading-none"
          style={{
            marginLeft: 'calc(6.5 * var(--u))',
            fontSize: 'calc(15.3 * var(--u))',
          }}
        >
          logoipsum
        </span>
      </div>
    </div>
  )
}
