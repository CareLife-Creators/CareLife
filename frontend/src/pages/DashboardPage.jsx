import SiteNav from '../components/SiteNav'
import './DashboardPage.css'
const modules = [
  {number:'01',icon:'✳',title:'Daycare',text:'Daycare discovery and the workflows around enrollment, attendance, and daily updates.',href:'#daycare',action:'Open daycare',tone:'mint'},
  {number:'02',icon:'♡',title:'Orphanage',text:'Explore fundraising campaigns, in-kind needs, and published impact updates.',href:'#orphanage',action:'Explore support',tone:'peach'},
  {number:'03',icon:'☼',title:'Elderly care',text:'Find care homes and caregivers, with private family and resident workflows protected by role.',href:'#elderly-care',action:'Open elderly care',tone:'lavender'},
]
function DashboardPage() {
  const email=localStorage.getItem('carelife_user')||'CareLife member'
  return <>
    <SiteNav/>
    <main className="member-dashboard">
      <header className="member-dashboard-header"><div><p className="member-dashboard-eyebrow">YOUR CARELIFE</p><h1>Good to see you.</h1><p className="member-dashboard-intro">Signed in as <strong>{email}</strong>. Start with a module or open a shared platform tool.</p></div><div className="member-dashboard-avatar" aria-hidden="true">{email.charAt(0).toUpperCase()}</div></header>
      <section className="member-dashboard-section" aria-labelledby="member-module-title"><div className="member-dashboard-section-heading"><div><p className="member-dashboard-eyebrow">CARE WORKSPACES</p><h2 id="member-module-title">Three modules, one account</h2></div><span className="member-dashboard-count">Choose a path</span></div><div className="member-dashboard-grid">{modules.map(item=><article className={'member-dashboard-card '+item.tone} key={item.href}><div className="member-dashboard-card-top"><span className="member-dashboard-card-icon" aria-hidden="true">{item.icon}</span><span className="member-dashboard-number">{item.number}</span></div><h3>{item.title}</h3><p>{item.text}</p><a href={item.href}>{item.action}<span aria-hidden="true">→</span></a></article>)}</div></section>
      <section className="member-tools-section" aria-labelledby="member-tools-title"><div><p className="member-dashboard-eyebrow">SHARED PLATFORM TOOLS</p><h2 id="member-tools-title">Verification and oversight</h2><p>Tools available to authorized organization members and CareLife administrators.</p></div><div className="member-tool-links"><a href="#verification"><span aria-hidden="true">✓</span><span><strong>Organization verification</strong><small>Check a permitted organization’s review status.</small></span><span aria-hidden="true">↗</span></a><a href="#organization-approval"><span aria-hidden="true">◇</span><span><strong>Admin approvals</strong><small>Review organization submissions when your role permits it.</small></span><span aria-hidden="true">↗</span></a></div></section>
      <aside className="member-dashboard-note"><span className="member-dashboard-note-icon" aria-hidden="true">i</span><div><strong>Access depends on your role</strong><p>Public directories can be explored without opening private records. Child, resident, financial, and organization-management actions must be authorized by the backend. More feature screens will be connected as their API workflows are completed.</p></div></aside>
    </main>
  </>
}
export default DashboardPage
