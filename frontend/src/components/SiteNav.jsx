import { useEffect, useState } from 'react'
import { logout } from '../api/auth'
import './SiteNav.css'
const publicLinks = [
  { href: '#home', label: 'Home' }, { href: '#daycare', label: 'Daycare' },
  { href: '#orphanage', label: 'Orphanage' }, { href: '#elderly-care', label: 'Elderly care' },
  { href: '#caregivers', label: 'Caregivers' },
]
const memberLinks = [
  { href: '#dashboard', label: 'My workspace' }, { href: '#verification', label: 'Verification' },
  { href: '#organization-approval', label: 'Admin approvals' },
]
function SiteNav() {
  const [open, setOpen] = useState(false)
  const [current, setCurrent] = useState(window.location.hash || '#home')
  const [hasSession, setHasSession] = useState(Boolean(localStorage.getItem('carelife_access_token')))
  useEffect(() => {
    function sync() {
      setCurrent(window.location.hash || '#home')
      setHasSession(Boolean(localStorage.getItem('carelife_access_token')))
      setOpen(false)
    }
    window.addEventListener('hashchange', sync)
    window.addEventListener('storage', sync)
    return () => { window.removeEventListener('hashchange', sync); window.removeEventListener('storage', sync) }
  }, [])
  const activeHref = current === '#daycare-directory' ? '#daycare'
    : current === '#elderly-care-directory' ? '#elderly-care'
      : current === '#orphanage-support' ? '#orphanage' : current
  const links = hasSession ? [...publicLinks, ...memberLinks] : publicLinks
  async function signOut() {
    try { await logout() } finally { setHasSession(false); window.location.hash = '#home' }
  }
  return <header className="site-nav"><div className="site-nav-inner">
    <a className="site-nav-brand" href="#home" aria-label="CareLife home"><span className="site-nav-logo" aria-hidden="true">C</span><span>CareLife</span></a>
    <button type="button" className="site-nav-toggle" aria-expanded={open} aria-controls="site-nav-menu" aria-label={open ? 'Close navigation menu' : 'Open navigation menu'} onClick={() => setOpen(v => !v)}><span /><span /><span /></button>
    <nav id="site-nav-menu" className={open ? 'site-nav-menu open' : 'site-nav-menu'} aria-label="Main navigation">
      {links.map(link => <a key={link.href} href={link.href} className={activeHref === link.href ? 'site-nav-link active' : 'site-nav-link'} aria-current={activeHref === link.href ? 'page' : undefined} onClick={() => setOpen(false)}>{link.label}</a>)}
      {hasSession ? <button type="button" className="site-nav-cta" onClick={() => { void signOut() }}>Sign out</button> : <>
        <a href="#login" className={current === '#login' ? 'site-nav-link active' : 'site-nav-link'} onClick={() => setOpen(false)}>Sign in</a>
        <a href="#signup" className="site-nav-cta" onClick={() => setOpen(false)}>Get started</a>
      </>}
    </nav>
  </div></header>
}
export default SiteNav
