import SiteNav from '../../components/SiteNav'
import { useSession } from '../../lib/session'
import './ModuleLandingPage.css'

const content = {
  daycare: {
    tone: 'mint', name: 'Daycare',
    title: 'Choose a daycare you can look into.',
    lede: 'Search daycare centers by name and location, or find an independent caregiver. Once your child is enrolled, attendance and daily notes come from the staff who are with them.',
    now: [['Daycare directory', 'Search centers and read their public details.', '#daycare-directory'], ['Caregiver directory', 'Find independent childcare caregivers.', '#caregivers']],
    soon: [['Child profile and enrollment', 'Add your child and send an enrollment request.'], ['Attendance and daily notes', 'See arrivals and notes from the staff on duty.'], ['Emergency contacts and pickup', 'Name who may collect your child.']],
    faq: [['Who can see my child’s details?', 'You, and the staff of the daycare your child is enrolled in. Public listings show centers, never children.'], ['Does “verified” mean government-licensed?', 'No. It means CareLife reviewed the organization’s submission. Check licensing with the authorities as well.']],
  },
  orphanage: {
    tone: 'peach', name: 'Orphanage',
    title: 'See what an orphanage needs before you give.',
    lede: 'Each organization lists its fundraising goals and in-kind needs, then publishes updates on what the support did. Children’s private records are never shown here.',
    now: [['Support board', 'Browse campaigns, current needs and impact updates. Signed-in members can pledge items.', '#orphanage-support']],
    soon: [['Giving through bKash', 'Pay a campaign directly from the board.'], ['Impact update editor', 'Staff publish updates with photos for donors.']],
    faq: [['Can I give money on the site today?', 'Not yet. Item pledges are open now; bKash checkout is the next piece.'], ['Will I see children’s names or photos?', 'No. Private child and outcome records are limited to authorized staff.']],
  },
  'elderly-care': {
    tone: 'lavender', name: 'Elderly care',
    title: 'Find care for a parent, and stay in the loop.',
    lede: 'Compare care homes and caregivers by services, fees and capacity. A family member can be authorized for one resident, then request check-ins that staff answer.',
    now: [['Care-home directory', 'Compare homes by fees, capacity and services.', '#elderly-care-directory'], ['Caregiver directory', 'Find caregivers for home visits.', '#caregivers']],
    soon: [['Resident access and consent', 'The care home authorizes you for one resident.'], ['Family check-ins', 'Ask for an update and get a recorded answer.'], ['Wellbeing notes', 'Short non-clinical notes, like a walk or a visit.']],
    faq: [['Is this a medical record?', 'No. CareLife shares everyday updates, not diagnoses or prescriptions.'], ['Who sees my relative’s updates?', 'Only family members the care home has authorized for that resident.']],
  },
}

function ModuleLandingPage({ moduleKey }) {
  const { signedIn } = useSession()
  const m = content[moduleKey] || content.daycare
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
          <h2 id="ml-now">Open now</h2>
          <div className="ml-cards">
            {m.now.map(([t, d, href]) => (
              <a className="ml-card" href={href} key={href}><strong>{t}</strong><span>{d}</span><em>Open</em></a>
            ))}
          </div>
        </section>

        <section className="ml-block" aria-labelledby="ml-soon">
          <h2 id="ml-soon">Being built</h2>
          <ul className="ml-soon">
            {m.soon.map(([t, d]) => <li key={t}><strong>{t}</strong><span>{d}</span></li>)}
          </ul>
        </section>

        <section className="ml-block" aria-labelledby="ml-faq">
          <h2 id="ml-faq">Questions people ask</h2>
          {m.faq.map(([q, a]) => <details key={q}><summary>{q}</summary><p>{a}</p></details>)}
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