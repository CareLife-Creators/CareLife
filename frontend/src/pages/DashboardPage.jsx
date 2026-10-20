import SiteNav from '../components/SiteNav'
import { isAdmin, isStaff, roleLabel } from '../lib/roles'
import { useSession } from '../lib/session'
import './DashboardPage.css'

const modules = [
  { number: '01', icon: '✳', title: 'Daycare', text: 'Daycare discovery and the workflows around enrollment, attendance, and daily updates.', href: '#daycare', action: 'Open daycare', tone: 'mint' },
  { number: '02', icon: '♡', title: 'Orphanage', text: 'Explore fundraising campaigns, in-kind needs, and published impact updates.', href: '#orphanage', action: 'Explore support', tone: 'peach' },
  { number: '03', icon: '☼', title: 'Elderly care', text: 'Find care homes and caregivers, with private family and resident workflows protected by role.', href: '#elderly-care', action: 'Open elderly care', tone: 'lavender' },
]

// Tools differ by role. The backend enforces the same rules.
function toolsFor(role) {
  if (isAdmin(role)) {
    return {
      title: 'Administration',
      intro: 'Review organizations and staff access requests.',
      links: [
        { href: '#organization-approval', icon: '◇', title: 'Organization approvals', text: 'Review organization submissions.' },
        { href: '#admin-role-requests', icon: '✓', title: 'Staff access requests', text: 'Approve or reject requests for staff roles.' },
      ],
    }
  }
  if (isStaff(role)) {
    return {
      title: 'Your organization',
      intro: 'Tools for your organization’s staff.',
      links: [
        { href: '#verification', icon: '✓', title: 'Organization verification', text: 'Check your organization’s review status.' },
      ],
    }
  }
  return {
    title: 'Staff access',
    intro: 'Work at a daycare, orphanage or care home?',
    links: [
      { href: '#staff-access', icon: '✓', title: 'Request staff access', text: 'Ask a CareLife administrator for a staff role.' },
    ],
  }
}

function DashboardPage() {
  const { email: storedEmail, role } = useSession()
  const email = storedEmail || 'CareLife member'
  const tools = toolsFor(role)

  return <>
    <SiteNav />
    <main className="member-dashboard">
      <header className="member-dashboard-header">
        <div>
          <p className="member-dashboard-eyebrow">YOUR CARELIFE</p>
          <h1>Good to see you.</h1>
          <p className="member-dashboard-intro">Signed in as <strong>{email}</strong>{role ? ' · ' + roleLabel(role) : ''}. Start with a module or open one of your tools.</p>
        </div>
        <div className="member-dashboard-avatar" aria-hidden="true">{email.charAt(0).toUpperCase()}</div>
      </header>
      <section className="member-dashboard-section" aria-labelledby="member-module-title">
        <div className="member-dashboard-section-heading">
          <div><p className="member-dashboard-eyebrow">CARE WORKSPACES</p><h2 id="member-module-title">Three modules, one account</h2></div>
          <span className="member-dashboard-count">Choose a path</span>
        </div>
        <div className="member-dashboard-grid">
          {modules.map((item) => (
            <article className={'member-dashboard-card ' + item.tone} key={item.href}>
              <div className="member-dashboard-card-top"><span className="member-dashboard-card-icon" aria-hidden="true">{item.icon}</span><span className="member-dashboard-number">{item.number}</span></div>
              <h3>{item.title}</h3><p>{item.text}</p>
              <a href={item.href}>{item.action}<span aria-hidden="true">→</span></a>
            </article>
          ))}
        </div>
      </section>
      <section className="member-tools-section" aria-labelledby="member-tools-title">
        <div><p className="member-dashboard-eyebrow">YOUR TOOLS</p><h2 id="member-tools-title">{tools.title}</h2><p>{tools.intro}</p></div>
        <div className="member-tool-links">
          {tools.links.map((link) => (
            <a href={link.href} key={link.href}>
              <span aria-hidden="true">{link.icon}</span>
              <span><strong>{link.title}</strong><small>{link.text}</small></span>
              <span aria-hidden="true">↗</span>
            </a>
          ))}
        </div>
      </section>
      <aside className="member-dashboard-note">
        <span className="member-dashboard-note-icon" aria-hidden="true">i</span>
        <div><strong>Access depends on your role</strong><p>Public directories can be explored without opening private records. Child, resident, financial, and organization-management actions are checked by the backend for your role.</p></div>
      </aside>
    </main>
  </>
}
export default DashboardPage