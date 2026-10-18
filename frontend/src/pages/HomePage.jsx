import heroImage from '../assets/hero.png'
import SiteNav from '../components/SiteNav'
import './HomePage.css'

const destinations = [
  {
    icon: '⌕',
    eyebrow: 'PUBLIC DIRECTORY',
    title: 'Find a daycare',
    description: 'Search verified daycare centers and review the public details available for each organization.',
    action: 'Browse directory',
    href: '#daycare-directory',
  },
  {
    icon: '✓',
    eyebrow: 'ORGANIZATION WORKSPACE',
    title: 'Check verification',
    description: 'Signed-in organization members can look up their verification status using their organization ID.',
    action: 'View verification',
    href: '#verification',
    protected: true,
  },
  {
    icon: '◎',
    eyebrow: 'ADMIN WORKSPACE',
    title: 'Review organizations',
    description: 'Authorized CareLife administrators can review pending organization verification requests.',
    action: 'Open approvals',
    href: '#organization-approval',
    protected: true,
  },
]

function HomePage() {
  const hasSession = Boolean(localStorage.getItem('carelife_access_token'))

  return (
    <>
      <SiteNav />
      <main className="home-page">
        <section className="home-hero">
          <div className="home-hero-copy">
            <p className="home-eyebrow"><span /> CARE THAT CONNECTS US</p>
            <h1>Better care starts with <em>clearer connections.</em></h1>
            <p className="home-hero-description">
              CareLife helps families discover care services and gives care
              organizations a clearer way to manage their verification journey.
            </p>
            <div className="home-hero-actions">
              <a className="home-primary-action" href="#daycare-directory">
                Explore daycare <span aria-hidden="true">↗</span>
              </a>
              <a className="home-secondary-action" href={hasSession ? '#dashboard' : '#signup'}>
                {hasSession ? 'Open your dashboard' : 'Create an account'}
              </a>
            </div>
            <div className="home-trust-note">
              <span className="home-trust-icon" aria-hidden="true">✓</span>
              <span>Public listings show organization information intended for discovery.</span>
            </div>
          </div>

          <div className="home-hero-art">
            <div className="home-art-orbit home-art-orbit-one" />
            <div className="home-art-orbit home-art-orbit-two" />
            <div className="home-art-image-wrap">
              <img src={heroImage} alt="" />
            </div>
            <div className="home-floating-note home-floating-note-top">
              <span className="home-floating-icon">✓</span>
              <span><strong>Verified listings</strong><small>Clear public information</small></span>
            </div>
            <div className="home-floating-note home-floating-note-bottom">
              <span className="home-floating-icon warm">♡</span>
              <span><strong>Care, connected</strong><small>Families and providers</small></span>
            </div>
          </div>
        </section>

        <section className="home-destinations" aria-labelledby="home-destinations-title">
          <div className="home-section-heading">
            <div>
              <p className="home-section-eyebrow">START HERE</p>
              <h2 id="home-destinations-title">What would you like to do?</h2>
            </div>
            <p>Choose an available CareLife workspace to continue.</p>
          </div>

          <div className="home-destination-grid">
            {destinations.map((item) => (
              <article className="home-destination-card" key={item.href}>
                <div className="home-destination-card-top">
                  <span className="home-destination-icon" aria-hidden="true">{item.icon}</span>
                  <span className="home-destination-eyebrow">{item.eyebrow}</span>
                </div>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
                <a href={item.protected && !hasSession ? '#login' : item.href}>
                  {item.protected && !hasSession ? 'Sign in to continue' : item.action}
                  <span aria-hidden="true"> →</span>
                </a>
              </article>
            ))}
          </div>
        </section>

        <section className="home-bottom-band">
          <div>
            <p className="home-section-eyebrow">A BETTER EXPERIENCE, STEP BY STEP</p>
            <h2>One welcoming place for care discovery and organization workflows.</h2>
          </div>
          <a href={hasSession ? '#dashboard' : '#signup'}>
            {hasSession ? 'Go to dashboard' : 'Join CareLife'} <span aria-hidden="true">↗</span>
          </a>
        </section>

        <footer className="home-footer">
          <a className="home-footer-brand" href="#home"><span>C</span> CareLife</a>
          <p>Built to make care services easier to discover and manage.</p>
          <a href="#daycare-directory">Browse daycare directory</a>
        </footer>
      </main>
    </>
  )
}

export default HomePage
