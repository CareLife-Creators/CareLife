import { useEffect, useState } from 'react'
import CareLifeLogo from './CareLifeLogo'
import { logout } from '../api/auth'
import { memberLinks, roleLabel } from '../lib/roles'
import { useSession } from '../lib/session'
import { getMyNotifications, getMyProfile } from '../api/workspace'
import { publicOrganizationName } from '../lib/publicDisplay'
import './SiteNav.css'

const publicLinks = [
  { href: '#home', label: 'Home' },
  { href: '#daycare', label: 'Daycare' },
  { href: '#orphanage', label: 'Orphanage' },
  { href: '#elderly-care', label: 'Elderly care' },
  { href: '#caregivers', label: 'Caregivers' },
  { href: '#for-organizations', label: 'For organizations' },
]

function SiteNav() {
  const [open, setOpen] = useState(false)
  const [accountMenuOpen, setAccountMenuOpen] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)
  const [displayName, setDisplayName] = useState('')
  const [current, setCurrent] = useState(window.location.hash || '#home')
  const { signedIn, role, email } = useSession()

  useEffect(() => {
    if (!signedIn) {
      setUnreadCount(0)
      setDisplayName('')
      return undefined
    }
    let mounted = true
    const refreshNavData = async () => {
      const [notifications, profile] = await Promise.allSettled([
        getMyNotifications({ unreadOnly: true }), getMyProfile(),
      ])
      if (!mounted) return
      if (notifications.status === 'fulfilled') setUnreadCount(Array.isArray(notifications.value) ? notifications.value.filter((item) => !item.is_read).length : 0)
      if (profile.status === 'fulfilled') setDisplayName(publicOrganizationName(profile.value.full_name) || '')
    }
    void refreshNavData()
    const interval = window.setInterval(() => void refreshNavData(), 60000)
    window.addEventListener('focus', refreshNavData)
    window.addEventListener('carelife:notifications-updated', refreshNavData)
    return () => {
      mounted = false
      window.clearInterval(interval)
      window.removeEventListener('focus', refreshNavData)
      window.removeEventListener('carelife:notifications-updated', refreshNavData)
    }
  }, [signedIn])

  useEffect(() => {
    function sync() {
      setCurrent(window.location.hash || '#home')
      setOpen(false)
      setAccountMenuOpen(false)
    }
    window.addEventListener('hashchange', sync)
    return () => window.removeEventListener('hashchange', sync)
  }, [])

  const activeHref = current === '#daycare-directory' ? '#daycare'
    : current === '#elderly-care-directory' ? '#elderly-care'
      : current === '#orphanage-support' ? '#orphanage' : current

  function openFamilyCareMap(event) {
    event.preventDefault()
    setOpen(false)
    const scrollToMap = () => {
      const map = document.getElementById('family-discovery')
      if (map) map.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' })
    }
    if (window.location.hash.split('?')[0] !== '#dashboard') {
      window.location.hash = '#dashboard'
      window.setTimeout(scrollToMap, 120)
    } else {
      scrollToMap()
    }
  }

  // Signed-in menu depends on the user's role. The backend enforces access too.
  const links = signedIn ? memberLinks(role) : publicLinks
  const profileLabel = displayName || (email ? email.split('@')[0].replace(/[._-]+/g, ' ') : 'Your profile')
  const initials = profileLabel.trim().split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join('').toUpperCase() || 'C'

  return (
    <header className="site-nav">
      <div className="site-nav-inner">
        <a className="site-nav-brand" href={signedIn ? '#dashboard' : '#home'} aria-label="CareLife home">
          <CareLifeLogo size={32} />
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
              onClick={link.label === 'Find care' && role === 'parent_guardian' ? openFamilyCareMap : () => setOpen(false)}
            >
              {link.label}
            </a>
          ))}

          {signedIn ? (
            <>
              <a className={current === '#messages' ? 'site-nav-messages active' : 'site-nav-messages'} href="#messages" aria-label="Messages" title="Messages" onClick={() => setOpen(false)}>
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 11.5a7.5 7.5 0 0 1-7.5 7.5H7l-3.5 2v-5.1A7.5 7.5 0 1 1 20 11.5Z" /><path d="M8 10h8M8 13.5h5" /></svg>
              </a>
              <a className={current === '#notifications' ? 'site-nav-notifications active' : 'site-nav-notifications'} href="#notifications" aria-label={unreadCount ? `Notifications, ${unreadCount} unread` : 'Notifications'} title="Notifications">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4" /></svg>
                {unreadCount > 0 && <span className="site-nav-notification-count">{unreadCount > 9 ? '9+' : unreadCount}</span>}
              </a>
              <div className="site-nav-account">
                <button type="button" className="site-nav-profile-trigger" aria-expanded={accountMenuOpen} aria-haspopup="menu" onClick={() => setAccountMenuOpen((value) => !value)}>
                  <span className="site-nav-profile-avatar" aria-hidden="true">{initials}</span>
                  <span className="site-nav-profile-name">{profileLabel}</span>
                  <svg className="site-nav-chevron" viewBox="0 0 16 16" aria-hidden="true"><path d="m4 6 4 4 4-4" /></svg>
                </button>
                {accountMenuOpen && <div className="site-nav-account-menu" role="menu">
                  <div className="site-nav-account-heading"><strong>{displayName || email || 'CareLife member'}</strong><small>{roleLabel(role)}</small></div>
                  <a role="menuitem" href="#account" onClick={() => setAccountMenuOpen(false)}>My profile</a>
                  <a role="menuitem" href="#messages" onClick={() => setAccountMenuOpen(false)}>Messages</a>
                  <button role="menuitem" type="button" onClick={() => { setAccountMenuOpen(false); void logout() }}>Sign out</button>
                </div>}
              </div>
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
