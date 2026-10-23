import SiteNav from '../../components/SiteNav'
import { useSession } from '../../lib/session'
import './ModuleLandingPage.css'

const content = {
  daycare: {
    tone: 'mint',
    index: '01',
    label: 'Daycare',
    note: 'A steadier day for your family',
    title: 'Find the right daycare for your family.',
    lede: 'Explore daycare centers by name or location, review the details they share and find caregivers who can support your family at home.',
    now: [
      ['Daycare directory', 'Search by center name or location and review what each place shares.', '#daycare-directory'],
      ['Caregiver directory', 'Browse independent caregivers and the services they offer.', '#caregivers'],
    ],
    tools: [
      ['A child’s profile', 'Keep your child’s details, emergency contacts and pickup people together.', '#my-children'],
      ['Everyday updates', 'Follow attendance and notes about your child’s day.', '#my-children'],
      ['Enrollment', 'Start a request and keep up with its progress.', '#my-children'],
    ],
    faq: [
      ['Who can see my child’s details?', 'Your child’s private details stay within your CareLife account and do not appear in the public daycare directory.'],
      ['What does a reviewed listing mean?', 'CareLife has reviewed the details submitted for a listing. Families should also check licensing and visit a center before choosing.'],
    ],
  },
  orphanage: {
    tone: 'peach',
    index: '02',
    label: 'Orphanage support',
    note: 'Give support where it matters',
    title: 'Give support that meets a real need.',
    lede: 'See current campaigns and requested items from children’s homes. Make a pledge and follow updates about the difference your support makes.',
    now: [
      ['Children’s home support board', 'Browse campaigns, requested items and updates from children’s homes.', '#orphanage-support'],
    ],
    tools: [
      ['Campaigns and requested items', 'See what children’s homes are raising and pledge useful items.', '#orphanage-support'],
      ['Progress updates', 'Follow the updates shared by children’s homes.', '#orphanage-support'],
    ],
    faq: [
      ['Can I donate with bKash?', 'When bKash is available for a campaign, you’ll see it as an option before completing your donation.'],
      ['What will I see on the support board?', 'You can browse campaigns, requested items and updates shared by children’s homes. Private child details are not shown.'],
    ],
  },
  'elderly-care': {
    tone: 'lavender',
    index: '03',
    label: 'Elderly care',
    note: 'Thoughtful care, closer to home',
    title: 'Find thoughtful care for someone you love.',
    lede: 'Explore care homes and independent caregivers, review the details they share and choose a next step that suits your family.',
    now: [
      ['Care-home directory', 'Explore locations, facilities, capacity and published fees.', '#elderly-care-directory'],
      ['Caregiver directory', 'Find independent caregivers by service and location.', '#caregivers'],
    ],
    tools: [
      ['Care requests', 'Ask about a care service and follow the request.', '#care-bookings'],
      ['Family check-ins', 'Keep up with wellbeing notes shared with your family.', '#family-checkins'],
      ['Care-home information', 'Learn about the services and facilities a care home provides.', '#elderly-care-directory'],
    ],
    faq: [
      ['Are check-ins medical advice?', 'No. Check-ins are updates about wellbeing and are not a diagnosis or a prescription.'],
      ['Can my family stay informed?', 'Family check-ins help relatives follow updates shared about a loved one’s wellbeing.'],
    ],
  },
}

function ModuleLandingPage({ moduleKey }) {
  const { signedIn } = useSession()
  const m = content[moduleKey] || content.daycare
  const tools = m.tools
  const scrollToStart = () => document.getElementById('ml-start')?.scrollIntoView({
    behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
    block: 'start',
  })
  return (
    <>
      <SiteNav />
      <main className={'ml ' + m.tone}>
        <header className="ml-hero">
          <div className="ml-hero-copy">
            <a className="ml-back" href={signedIn ? '#dashboard' : '#home'}><span aria-hidden="true">←</span> {signedIn ? 'My workspace' : 'CareLife home'}</a>
            <span className="ml-eyebrow"><i /> {m.label} <span>·</span> {m.index}</span>
            <h1>{m.title}</h1>
            <p>{m.lede}</p>
            <div className="ml-hero-actions">
              <a className="ml-btn" href={m.now[0][2]}>{m.now[0][0]} <span aria-hidden="true">→</span></a>
              <button className="ml-text-link" type="button" onClick={scrollToStart}>See what you can do <span aria-hidden="true">↓</span></button>
            </div>
          </div>
          <div className="ml-hero-art" role="img" aria-label={`${m.label}: ${m.note}`}>
            <span className="ml-art-orbit ml-art-orbit-one" />
            <span className="ml-art-orbit ml-art-orbit-two" />
            <span className="ml-art-index">{m.index}</span>
            <div className="ml-art-note"><i /><span>{m.note}</span></div>
            <div className="ml-art-stamp">Care<br />lives<br />here<span aria-hidden="true">♡</span></div>
          </div>
        </header>
        <section className="ml-block ml-start" id="ml-start" aria-labelledby="ml-now">
          <div className="ml-section-heading"><div><span className="ml-section-kicker">START HERE</span><h2 id="ml-now">Find the right place to begin.</h2></div><p>Choose a directory to explore the options available through CareLife.</p></div>
          <div className="ml-cards">
            {m.now.map(([title, description, href]) => (
              <a className="ml-card ml-directory-card" href={href} key={href}><span className="ml-card-icon" aria-hidden="true">↗</span><span className="ml-card-body"><strong>{title}</strong><span>{description}</span><em>{signedIn ? 'Explore directory' : 'Sign in to explore'} <span aria-hidden="true">→</span></em></span></a>
            ))}
          </div>
        </section>
        <section className="ml-block" aria-labelledby="ml-tools">
          <div className="ml-section-heading"><div><span className="ml-section-kicker">CARE THAT CONNECTS</span><h2 id="ml-tools">More ways CareLife can help.</h2></div><p>Each option supports a practical part of caring, giving or staying connected.</p></div>
          <div className="ml-cards ml-feature-grid">
            {tools.map(([title, description, href]) => (
              <a className="ml-card ml-feature-card" href={href} key={title}><span className="ml-feature-mark" aria-hidden="true">✳</span><strong>{title}</strong><span>{description}</span><em>{signedIn ? 'Open this feature' : 'Sign in to continue'} <span aria-hidden="true">→</span></em></a>
            ))}
          </div>
        </section>
        <section className="ml-block" aria-labelledby="ml-faq">
          <div className="ml-section-heading"><div><span className="ml-section-kicker">GOOD TO KNOW</span><h2 id="ml-faq">A few helpful answers.</h2></div></div>
          {m.faq.map(([question, answer]) => <details key={question}><summary>{question}</summary><p>{answer}</p></details>)}
        </section>
        <footer className="ml-foot">
          <div><span className="ml-section-kicker">A LITTLE CLOSER, EVERY DAY</span><h2>Start with what matters to you.</h2><p>Take the next step with CareLife.</p></div>
          {signedIn ? <a className="ml-btn" href="#dashboard">Open my workspace <span aria-hidden="true">→</span></a> : <a className="ml-btn" href="#signup">Create an account <span aria-hidden="true">→</span></a>}
        </footer>
      </main>
    </>
  )
}

export default ModuleLandingPage
