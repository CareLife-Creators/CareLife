import SiteNav from '../components/SiteNav'
import { isAdmin, isStaff, roleLabel } from '../lib/roles'
import { useSession } from '../lib/session'
import './OrganizationOnboardingPage.css'

const organizationTypes = [
  { number: '01', title: 'Daycare centers', description: 'Share your center’s details and manage child enrollment and attendance.', color: 'mint' },
  { number: '02', title: 'Children’s homes', description: 'Publish support needs and keep donors informed about your work.', color: 'peach' },
  { number: '03', title: 'Elder-care homes', description: 'Present your care home and coordinate resident services with families.', color: 'lavender' },
]

export default function OrganizationOnboardingPage() {
  const { signedIn, role } = useSession()
  const staff = isStaff(role)
  const admin = isAdmin(role)
  const primaryHref = !signedIn ? '#signup' : admin ? '#organization-approval' : staff ? '#organization-workspace' : '#staff-access'
  const primaryLabel = !signedIn ? 'Create your account' : admin ? 'Review organizations' : staff ? 'Open organization workspace' : 'Request staff access'

  return (
    <>
      <SiteNav />
      <main className="org-onboarding-page">
        <header className="org-onboarding-hero">
          <div className="org-onboarding-hero-copy">
            <p className="org-onboarding-eyebrow">FOR CARE ORGANIZATIONS</p>
            <h1>Bring your care organization onto CareLife.</h1>
            <p>Help families discover your services, understand what you offer, and keep up with the care that matters to them.</p>
            <div className="org-onboarding-actions">
              <a className="org-onboarding-primary" href={primaryHref}>{primaryLabel}<span aria-hidden="true">→</span></a>
              {!signedIn && <a className="org-onboarding-secondary" href="#login">I already have an account</a>}
              {staff && <a className="org-onboarding-secondary" href="#verification">Check review status</a>}
            </div>
            {signedIn && <p className="org-onboarding-role">Signed in as {roleLabel(role)}.</p>}
          </div>
          <div className="org-onboarding-hero-aside" aria-hidden="true">
            <span className="org-orbit org-orbit-one" />
            <span className="org-orbit org-orbit-two" />
            <span className="org-hero-mark">Care<br />that connects<span>✳</span></span>
          </div>
        </header>

        <section className="org-types-section" aria-labelledby="org-types-title">
          <div className="org-section-heading">
            <div><p className="org-onboarding-eyebrow">THREE KINDS OF CARE</p><h2 id="org-types-title">A place for your organization</h2></div>
            <p>Choose the type that reflects the work your organization does.</p>
          </div>
          <div className="org-type-grid">
            {organizationTypes.map((item) => <article className={'org-type-card ' + item.color} key={item.number}>
              <div className="org-type-card-top"><span className="org-type-number">{item.number}</span><span className="org-type-symbol" aria-hidden="true">{item.number === '01' ? '✳' : item.number === '02' ? '♡' : '☼'}</span></div>
              <h3>{item.title}</h3><p>{item.description}</p>
            </article>)}
          </div>
        </section>

        <section className="org-steps-section" aria-labelledby="org-steps-title">
          <div className="org-section-heading">
            <div><p className="org-onboarding-eyebrow">HOW TO GET STARTED</p><h2 id="org-steps-title">Four clear steps</h2></div>
            <p>Staff access and organization verification are separate reviews, so each one has a clear status.</p>
          </div>
          <ol className="org-steps-list">
            <li><span>01</span><div><h3>Create a CareLife account</h3><p>Sign up with your name, work email and phone number, then sign in.</p></div></li>
            <li><span>02</span><div><h3>Request the right staff access</h3><p>Choose daycare, orphanage or care-home staff access. Include your organization and position in the note.</p></div></li>
            <li><span>03</span><div><h3>Register your organization</h3><p>After staff access is approved, open Organization workspace and submit your organization name and license details. If your organization already has an ID, load it there.</p></div></li>
            <li><span>04</span><div><h3>Complete organization review</h3><p>CareLife reviews the organization separately. Its profile can be presented in the relevant directory after approval.</p></div></li>
          </ol>
          <div className="org-review-note"><span aria-hidden="true">i</span><p><strong>Two reviews, two statuses.</strong> Staff access approval gives you the matching workspace. Organization approval is a separate step for the organization’s profile.</p></div>
        </section>

        <section className="org-onboarding-end">
          <div><p className="org-onboarding-eyebrow">READY TO BEGIN?</p><h2>Let families find the care you provide.</h2></div>
          <a className="org-onboarding-primary" href={primaryHref}>{primaryLabel}<span aria-hidden="true">→</span></a>
        </section>
      </main>
      <footer className="org-onboarding-footer"><a href="#home">CareLife</a><span>Care, made closer.</span><a href="#home">Back to CareLife <span aria-hidden="true">↑</span></a></footer>
    </>
  )
}
