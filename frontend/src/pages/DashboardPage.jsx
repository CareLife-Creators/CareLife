import { useEffect, useState } from 'react'
import SiteNav from '../components/SiteNav'
import { isAdmin, isStaff, roleLabel } from '../lib/roles'
import { useSession } from '../lib/session'
import { getMyCaregiverProfile, getMyAvailability, getMyCaregiverAppointments } from '../api/workspace'
import { getMyChildren, getMyEnrollments, getChildAttendance, getChildDailyUpdates } from '../api/workspace'
import { getMyProfile } from '../api/workspace'
import { getCaregiverDirectory, getElderCareDirectory, getPublicOrganizationMap } from '../api/discovery'
import { getDaycareDirectory } from '../api/daycareDirectory'
import { BANGLADESH_DIVISIONS } from '../data/bangladeshMap'
import AdminWorkspacePage from './AdminWorkspacePage'
import OrganizationSatelliteMap from '../components/OrganizationSatelliteMap'
import useMyProfilePhoto from '../hooks/useMyProfilePhoto'
import './DashboardPage.css'

const modules = [
  { number: '01', icon: '✳', title: 'Daycare', text: 'Daycare discovery and the workflows around enrollment, attendance, and daily updates.', href: '#daycare', action: 'Open daycare', tone: 'mint' },
  { number: '02', icon: '♡', title: 'Orphanage', text: 'Explore fundraising campaigns, in-kind needs, and published impact updates.', href: '#orphanage', action: 'Explore support', tone: 'peach' },
  { number: '03', icon: '☼', title: 'Elderly care', text: 'Find care homes and caregivers, with private family and resident workflows protected by role.', href: '#elderly-care', action: 'Open elderly care', tone: 'lavender' },
]

