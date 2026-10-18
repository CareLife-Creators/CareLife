import SiteNav from '../components/SiteNav'
import './DashboardPage.css'

const quickLinks = [
  {
    icon: '⌕',
    title: 'Daycare directory',
    description: 'Browse the current public directory of verified daycare centers.',
    label: 'Browse directory',
    href: '#daycare-directory',
  },
  {
    icon: '✓',
    title: 'Organization verification',
    description: 'View verification status for an organization you are authorized to access.',
    label: 'Check status',
    href: '#verification',
  },
  {
    icon: '◎',
    title: 'Organization approvals',
    description: 'Review pending verification requests if your account has administrator access.',
    label: 'Open approvals',
    href: '#organization-approval',
  },
]

function DashboardPage() {
  const email = localStorage.getItem('carelife_user') || 'CareLife member'

  return (
    <>
      <SiteNav />
      <main className="member-dashboard">
        <header className="member-dashboard-header">
          <div>
            <p className="member-dashboard-eyebrow">YOUR WORKSPACE</p>
            <h1>Welcome back.</h1>
            <p className="member-dashboard-intro">
              Signed in as <strong>{email}</strong>. Pick up where you need to be.
            </p>
          </div>
          <div className="member-dashboard-avatar" aria-hidden="true">
            {email.charAt(0).toUpperCase()}
          </div>
        </header>

        <section className="member-dashboard-section">
          <div className="member-dashboard-section-heading">
            <div>
              <p className="member-dashboard-eyebrow">QUICK ACCESS</p>
              <h2>Available workspaces</h2>
            </div>
            <span className="member-dashboard-count">3 destinations</span>
          </div>

          <div className="member-dashboard-grid">
            {quickLinks.map((item) => (
              <article className="member-dashboard-card" key={item.href}>
                <span className="member-dashboard-card-icon" aria-hidden="true">{item.icon}</span>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
                <a href={item.href}>{item.label} <span aria-hidden="true">→</span></a>
              </article>
            ))}
          </div>
        </section>

        <aside className="member-dashboard-note">
          <span className="member-dashboard-note-icon" aria-hidden="true">i</span>
          <div>
            <strong>Your workspace is evolving</strong>
            <p>
              Only the frontend screens currently connected to working routes are listed here.
              Other CareLife modules should be added when their user flows and API integrations
              are ready, rather than linked to unfinished pages.
            </p>
          </div>
        </aside>
      </main>
    </>
  )
}

export default DashboardPage
