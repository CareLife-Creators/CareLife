import { logout } from '../api/auth'
import { useSession } from '../lib/session'
import './AdminNav.css'

const navigation = [
  { href: '#dashboard', label: 'Overview' },
  { href: '#admin-users', label: 'Users' },
  { href: '#organization-approval', label: 'Organizations' },
  { href: '#admin-operations?tab=caregivers', label: 'Caregiver review' },
  { href: '#admin-operations?tab=impact', label: 'Impact review' },
  { href: '#admin-operations?tab=audit', label: 'Audit log' },
]

export default function AdminNav() {
  const { email } = useSession()
  const current = window.location.hash

  return <header className="admin-nav">
    <a className="admin-nav-brand" href="#dashboard"><span className="admin-nav-mark" aria-hidden="true">C</span><span>CARELIFE<small>OPERATIONS CONSOLE</small></span></a>
    <nav aria-label="Administration">
      {navigation.map((item) => {
        const route = item.href.split('?')[0]
        const currentTab = new URLSearchParams(current.split('?')[1] || '').get('tab') || 'caregivers'
        const itemTab = new URLSearchParams(item.href.split('?')[1] || '').get('tab') || 'caregivers'
        const active = current.split('?')[0] === route && (route !== '#admin-operations' || currentTab === itemTab)
        return <a key={item.href} href={item.href} className={active ? 'active' : ''} aria-current={active ? 'page' : undefined}>{item.label}</a>
      })}
    </nav>
    <div className="admin-nav-user"><span className="admin-nav-status" aria-hidden="true"/><span className="admin-nav-email">{email || 'Administrator'}</span><button type="button" onClick={() => void logout()}>Sign out</button></div>
  </header>
}