// Tools differ by role. The backend enforces the same rules.
function toolsFor(role, organizationRoles = []) {
  if (isAdmin(role)) {
    return {
      title: 'Administration',
      intro: 'Review organization applications, caregiver verification, and public impact submissions.',
      links: [
        { href: '#organization-approval', icon: '◇', title: 'Organization approvals', text: 'Review submitted organization verification records.' },
        { href: '#admin-operations', icon: '⌁', title: 'Caregiver review & audit', text: 'Review caregiver submissions and inspect audit events.' },
      ],
    }
  }
  if (organizationRoles.length) {
    const roles = new Set(organizationRoles.map((item) => item.organization_role))
    return {
      title: 'Your organization',
      intro: 'Open a workspace for an organization that approved your access.',
      links: [
        { href: '#organization-workspace', icon: '⌂', title: 'Organization workspace', text: `Manage ${organizationRoles.length === 1 ? 'your approved organization' : `${organizationRoles.length} approved organizations`} and their authorized workflows.` },
        { href: '#verification', icon: '✓', title: 'Verification status', text: 'Review current organization verification and license dates.' },
        ...(roles.has('daycare_staff') ? [{ href: '#organization-workspace', icon: '✳', title: 'Enrollment review', text: 'Review family applications and manage daycare attendance.' }] : []),
        ...(roles.has('orphanage_staff') ? [{ href: '#organization-workspace', icon: '♡', title: 'Children’s home operations', text: 'Manage approved support updates and restricted case workflows.' }] : []),
        ...(roles.has('care_home_staff') ? [{ href: '#organization-workspace', icon: '◷', title: 'Care-home operations', text: 'Manage authorized resident and family-consent workflows.' }] : []),
      ],
    }
  }
  if (isStaff(role)) {
    return {
      title: 'Organization access',
      intro: 'Organization workspaces open after an administrator approves your organization application and membership.',
      links: [
        { href: '#for-organizations', icon: '◇', title: 'Organization access', text: 'Review the registration steps and submit organization details for administrator review.' },
      ],
    }
  }
  if (role === 'independent_caregiver') {
    return {
      title: 'Caregiver workspace',
      intro: 'Keep your profile and availability current, then respond to appointment requests.',
      links: [
        { href: '#caregiver-workspace', icon: '✳', title: 'Caregiver profile & schedule', text: 'Manage your profile, document references and availability.' },
        { href: '#care-bookings', icon: '◷', title: 'Appointments', text: 'Review caregiver appointment requests.' },
      ],
    }
  }
  if (role === 'parent_guardian') {
    return {
      title: 'Family workspace',
      intro: 'Manage child details and follow requests for care.',
      links: [
        { href: '#my-children', icon: '✳', title: 'Children & enrollment', text: 'Manage child profiles, contacts and daycare applications.' },
        { href: '#care-bookings', icon: '◷', title: 'Care bookings', text: 'Request care and follow booking decisions.' },
      ],
    }
  }
  if (role === 'family_representative') {
    return {
      title: 'Family care',
      intro: 'Keep care coordination and booking requests in one place.',
      links: [
        { href: '#care-bookings', icon: '◷', title: 'Care bookings', text: 'Request a service and follow booking status.' },
      ],
    }
  }
  return {
    title: role === 'donor_supporter' ? 'Giving & support' : 'CareLife workspace',
    intro: role === 'donor_supporter' ? 'Review active needs and follow campaign payment records.' : 'Choose the care tools that match how you use CareLife.',
    links: role === 'donor_supporter'
      ? [{ href: '#orphanage-support', icon: '♡', title: 'Support board', text: 'Pledge practical items or start bKash checkout for a campaign.' }]
      : [{ href: '#organization-apply', icon: '◇', title: 'Register an organization', text: 'Submit organization details for administrator review.' }],
  }
}
function DashboardPage() {
  const { email: storedEmail, role, organizationRoles = [] } = useSession()
  const profilePhotoUrl = useMyProfilePhoto()
  const email = storedEmail || 'CareLife member'
  const tools = toolsFor(role, organizationRoles)

  if (role === 'independent_caregiver') return <CaregiverDashboard email={email} />
  if (role === 'parent_guardian') return <FamilyDashboard email={email} />
  if (isAdmin(role)) return <AdminWorkspacePage />

  return <>
    <SiteNav />
    <main className="member-dashboard">
      <header className="member-dashboard-header">
        <div>
          <p className="member-dashboard-eyebrow">YOUR CARELIFE</p>
          <h1>Good to see you.</h1>
          <p className="member-dashboard-intro">Signed in as <strong>{email}</strong>{role ? ' · ' + roleLabel(role) : ''}. Start with a module or open one of your tools.</p>
        </div>
        <div className="member-dashboard-avatar" aria-hidden="true">{profilePhotoUrl ? <img src={profilePhotoUrl} alt="" /> : email.charAt(0).toUpperCase()}</div>
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

const divisionCopy = (value) => String(value || '').toLocaleLowerCase()
const serviceLabels = { daycare: 'Daycare', elderCare: 'Care home', orphanage: 'Children’s home', caregiver: 'Caregiver' }
const serviceRoutes = { daycare: '#daycare-directory', elderCare: '#elderly-care-directory', orphanage: '#orphanage-support', caregiver: '#caregivers' }
function FamilyDashboard({ email }) {
  const [profile, setProfile] = useState(null)
  const [children, setChildren] = useState([])
  const [enrollments, setEnrollments] = useState([])
  const [familyUpdates, setFamilyUpdates] = useState([])
  const [providers, setProviders] = useState([])
  const [loading, setLoading] = useState(true)
  const [directoryError, setDirectoryError] = useState('')
  const [selectedArea, setSelectedArea] = useState('all')
  const [selectedOrganizationId, setSelectedOrganizationId] = useState('')
  const [selectedType, setSelectedType] = useState('all')
  const [search, setSearch] = useState('')

  useEffect(() => {
    let cancelled = false

    async function loadFamilyWorkspace() {
      setLoading(true)
      const [profileResult, childrenResult, enrollmentResult, organizationMapResult, daycareResult, elderCareResult, caregiverResult] = await Promise.allSettled([
        getMyProfile(), getMyChildren(), getMyEnrollments(), getPublicOrganizationMap(),
        getDaycareDirectory(), getElderCareDirectory(), getCaregiverDirectory(),
      ])
      if (cancelled) return

      const familyChildren = childrenResult.status === 'fulfilled' && Array.isArray(childrenResult.value) ? childrenResult.value : []
      const familyEnrollments = enrollmentResult.status === 'fulfilled' && Array.isArray(enrollmentResult.value) ? enrollmentResult.value : []
      const organizationItems = organizationMapResult.status === 'fulfilled' && Array.isArray(organizationMapResult.value) ? organizationMapResult.value : []
      const daycareItems = daycareResult.status === 'fulfilled' && Array.isArray(daycareResult.value) ? daycareResult.value : []
      const elderCareItems = elderCareResult.status === 'fulfilled' && Array.isArray(elderCareResult.value) ? elderCareResult.value : []
      const caregiverItems = caregiverResult.status === 'fulfilled' && Array.isArray(caregiverResult.value) ? caregiverResult.value : []

      setProfile(profileResult.status === 'fulfilled' ? profileResult.value : null)
      setChildren(familyChildren)
      setEnrollments(familyEnrollments)
      const publicOrganizations = new Map()
      const addOrganization = (item, kind) => {
        const id = item.organization_id || item.id
        if (!id) return
        const current = publicOrganizations.get(id) || {}
        publicOrganizations.set(id, {
          ...current,
          ...item,
          id,
          name: item.organization_name || item.name || current.name,
          kind: kind || current.kind || (item.organization_type === 'elderly_care' ? 'elderCare' : item.organization_type === 'orphanage' ? 'orphanage' : 'daycare'),
          latitude: item.latitude ?? current.latitude,
          longitude: item.longitude ?? current.longitude,
          is_verified: true,
        })
      }
      organizationItems.forEach((item) => addOrganization(item))
      daycareItems.forEach((item) => addOrganization(item, 'daycare'))
      elderCareItems.forEach((item) => addOrganization(item, 'elderCare'))

      setProviders([
        ...publicOrganizations.values(),
        ...caregiverItems.map((item) => ({ ...item, id: item.caregiver_id, name: item.full_name || 'Independent caregiver', kind: 'caregiver', description: item.bio || item.service_type || '' })),
      ])
      setDirectoryError([organizationMapResult, daycareResult, elderCareResult, caregiverResult].every((result) => result.status === 'rejected')
        ? 'Care listings could not be loaded right now.' : '')

      if (familyChildren.length) {
        const detailResults = await Promise.all(familyChildren.map(async (child) => {
          const [attendanceResult, updatesResult] = await Promise.allSettled([
            getChildAttendance(child.id), getChildDailyUpdates(child.id),
          ])
          return {
            childName: child.full_name || 'Your child',
            attendance: attendanceResult.status === 'fulfilled' && Array.isArray(attendanceResult.value) ? attendanceResult.value : [],
            updates: updatesResult.status === 'fulfilled' && Array.isArray(updatesResult.value) ? updatesResult.value : [],
          }
        }))
        if (!cancelled) {
          const activity = detailResults.flatMap((item) => [
            ...item.attendance.map((record) => ({ id: 'attendance-' + record.id, childName: item.childName, type: 'attendance', date: record.attendance_date, note: record.check_out_at ? 'Checked out at ' + new Date(record.check_out_at).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) : 'Checked in at ' + new Date(record.check_in_at).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) })),
            ...item.updates.map((record) => ({ id: 'update-' + record.id, childName: item.childName, type: 'update', date: record.update_date, note: record.notes })),
          ]).sort((a, b) => new Date(b.date || 0) - new Date(a.date || 0))
          setFamilyUpdates(activity.slice(0, 4))
        }
      }
      setLoading(false)
    }

    void loadFamilyWorkspace()
    return () => { cancelled = true }
  }, [])

  const pendingEnrollments = enrollments.filter((item) => ['pending', 'requested'].includes(String(item.status || '').toLowerCase()))
  const firstName = (profile?.full_name || '').trim().split(/\s+/)[0]
  const areaCounts = BANGLADESH_DIVISIONS.map((division) => ({
    ...division,
    count: providers.filter((provider) => division.aliases.some((alias) => divisionCopy(provider.location).includes(alias))).length,
  }))
  const query = search.trim().toLocaleLowerCase()
  const visibleProviders = providers.filter((provider) => {
    const typeMatches = selectedType === 'all' || provider.kind === selectedType
    const area = areaCounts.find((division) => division.id === selectedArea)
    const areaMatches = !area || area.aliases.some((alias) => divisionCopy(provider.location).includes(alias))
    const queryMatches = !query || [provider.name, provider.location, provider.description].some((value) => String(value || '').toLocaleLowerCase().includes(query))
    return typeMatches && areaMatches && queryMatches
  })

  return <>
    <SiteNav />
    <main className="member-dashboard family-dashboard">
      <header className="family-welcome">
        <div className="family-welcome-copy">
          <p className="member-dashboard-eyebrow">YOUR FAMILY</p>
          <h1>{firstName ? `Welcome back, ${firstName}.` : 'Your family, in one place.'}</h1>
          <p>Follow your child’s care, keep important details close, and find a daycare or care professional near you.</p>
          <div className="family-welcome-actions"><a className="family-primary-action" href="#my-children">Open my child’s care <span aria-hidden="true">→</span></a><button className="family-secondary-action" type="button" onClick={() => document.getElementById('family-discovery')?.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' })}>Find care on the map</button><a className="family-secondary-action" href="#messages">Messages</a></div>
        </div>
        <div className="family-welcome-mark" aria-hidden="true"><span>{(firstName || email).charAt(0).toUpperCase()}</span></div>
      </header>

      <section className="family-overview" aria-label="Family care overview">
        <a href="#my-children" className="family-overview-card"><span>Children</span><strong>{loading ? '…' : children.length}</strong><small>{children.length === 1 ? 'profile in your care' : 'profiles in your care'}</small></a>
        <a href="#my-children" className="family-overview-card"><span>Enrollment requests</span><strong>{loading ? '…' : pendingEnrollments.length}</strong><small>{pendingEnrollments.length ? 'waiting for an update' : 'No requests waiting'}</small></a>
        <a href="#my-children" className="family-overview-card"><span>Latest care notes</span><strong>{loading ? '…' : familyUpdates.length}</strong><small>{familyUpdates.length ? 'updates from your child’s care' : 'Updates appear here when shared'}</small></a>
      </section>

      <section className="family-activity" aria-labelledby="family-activity-title">
        <div className="family-section-heading"><div><p className="member-dashboard-eyebrow">A LITTLE PEACE OF MIND</p><h2 id="family-activity-title">Your child’s latest activity</h2></div><a href="#my-children">Open child details <span aria-hidden="true">→</span></a></div>
        {loading ? <div className="family-activity-empty" role="status">Loading family updates…</div> : familyUpdates.length ? <div className="family-activity-list">{familyUpdates.slice(0, 3).map((item) => <article className="family-activity-item" key={item.id}><span className={item.type === 'attendance' ? 'family-activity-icon attendance' : 'family-activity-icon'} aria-hidden="true">{item.type === 'attendance' ? '✓' : '✳'}</span><div><strong>{item.childName} · {item.type === 'attendance' ? 'Attendance' : 'Daily note'}</strong><p>{item.note}</p></div><time>{item.date ? new Date(item.date).toLocaleDateString([], { month: 'short', day: 'numeric' }) : 'Recent'}</time></article>)}</div> : <div className="family-activity-empty"><div><strong>{children.length ? 'No care updates yet' : 'Start with your child’s profile'}</strong><p>{children.length ? 'Arrival updates and notes shared by the daycare will appear here.' : 'Add a child profile to keep enrollment, safety contacts, and daily updates together.'}</p></div><a className="family-primary-action" href={children.length ? '#daycare-directory' : '#my-children'}>{children.length ? 'Find a daycare' : 'Add child details'} <span aria-hidden="true">→</span></a></div>}
      </section>

      <section className="family-discovery" id="family-discovery" aria-labelledby="family-discovery-title" tabIndex="-1">
        <div className="family-discovery-heading"><div><p className="member-dashboard-eyebrow">FIND CARE NEAR YOU</p><h2 id="family-discovery-title">Explore care on the map</h2><p>Find verified organizations at the locations they submitted, then filter the listings by division.</p></div><span className="family-map-note">Exact pins appear for organizations that submitted map coordinates.</span></div>
        <div className="family-discovery-layout">
          <div className="family-map-panel">
            <div className="family-map-heading"><strong>Care across Bangladesh</strong><span>{providers.length} public listings</span></div>
            <OrganizationSatelliteMap organizations={visibleProviders.filter((provider) => provider.organization_id && provider.latitude != null && provider.longitude != null)} selectedId={selectedOrganizationId} onSelect={setSelectedOrganizationId} />
            <div className="family-area-list" aria-label="Filter listings by division">
              <button type="button" className={selectedArea === 'all' ? 'active' : ''} aria-pressed={selectedArea === 'all'} onClick={() => setSelectedArea('all')}>All Bangladesh <span>{providers.length}</span></button>
              {areaCounts.map((division) => <button type="button" key={division.id} className={selectedArea === division.id ? 'active' : ''} aria-pressed={selectedArea === division.id} onClick={() => setSelectedArea(division.id)}>{division.name} <span>{division.count}</span></button>)}
            </div>
            <p className="family-map-disclaimer">Select an exact pin to zoom to the organization’s submitted location. Satellite imagery is provided by Esri and Maxar.</p>
          </div>

          <div className="family-provider-panel">
            <div className="family-provider-toolbar">
              <label className="visually-hidden" htmlFor="family-provider-search">Search care listings</label>
              <input id="family-provider-search" type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search by name or service" />
              <label className="visually-hidden" htmlFor="family-provider-type">Filter by care type</label>
              <select id="family-provider-type" value={selectedType} onChange={(event) => setSelectedType(event.target.value)}><option value="all">All care</option><option value="daycare">Daycare</option><option value="orphanage">Children’s homes</option><option value="elderCare">Care homes</option><option value="caregiver">Caregivers</option></select>
            </div>
            <div className="family-provider-heading"><h3>{selectedArea === 'all' ? 'Care listings' : `Care in ${areaCounts.find((division) => division.id === selectedArea)?.name}`}</h3><span>{visibleProviders.length} found</span></div>
            {directoryError ? <div className="family-provider-empty" role="alert"><strong>Listings are unavailable</strong><p>{directoryError}</p><a href="#daycare-directory">Open care directories</a></div> : visibleProviders.length ? <div className="family-provider-list">{visibleProviders.slice(0, 7).map((provider) => <article className="family-provider-card" key={provider.kind + provider.id}><span className={'family-provider-type ' + provider.kind}>{serviceLabels[provider.kind]}</span>{provider.kind === 'caregiver' && <small className={provider.is_verified ? 'family-provider-verification verified' : 'family-provider-verification'}>{provider.is_verified ? 'Verified' : 'Not yet verified'}</small>}<h4>{provider.name}</h4><p>{provider.description || 'Public listing'}</p><div className="family-provider-meta"><span>{provider.location || 'Location not listed'}</span>{provider.contact && <a href={'tel:' + String(provider.contact).replace(/[^\d+]/g, '')}>Call</a>}</div><a className="family-provider-link" href={serviceRoutes[provider.kind]}>View listing <span aria-hidden="true">→</span></a></article>)}</div> : <div className="family-provider-empty"><strong>{providers.length ? 'No listings for this search' : 'No public care listings yet'}</strong><p>{providers.length ? 'Try another area or clear the search to see more options.' : 'Published listings will appear here. You can still explore the directory and search another location.'}</p><div><a href="#daycare-directory">Daycare directory</a><a href="#orphanage-support">Children’s homes</a><a href="#elderly-care-directory">Care homes</a><a href="#caregivers">Caregivers</a></div></div>}
          </div>
        </div>
      </section>
    </main>
  </>
}

