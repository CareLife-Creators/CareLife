import { useEffect, useState } from 'react'
import { logout } from '../api/auth'
import { memberLinks, roleLabel } from '../lib/roles'
import { useSession } from '../lib/session'
import './SiteNav.css'

const publicLinks = [
  { href: '#home', label: 'Home' },
  { href: '#daycare', label: 'Daycare' },
  { href: '#orphanage', label: 'Orphanage' },
  { href: '#elderly-care', label: 'Elderly care' },
  { href: '#caregivers', label: 'Caregivers' },
]

function SiteNav() {
  const [open, setOpen] = useState(false)
  const [current, setCurrent] = useState(window.location.hash || '#home')
  const { signedIn, role } = useSession()

  useEffect(() => {
    function sync() {
      setCurrent(window.location.hash || '#home')
      setOpen(false)
    }
    window.addEventListener('hashchange', sync)
    return () => window.removeEventListener('hashchange', sync)
  }, [])

  const activeHref = current === '#daycare-directory' ? '#daycare'
    : current === '#elderly-care-directory' ? '#elderly-care'
      : current === '#orphanage-support' ? '#orphanage' : current

  // Signed-in menu depends on the user's role. The backend enforces access too.
  const links = signedIn ? memberLinks(role) : publicLinks

  return (
    <header className="site-nav">
      <div className="site-nav-inner">
        <a className="site-nav-brand" href={signedIn ? '#dashboard' : '#home'} aria-label="CareLife home">
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
          <span /><span /><span />
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
              className={activeHref === link.href ? 'site-nav-link active' : 'site-nav-link'}
              aria-current={activeHref === link.href ? 'page' : undefined}
              onClick={() => setOpen(false)}
            >
              {link.label}
            </a>
          ))}

          {signedIn ? (
            <>
              {role && <span className="site-nav-role">{roleLabel(role)}</span>}
              <button type="button" className="site-nav-cta" onClick={() => { void logout() }}>
                Sign out
              </button>
            </>
          ) : (
            <>
              <a
                href="#login"
                className={current === '#login' ? 'site-nav-link active' : 'site-nav-link'}
                onClick={() => setOpen(false)}
              >
                Sign in
              </a>
              <a href="#signup" className="site-nav-cta" onClick={() => setOpen(false)}>
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