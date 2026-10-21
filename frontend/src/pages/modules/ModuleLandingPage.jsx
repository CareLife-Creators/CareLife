import SiteNav from '../../components/SiteNav'
import { useSession } from '../../lib/session'
import { isStaff } from '../../lib/roles'
import './ModuleLandingPage.css'

const content = {
  daycare: {
    tone: 'mint',
    title: 'Choose a daycare you can look into.',
    lede: 'Compare verified daycare listings, then manage your child’s enrollment, emergency contacts, pickup permissions and attendance from the private workspace.',
    now: [
      ['Daycare directory', 'Search centers by name or location and inspect their published details.', '#daycare-directory'],
      ['Caregiver directory', 'Browse approved independent caregivers.', '#caregivers'],
    ],
    tools: [
      ['Child profiles & enrollment', 'Register a child, select a listed daycare, and follow enrollment decisions.', '#my-children'],
      ['Attendance & daily updates', 'Review attendance history and the day notes recorded by authorized staff.', '#my-children'],
      ['Emergency contacts & pickup', 'Keep emergency numbers and authorized pickup people attached to the child profile.', '#my-children'],
    ],
    faq: [
      ['Who can see my child’s details?', 'Child profiles and their contacts are served through authenticated endpoints rather than the public daycare directory.'],
      ['What does a verified listing mean?', 'CareLife has reviewed the organization submission. A platform review is not a substitute for checking legal licensing with the relevant authority.'],
    ],
  },
  orphanage: {
    tone: 'peach',
    title: 'See what an orphanage needs before you give.',
    lede: 'Compare published fundraising targets and item needs, make an in-kind pledge, complete supported bKash campaign checkout, and read impact updates from organizations.',
    now: [
      ['Support board', 'View campaigns, in-kind needs and published impact updates; eligible donor accounts can start bKash checkout.', '#orphanage-support'],
    ],
    tools: [
      ['Campaigns & needs', 'Orphanage staff can publish fundraising campaigns and item or monetary needs.', '#organization-workspace'],
      ['Impact updates', 'Submit a written update to the backend’s review and publication workflow.', '#organization-workspace'],
    ],
    faq: [
      ['Can I donate with bKash?', 'The backend exposes a bKash checkout flow for accounts with the Donor / Supporter role. Checkout redirects to the payment URL returned by the payment gateway.'],
      ['Are child records visible to donors?', 'No. The public support board displays campaigns, needs and published updates, not private child or outcome records.'],
    ],
  },
  'elderly-care': {
    tone: 'lavender',
    title: 'Find care for a parent, and stay in the loop.',
    lede: 'Compare care homes and caregivers, request a scheduled service, and use the protected care-home workspace for resident profiles and consent-controlled wellbeing check-ins.',
    now: [
      ['Care-home directory', 'Review public details such as location, capacity, facilities and published fees.', '#elderly-care-directory'],
      ['Caregiver directory', 'Find approved caregivers by service type and location.', '#caregivers'],
    ],
    tools: [
      ['Care bookings', 'Request caregiver appointments or an elder-care booking and follow the returned status.', '#care-bookings'],
      ['Family wellbeing check-ins', 'Family representatives can submit and review updates for a resident they are authorized to access.', '#family-checkins'],
      ['Residents & family consent', 'Care-home staff can maintain resident profiles and record family consent before check-ins.', '#organization-workspace'],
    ],
    faq: [
      ['Are the check-ins medical records?', 'The wellbeing check-in workflow stores a wellbeing status and optional note; it is not a diagnosis or prescription service.'],
      ['Who can receive a family check-in?', 'The backend requires a consent record for the named family representative before allowing the related check-in workflow.'],
    ],
  },
}

function ModuleLandingPage({ moduleKey }) {
  const { signedIn, role } = useSession()
  const m = content[moduleKey] || content.daycare
  const staffTools = isStaff(role)
  const tools = m.tools.filter(([title]) => {
    if (title === 'Campaigns & needs' || title === 'Impact updates') return role === 'orphanage_staff' || role === 'carelife_admin'
    if (title === 'Residents & family consent') return role === 'care_home_staff' || role === 'carelife_admin'
    return true
  })
  return (
    <>
      <SiteNav />
      <main className={'ml ' + m.tone}>
        <header className="ml-hero">
          <a className="ml-back" href={signedIn ? '#dashboard' : '#home'}>← {signedIn ? 'My workspace' : 'CareLife'}</a>
          <h1>{m.title}</h1>
          <p>{m.lede}</p>
        </header>
        <section className="ml-block" aria-labelledby="ml-now">
          <h2 id="ml-now">Explore the directory</h2>
          <div className="ml-cards">
            {m.now.map(([title, description, href]) => (
              <a className="ml-card" href={href} key={href}><strong>{title}</strong><span>{description}</span><em>Open directory →</em></a>
            ))}
          </div>
        </section>
        <section className="ml-block" aria-labelledby="ml-tools">
          <h2 id="ml-tools">{staffTools ? 'Workflows for your account' : 'What you can do on CareLife'}</h2>
          <div className="ml-cards">
            {tools.map(([title, description, href]) => (
              <a className="ml-card" href={href} key={title}><strong>{title}</strong><span>{description}</span><em>Open workflow →</em></a>
            ))}
          </div>
        </section>
        <section className="ml-block" aria-labelledby="ml-faq">
          <h2 id="ml-faq">Questions about this module</h2>
          {m.faq.map(([question, answer]) => <details key={question}><summary>{question}</summary><p>{answer}</p></details>)}
        </section>
        <footer className="ml-foot">
          {signedIn ? <a className="ml-btn" href="#dashboard">Open my workspace</a> : <a className="ml-btn" href="#signup">Create an account</a>}
          <a href={signedIn ? '#dashboard' : '#home'}>Back to {signedIn ? 'my workspace' : 'the overview'}</a>
        </footer>
      </main>
    </>
  )
}

export default ModuleLandingPage
