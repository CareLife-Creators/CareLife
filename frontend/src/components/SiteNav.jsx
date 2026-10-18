import { useEffect, useState } from 'react'
import { logout } from '../api/auth'
import './SiteNav.css'

const publicLinks = [
  { href: '#home', label: 'Home' },
  { href: '#daycare-directory', label: 'Daycare directory' },
]

const memberLinks = [
  { href: '#dashboard', label: 'Dashboard' },
  { href: '#verification', label: 'Verification' },
  { href: '#organization-approval', label: 'Admin approvals' },
]

function SiteNav() {
  const [open, setOpen] = useState(false)
  const [current, setCurrent] = useState(window.location.hash || '#home')
  const [hasSession, setHasSession] = useState(
    Boolean(localStorage.getItem('carelife_access_token'))
  )

  useEffect(() => {
    function syncNavigation() {
      setCurrent(window.location.hash || '#home')
      setHasSession(Boolean(localStorage.getItem('carelife_access_token')))
      setOpen(false)
    }

    window.addEventListener('hashchange', syncNavigation)
    window.addEventListener('storage', syncNavigation)

    return () => {
      window.removeEventListener('hashchange', syncNavigation)
      window.removeEventListener('storage', syncNavigation)
    }
  }, [])

  const links = hasSession ? [...publicLinks, ...memberLinks] : publicLinks

  return (
    <header className="site-nav">
      <div className="site-nav-inner">
        <a className="site-nav-brand" href="#home" aria-label="CareLife home">
          <span className="site-nav-logo" aria-hidden="true">C</span>
          <span>CareLife</span>
        </a>

        <button
          type="button"
          className="site-nav-toggle"
          aria-expanded={open}
          aria-controls="site-nav-menu"
          aria-label={open ? 'Close navigation menu' : 'Open navigation menu'}
          onClick={() => setOpen((value) => !value)}
        >
          <span />
          <span />
          <span />
        </button>

        <nav
          id="site-nav-menu"
          className={open ? 'site-nav-menu open' : 'site-nav-menu'}
          aria-label="Main navigation"
        >
          {links.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className={current === link.href ? 'site-nav-link active' : 'site-nav-link'}
              aria-current={current === link.href ? 'page' : undefined}
              onClick={() => setOpen(false)}
            >
              {link.label}
            </a>
          ))}

          {hasSession ? (
            <button
              type="button"
              className="site-nav-cta"
              onClick={() => { void logout() }}
            >
              Sign out
            </button>
          ) : (
            <>
              <a
                href="#login"
                className={current === '#login' ? 'site-nav-link active' : 'site-nav-link'}
                onClick={() => setOpen(false)}
              >
                Sign in
              </a>
              <a
                href="#signup"
                className="site-nav-cta"
                onClick={() => setOpen(false)}
              >
                Get started
              </a>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}

export default SiteNav