function CaregiverDashboard({ email }) {
  const [profile, setProfile] = useState(null)
  const [availability, setAvailability] = useState([])
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    Promise.allSettled([getMyCaregiverProfile(), getMyAvailability(), getMyCaregiverAppointments()]).then((results) => {
      if (cancelled) return
      if (results[0].status === 'fulfilled') setProfile(results[0].value)
      if (results[1].status === 'fulfilled') setAvailability(Array.isArray(results[1].value) ? results[1].value : [])
      if (results[2].status === 'fulfilled') setAppointments(Array.isArray(results[2].value) ? results[2].value : [])
      if (results.every((result) => result.status === 'rejected')) setError('Your caregiver overview is temporarily unavailable. Refresh the page to try again.')
      setLoading(false)
    })
    return () => { cancelled = true }
  }, [])

  const pendingAppointments = appointments.filter((item) => item.status === 'pending')
  const verification = String(profile?.verification_status || 'not started').replaceAll('_', ' ')

  return <>
    <SiteNav />
    <main className="member-dashboard caregiver-dashboard">
      <header className="caregiver-overview-hero">
        <div className="caregiver-overview-copy"><p className="member-dashboard-eyebrow">CAREGIVER OVERVIEW</p><h1>Your care practice, at a glance.</h1><p>Welcome back, {profile?.full_name || email}. Keep your profile current, set the times you can work, and stay on top of new appointment requests.</p><a className="caregiver-overview-action" href="#caregiver-workspace">Open caregiver tools <span aria-hidden="true">→</span></a></div>
        <div className="caregiver-overview-orbit" aria-hidden="true"><span>Care<br/>Life</span></div>
      </header>
      {error && <div className="caregiver-overview-error" role="alert">{error}</div>}
      <section className="caregiver-stat-grid" aria-label="Caregiver status">
        <a href="#caregiver-workspace" className="caregiver-stat-card"><span>Profile review</span><strong className={'caregiver-review-status ' + verification.replaceAll(' ', '-')}>{loading ? '…' : verification}</strong><small>{profile?.verification_status === 'approved' ? 'Your profile can appear in the directory.' : 'Complete and submit your profile for review.'}</small></a>
        <a href="#caregiver-workspace" className="caregiver-stat-card"><span>Availability</span><strong>{loading ? '…' : availability.length}</strong><small>Published time slots available to families</small></a>
        <a href="#care-bookings" className="caregiver-stat-card"><span>New requests</span><strong>{loading ? '…' : pendingAppointments.length}</strong><small>{pendingAppointments.length === 1 ? 'Appointment needs' : 'Appointments need'} your response</small></a>
      </section>
      <section className="caregiver-next-section">
        <div className="member-dashboard-section-heading"><div><p className="member-dashboard-eyebrow">YOUR NEXT STEPS</p><h2>Keep things moving</h2></div><a href="#account" className="caregiver-inbox-link">Open messages <span aria-hidden="true">→</span></a></div>
        <div className="caregiver-next-grid">
          <a href="#caregiver-workspace" className="caregiver-next-card"><span className="caregiver-step-icon">01</span><strong>Keep your profile up to date</strong><small>Share your experience and the areas where you provide care.</small><span className="caregiver-card-action">Edit profile <b>→</b></span></a>
          <a href="#caregiver-workspace" className="caregiver-next-card"><span className="caregiver-step-icon">02</span><strong>Set your availability</strong><small>Let families see when you are open to appointment requests.</small><span className="caregiver-card-action">Manage availability <b>→</b></span></a>
          <a href="#care-bookings" className="caregiver-next-card"><span className="caregiver-step-icon">03</span><strong>Respond to families</strong><small>Review incoming appointment requests and follow their status.</small><span className="caregiver-card-action">View appointments <b>→</b></span></a>
        </div>
      </section>
    </main>
  </>
}
export default DashboardPage
