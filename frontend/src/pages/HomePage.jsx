import heroImage from '../assets/hero.png'
import SiteNav from '../components/SiteNav'
import './HomePage.css'
const modules = [
  { number:'01', icon:'✳', title:'Daycare', subtitle:'Care for growing minds', text:'Discover daycare centers and caregivers, then manage the everyday details that help children stay safe and supported.', features:['Center discovery','Caregiver profiles','Enrollment and daily care'], href:'#daycare', action:'Explore daycare', tone:'mint' },
  { number:'02', icon:'♡', title:'Orphanage', subtitle:'Support with transparency', text:'Explore organization needs, fundraising campaigns, in-kind requests, and published updates about how support is used.', features:['Campaigns and needs','In-kind pledges','Impact updates'], href:'#orphanage', action:'Explore support', tone:'peach' },
  { number:'03', icon:'☼', title:'Elderly care', subtitle:'Care that keeps families close', text:'Discover elderly-care homes and care providers, with privacy and family involvement at the heart of the experience.', features:['Care-home directory','Caregiver discovery','Family access and updates'], href:'#elderly-care', action:'Explore elderly care', tone:'lavender' },
]
const shared = [
  { icon:'✓', title:'Shared verification', text:'Organization and caregiver review processes.' },
  { icon:'↗', title:'Clear service status', text:'Understand the status of a request or record.' },
  { icon:'⌁', title:'One platform', text:'Common accounts, notifications, and administration.' },
  { icon:'◇', title:'Privacy by role', text:'Sensitive child and resident records stay restricted.' },
]
function HomePage() {
  const hasSession = Boolean(localStorage.getItem('carelife_access_token'))
  return <>
    <SiteNav />
    <main className="home-page">
      <section className="home-hero">
        <div className="home-hero-copy">
          <p className="home-eyebrow"><span /> CARE, CONNECTED</p>
          <h1>Three care journeys. <em>One place to start.</em></h1>
          <p className="home-hero-description">CareLife brings daycare, orphanage support, and elderly care together in one platform. Each module has its own workflow, while shared services make the experience familiar and easier to navigate.</p>
          <div className="home-hero-actions"><a className="home-primary-action" href="#daycare">Explore the modules <span aria-hidden="true">↗</span></a><a className="home-secondary-action" href={hasSession ? '#dashboard' : '#signup'}>{hasSession ? 'Open your workspace' : 'Create an account'}</a></div>
          <div className="home-trust-note"><span className="home-trust-icon" aria-hidden="true">✓</span><span>Choose a module first. CareLife guides you to the relevant services.</span></div>
        </div>
        <div className="home-hero-art" aria-label="Illustration representing connected care"><div className="home-art-orbit home-art-orbit-one" /><div className="home-art-orbit home-art-orbit-two" /><div className="home-art-image-wrap"><img src={heroImage} alt="" /></div><div className="home-floating-note home-floating-note-top"><span className="home-floating-icon">✓</span><span><strong>One shared platform</strong><small>Different needs, clear pathways</small></span></div><div className="home-floating-note home-floating-note-bottom"><span className="home-floating-icon warm">♡</span><span><strong>Care, connected</strong><small>Families and providers</small></span></div></div>
      </section>
      <section className="home-modules" aria-labelledby="home-modules-title"><div className="home-section-heading"><div><p className="home-section-eyebrow">THREE SPECIALIZED MODULES</p><h2 id="home-modules-title">Where would you like to begin?</h2></div><p>Choose the care journey that matches what you need today.</p></div>
        <div className="home-module-grid">{modules.map(item => <article className={'home-module-card '+item.tone} key={item.number}><div className="home-module-card-top"><span className="home-module-icon" aria-hidden="true">{item.icon}</span><span className="home-module-number">{item.number} / MODULE</span></div><p className="home-module-subtitle">{item.subtitle}</p><h3>{item.title}</h3><p className="home-module-description">{item.text}</p><ul>{item.features.map(feature => <li key={feature}>{feature}</li>)}</ul><a className="home-module-link" href={item.href}>{item.action}<span aria-hidden="true">→</span></a></article>)}</div>
      </section>
      <section className="home-how-it-works" aria-labelledby="home-how-title"><div className="home-how-copy"><p className="home-section-eyebrow">HOW CARELIFE FITS TOGETHER</p><h2 id="home-how-title">Separate care needs. Shared foundations.</h2><p>The modules stay focused on their own responsibilities. Common services support identity, verification, communication, and oversight without mixing private records between care domains.</p><a href={hasSession ? '#dashboard' : '#signup'}>{hasSession ? 'Open your workspace' : 'Join CareLife'} <span aria-hidden="true">↗</span></a></div><div className="home-how-steps"><article><span>01</span><div><h3>Choose a module</h3><p>Start with children’s care, orphanage support, or elderly care.</p></div></article><article><span>02</span><div><h3>Follow the right path</h3><p>Families, donors, caregivers, and organizations have different responsibilities.</p></div></article><article><span>03</span><div><h3>Use shared services</h3><p>Verification, status tracking, notifications, and administration support the platform.</p></div></article></div></section>
      <section className="home-shared-services" aria-labelledby="home-shared-title"><div className="home-section-heading"><div><p className="home-section-eyebrow">SHARED ACROSS CARELIFE</p><h2 id="home-shared-title">A consistent experience, wherever you go.</h2></div><p>One product experience with distinct permissions for each role.</p></div><div className="home-shared-grid">{shared.map(item=><article key={item.title}><span aria-hidden="true">{item.icon}</span><h3>{item.title}</h3><p>{item.text}</p></article>)}</div></section>
      <section className="home-bottom-band"><div><p className="home-section-eyebrow">YOUR NEXT STEP</p><h2>Start with the service that matters to you.</h2><p>Browse public information now, or sign in to reach your available workspace.</p></div><a href={hasSession ? '#dashboard' : '#signup'}>{hasSession ? 'Go to workspace' : 'Get started'} <span aria-hidden="true">↗</span></a></section>
      <footer className="home-footer"><a className="home-footer-brand" href="#home"><span>C</span> CareLife</a><p>One platform. Three care journeys. Clearer connections.</p><nav aria-label="Footer navigation"><a href="#daycare">Daycare</a><a href="#orphanage">Orphanage</a><a href="#elderly-care">Elderly care</a></nav></footer>
    </main>
  </>
}
export default HomePage
