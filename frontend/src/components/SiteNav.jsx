import { useState } from 'react'
import './SiteNav.css'

const links = [
  { href: '#daycare-directory', label: 'Daycare Directory' },
  { href: '#organization-approval', label: 'Approvals' },
  { href: '#', label: 'Verification' },
]

function SiteNav() {
  const [open, setOpen] = useState(false)
  const current = window.location.hash

  return (
    <header className="site-nav">
      <div className="site-nav-inner">
        <a className="site-nav-brand" href="#daycare-directory">
          <span className="site-nav-logo">C</span>
          <span>CareLife</span>
        </a>

        <button
          type="button"
          className="site-nav-toggle"
          aria-expanded={open}
          aria-controls="site-nav-menu"
          aria-label={open ? 'Close menu' : 'Open menu'}
          onClick={() => setOpen((value) => !value)}
        >
          <span />
          <span />
          <span />
        </button>

        <nav
          id="site-nav-menu"
          className={open ? 'site-nav-menu open' : 'site-nav-menu'}
        >
          {links.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className={
                current === link.href
                  ? 'site-nav-link active'
                  : 'site-nav-link'
              }
              onClick={() => setOpen(false)}
            >
              {link.label}
            </a>
          ))}
          <a
            href="#login"
            className="site-nav-cta"
            onClick={() => setOpen(false)}
          >
            Sign in
          </a>
        </nav>
      </div>
    </header>
  )
}

export default SiteNav
