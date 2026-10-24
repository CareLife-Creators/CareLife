import { useCallback, useEffect, useMemo, useState } from 'react'
import SiteNav from '../components/SiteNav'
import OrganizationSatelliteMap from '../components/OrganizationSatelliteMap'
import { useSession } from '../lib/session'
import { publicOrganizationDescription, publicOrganizationName, publicOrganizationValue } from '../lib/publicDisplay'
import {
  getOrganizationProfile, updateOrganizationProfile,
  getOrganizationCampaigns, createOrganizationCampaign, getOrganizationNeeds,
  createOrganizationNeed, getOrganizationImpactUpdates, createOrganizationImpactUpdate,
  getOrganizationResidents, createResidentProfile, setResidentConsent, getResidentCheckIns,
  getOrganizationOrphanageChildren, createOrphanageChild,
  getChildOutcomes, createChildOutcome, uploadImpactMedia,
  getOrganizationInKindPledges, updateInKindPledgeStatus,
  getPendingDaycareEnrollments, reviewEnrollment,
} from '../api/workspace'
import './Workspace.css'

const ORG_KEY = 'carelife_active_organization_id'
const dateTime = (value) => {
  const date = new Date(value)
  return value && !Number.isNaN(date.getTime()) ? date.toLocaleString() : 'Not recorded'
}

export default function OrganizationWorkspacePage() {
  const { email, organizationRoles = [] } = useSession()
  const organizationStorageKey = `${ORG_KEY}:${email || 'member'}`
  const approvedOrganizations = useMemo(() => organizationRoles.filter((item) => item?.organization_id && item?.organization_role), [organizationRoles])
  const [tab, setTab] = useState('overview')
  const [organizationId, setOrganizationId] = useState(() => {
    try {
      const saved = localStorage.getItem(`${ORG_KEY}:${email || 'member'}`) || ''
      return organizationRoles.some((item) => item.organization_id === saved) ? saved : (organizationRoles[0]?.organization_id || '')
    } catch { return organizationRoles[0]?.organization_id || '' }
  })
  const workspaceRole = approvedOrganizations.find((item) => item.organization_id === organizationId)?.organization_role || ''

  useEffect(() => {
    if (!approvedOrganizations.some((item) => item.organization_id === organizationId)) {
      const nextId = approvedOrganizations[0]?.organization_id || ''
      setOrganizationId(nextId)
      if (nextId) {
        try { localStorage.setItem(organizationStorageKey, nextId) } catch { /* The approved ID remains selected in memory. */ }
      }
    }
  }, [approvedOrganizations, organizationId, organizationStorageKey])
  const [profile, setProfile] = useState(null)
  const [profileForm, setProfileForm] = useState({})
  const [campaigns, setCampaigns] = useState([])
  const [needs, setNeeds] = useState([])
  const [updates, setUpdates] = useState([])
  const [pledges, setPledges] = useState([])
  const [daycareEnrollments, setDaycareEnrollments] = useState([])
  const [residents, setResidents] = useState([])
  const [selectedResidentId, setSelectedResidentId] = useState('')
  const [checkIns, setCheckIns] = useState([])
  const [orphanageChildren, setOrphanageChildren] = useState([])
  const [selectedOrphanageChildId, setSelectedOrphanageChildId] = useState('')
  const [outcomes, setOutcomes] = useState([])
  const [orphanageChildForm, setOrphanageChildForm] = useState({ full_name: '', date_of_birth: '', gender: '', allergies: '', medical_notes: '' })
  const [outcomeForm, setOutcomeForm] = useState({ outcome_type: 'adoption', outcome_date: '', notes: '' })
  const [mediaUpdateId, setMediaUpdateId] = useState('')
  const [mediaFile, setMediaFile] = useState(null)
  const [residentForm, setResidentForm] = useState({ full_name: '', preferred_name: '', date_of_birth: '', room_number: '', emergency_contact_name: '', emergency_contact_phone: '' })
  const [consentForm, setConsentForm] = useState({ family_representative_id: '', consent_granted: true })
  const [campaignForm, setCampaignForm] = useState({ title: '', description: '', target_amount: '', currency: 'BDT' })
  const [needForm, setNeedForm] = useState({ title: '', description: '', category: '', need_type: 'in_kind', target_quantity: '', unit: '' })
  const [impactForm, setImpactForm] = useState({ title: '', content: '' })
  const [loading, setLoading] = useState(false)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [refreshKey, setRefreshKey] = useState(0)

  const loadOrganization = useCallback(async () => {
    if (!organizationId.trim()) {
      setProfile(null); setCampaigns([]); setNeeds([]); setUpdates([]); setResidents([]); setPledges([]); setDaycareEnrollments([]); setOrphanageChildren([]); setOutcomes([]); setLoading(false)
      return
    }
    setLoading(true)
    setError('')
    if (!approvedOrganizations.some((item) => item.organization_id === organizationId.trim())) {
      setProfile(null); setCampaigns([]); setNeeds([]); setUpdates([]); setResidents([]); setPledges([]); setDaycareEnrollments([]); setOrphanageChildren([]); setOutcomes([]); setLoading(false)
      setError('This account has no approved access to that organization.')
      return
    }
    try { localStorage.setItem(organizationStorageKey, organizationId.trim()) } catch { /* Current approved selection remains in memory. */ }
    const results = await Promise.allSettled([
      getOrganizationProfile(organizationId.trim()),
      workspaceRole === 'orphanage_staff' ? getOrganizationCampaigns(organizationId.trim()) : Promise.resolve([]),
      workspaceRole === 'orphanage_staff' ? getOrganizationNeeds(organizationId.trim()) : Promise.resolve([]),
      workspaceRole === 'orphanage_staff' ? getOrganizationImpactUpdates(organizationId.trim()) : Promise.resolve([]),
      workspaceRole === 'care_home_staff' ? getOrganizationResidents(organizationId.trim()) : Promise.resolve([]),
      workspaceRole === 'orphanage_staff' ? getOrganizationOrphanageChildren(organizationId.trim()) : Promise.resolve([]),
      workspaceRole === 'orphanage_staff' ? getOrganizationInKindPledges(organizationId.trim()) : Promise.resolve([]),
      workspaceRole === 'daycare_staff' ? getPendingDaycareEnrollments() : Promise.resolve([]),
    ])
    if (results[0].status === 'fulfilled') {
      setProfile(results[0].value)
      setProfileForm({
        organization_name: publicOrganizationName(results[0].value.organization_name),
        description: publicOrganizationDescription(results[0].value.description, results[0].value.organization_type),
        location: results[0].value.location || '',
        latitude: results[0].value.latitude ?? '', longitude: results[0].value.longitude ?? '',
        contact: results[0].value.contact || '',
        capacity: results[0].value.capacity ?? 0,
        age_range: results[0].value.age_range || '',
        opening_hours: results[0].value.opening_hours || '',
        facilities: publicOrganizationValue(results[0].value.facilities, ''),
        fees: publicOrganizationValue(results[0].value.fees, ''),
      })
    } else setError(results[0].reason instanceof Error ? results[0].reason.message : 'The organization profile could not be loaded.')
    if (results[1].status === 'fulfilled') setCampaigns(Array.isArray(results[1].value) ? results[1].value : [])
    if (results[2].status === 'fulfilled') setNeeds(Array.isArray(results[2].value) ? results[2].value : [])
    if (results[3].status === 'fulfilled') setUpdates(Array.isArray(results[3].value) ? results[3].value : [])
    if (results[4].status === 'fulfilled') {
      const rows = Array.isArray(results[4].value) ? results[4].value : []
      setResidents(rows)
      setSelectedResidentId((current) => current && rows.some((item) => item.id === current) ? current : (rows[0]?.id || ''))
    }
    if (workspaceRole === 'orphanage_staff' && results[5].status === 'fulfilled') {
      const rows = Array.isArray(results[5].value) ? results[5].value : []
      setOrphanageChildren(rows)
      setSelectedOrphanageChildId((current) => current && rows.some((item) => item.id === current) ? current : (rows[0]?.id || ''))
    }
    if (workspaceRole === 'orphanage_staff' && results[6].status === 'fulfilled') setPledges(Array.isArray(results[6].value) ? results[6].value : [])
    if (workspaceRole === 'daycare_staff' && results[7].status === 'fulfilled') {
      setDaycareEnrollments((Array.isArray(results[7].value) ? results[7].value : [])
        .filter((item) => item.daycare_organization_id === organizationId.trim()))
    } else if (workspaceRole === 'daycare_staff') {
      setDaycareEnrollments([])
      setError((current) => current || (results[7].reason instanceof Error ? results[7].reason.message : 'Enrollment requests could not be loaded.'))
    }
    setLoading(false)
  }, [approvedOrganizations, organizationId, organizationStorageKey, workspaceRole])

  // eslint-disable-next-line react-hooks/set-state-in-effect -- Load organization data when role, ID, or refresh token changes.
  useEffect(() => { void loadOrganization() }, [refreshKey, loadOrganization])

  /* eslint-disable react-hooks/set-state-in-effect -- Clear previously selected resident data and fetch the new resident's check-ins. */
  useEffect(() => {
    if (!selectedResidentId) { setCheckIns([]); return }
    let cancelled = false
    getResidentCheckIns(selectedResidentId).then((data) => {
      if (!cancelled) setCheckIns(Array.isArray(data) ? data : [])
    }).catch(() => { if (!cancelled) setCheckIns([]) })
    return () => { cancelled = true }
  }, [selectedResidentId, refreshKey])
  /* eslint-enable react-hooks/set-state-in-effect */

  /* eslint-disable react-hooks/set-state-in-effect -- Clear previous child outcomes when there is no eligible orphanage child selected. */
  useEffect(() => {
    if (!selectedOrphanageChildId || workspaceRole !== 'orphanage_staff') { setOutcomes([]); return }
    let cancelled = false
    getChildOutcomes(selectedOrphanageChildId).then((data) => {
      if (!cancelled) setOutcomes(Array.isArray(data) ? data : [])
    }).catch(() => { if (!cancelled) setOutcomes([]) })
    return () => { cancelled = true }
  }, [selectedOrphanageChildId, refreshKey, workspaceRole])
  /* eslint-enable react-hooks/set-state-in-effect */


  async function updatePledge(pledge, status) {
    setBusy(pledge.id); setError(''); setNotice('')
    try {
      const updated = await updateInKindPledgeStatus(organizationId.trim(), pledge.id, status)
      setPledges((current) => current.map((item) => item.id === updated.id ? updated : item))
      setNotice('Pledge marked ' + status + '.')
    } catch (err) { setError(err instanceof Error ? err.message : 'Pledge status could not be updated.') }
    finally { setBusy('') }
  }

  async function reviewDaycareEnrollment(enrollmentId, status) {
    setBusy(enrollmentId); setError(''); setNotice('')
    try {
      await reviewEnrollment(enrollmentId, status)
      setNotice(`Enrollment request ${status}.`)
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Enrollment request could not be updated.')
    } finally { setBusy('') }
  }

  async function submitOrphanageChild(event) {
    event.preventDefault()
    setBusy('orphanage-child'); setError(''); setNotice('')
    try {
      const child = await createOrphanageChild(organizationId.trim(), {
        full_name: orphanageChildForm.full_name.trim(),
        date_of_birth: orphanageChildForm.date_of_birth,
        gender: orphanageChildForm.gender.trim() || null,
        allergies: orphanageChildForm.allergies.trim() || null,
        medical_notes: orphanageChildForm.medical_notes.trim() || null,
      })
      setOrphanageChildForm({ full_name: '', date_of_birth: '', gender: '', allergies: '', medical_notes: '' })
      setSelectedOrphanageChildId(child.id)
      setNotice('Private orphanage child record created.')
      setRefreshKey((value) => value + 1)
    } catch (err) { setError(err instanceof Error ? err.message : 'Child record could not be created.') }
    finally { setBusy('') }
  }

  async function submitOutcome(event) {
    event.preventDefault()
    if (!selectedOrphanageChildId) return
    setBusy('outcome'); setError(''); setNotice('')
    try {
      await createChildOutcome(selectedOrphanageChildId, {
        outcome_type: outcomeForm.outcome_type,
        outcome_status: 'pending',
        outcome_date: outcomeForm.outcome_date,
        notes: outcomeForm.notes.trim() || null,
      })
      setOutcomeForm({ outcome_type: 'adoption', outcome_date: '', notes: '' })
      setNotice('Outcome record submitted for the selected child.')
      setRefreshKey((value) => value + 1)
    } catch (err) { setError(err instanceof Error ? err.message : 'Outcome record could not be submitted.') }
    finally { setBusy('') }
  }

  async function submitMedia(event) {
    event.preventDefault()
    if (!mediaUpdateId || !mediaFile) {
      setError('Select an impact update and choose a media file first.')
      return
    }
    if (mediaFile.size > 30 * 1024 * 1024) {
      setError('The backend limits an impact media file to 30 MB.')
      return
    }
    setBusy('media'); setError(''); setNotice('')
    try {
      await uploadImpactMedia(organizationId.trim(), mediaUpdateId, mediaFile)
      setMediaFile(null)
      setNotice('Media file attached to the impact update for review.')
      setRefreshKey((value) => value + 1)
    } catch (err) { setError(err instanceof Error ? err.message : 'Impact media upload failed.') }
    finally { setBusy('') }
  }

  async function submitProfile(event) {
    event.preventDefault()
    setBusy('profile'); setError(''); setNotice('')
    const body = {}
    for (const field of ['organization_name', 'description', 'location', 'contact', 'age_range', 'opening_hours', 'facilities', 'fees']) body[field] = String(profileForm[field] || '').trim() || null
    body.latitude = profileForm.latitude === '' ? null : Number(profileForm.latitude)
    body.longitude = profileForm.longitude === '' ? null : Number(profileForm.longitude)
    body.capacity = Number(profileForm.capacity)
    try {
      const result = await updateOrganizationProfile(organizationId.trim(), body)
      setProfile(result)
      setNotice('Organization profile updated.')
      setRefreshKey((value) => value + 1)
    } catch (err) { setError(err instanceof Error ? err.message : 'Organization profile could not be updated.') }
    finally { setBusy('') }
  }

  async function submitCampaign(event) {
    event.preventDefault()
    setBusy('campaign'); setError(''); setNotice('')
    try {
      await createOrganizationCampaign(organizationId.trim(), { ...campaignForm, title: campaignForm.title.trim(), target_amount: campaignForm.target_amount, currency: campaignForm.currency })
      setCampaignForm({ title: '', description: '', target_amount: '', currency: 'BDT' })
      setNotice('Fundraising campaign published.')
      setRefreshKey((value) => value + 1)
    } catch (err) { setError(err instanceof Error ? err.message : 'Campaign could not be created.') }
    finally { setBusy('') }
  }

  async function submitNeed(event) {
    event.preventDefault()
    setBusy('need'); setError(''); setNotice('')
    const body = { title: needForm.title.trim(), description: needForm.description.trim() || null, category: needForm.category.trim(), need_type: needForm.need_type }
    if (needForm.need_type === 'in_kind') { body.target_quantity = needForm.target_quantity; body.unit = needForm.unit.trim() }
    else body.target_amount = needForm.target_amount
    try {
      await createOrganizationNeed(organizationId.trim(), body)
      setNeedForm({ title: '', description: '', category: '', need_type: 'in_kind', target_quantity: '', unit: '' })
      setNotice('Donation need published.')
      setRefreshKey((value) => value + 1)
    } catch (err) { setError(err instanceof Error ? err.message : 'Donation need could not be published.') }
    finally { setBusy('') }
  }

  async function submitImpact(event) {
    event.preventDefault()
    setBusy('impact'); setError(''); setNotice('')
    try {
      const created = await createOrganizationImpactUpdate(organizationId.trim(), { title: impactForm.title.trim(), content: impactForm.content.trim() })
      setImpactForm({ title: '', content: '' })
      setMediaUpdateId(created?.id || '')
      setNotice(created?.id ? 'Impact update submitted for review. Update ID: ' + created.id : 'Impact update submitted to the backend review workflow.')
      setRefreshKey((value) => value + 1)
    } catch (err) { setError(err instanceof Error ? err.message : 'Impact update could not be submitted.') }
    finally { setBusy('') }
  }

  async function submitResident(event) {
    event.preventDefault()
    setBusy('resident'); setError(''); setNotice('')
    const body = { full_name: residentForm.full_name.trim(), preferred_name: residentForm.preferred_name.trim() || null, date_of_birth: residentForm.date_of_birth || null, room_number: residentForm.room_number.trim() || null, emergency_contact_name: residentForm.emergency_contact_name.trim() || null, emergency_contact_phone: residentForm.emergency_contact_phone.trim() || null }
    try {
      const result = await createResidentProfile(organizationId.trim(), body)
      setResidentForm({ full_name: '', preferred_name: '', date_of_birth: '', room_number: '', emergency_contact_name: '', emergency_contact_phone: '' })
      setSelectedResidentId(result.id)
      setNotice('Resident profile created for authorized care-home use.')
      setRefreshKey((value) => value + 1)
    } catch (err) { setError(err instanceof Error ? err.message : 'Resident profile could not be created.') }
    finally { setBusy('') }
  }

  async function submitConsent(event) {
    event.preventDefault()
    setBusy('consent'); setError(''); setNotice('')
    try {
      await setResidentConsent(organizationId.trim(), selectedResidentId, consentForm)
      setNotice(consentForm.consent_granted ? 'Family representative consent recorded.' : 'Consent revocation request recorded.')
    } catch (err) { setError(err instanceof Error ? err.message : 'Consent could not be saved.') }
    finally { setBusy('') }
  }



  const isOrphanage = workspaceRole === 'orphanage_staff'
  const isCareHome = workspaceRole === 'care_home_staff'
  const isDaycare = workspaceRole === 'daycare_staff'
  const workspaceTitle = isDaycare ? 'Daycare operations' : isOrphanage ? 'Children’s home operations' : 'Care-home operations'
  const workspaceDescription = isDaycare
    ? 'Manage your daycare’s public information, enrollment requests, attendance, daily updates and pickup permissions.'
    : isOrphanage
      ? 'Manage children’s home information, private child records, fundraising, item pledges and published impact updates.'
      : 'Manage your care home’s public information, resident records, family consent and wellbeing check-ins.'
  const tabs = [
    ['overview', 'Overview'],
    ['profile', 'Organization profile'],
    ...(isDaycare ? [['enrollments', 'Enrollment review']] : []),
    ...(isCareHome ? [['residents', 'Residents & check-ins']] : []),
    ...(isOrphanage ? [['children', 'Children & outcomes'], ['support', 'Campaigns & impact'], ['pledges', 'Item pledges']] : []),
  ]
  const pendingRequestTrend = Array.from({ length: 7 }, (_, index) => {
    const day = new Date()
    day.setDate(day.getDate() - (6 - index))
    const key = day.toLocaleDateString()
    const count = daycareEnrollments.filter((item) => item.requested_at && new Date(item.requested_at).toLocaleDateString() === key).length
    return { label: day.toLocaleDateString(undefined, { weekday: 'short' }), count }
  })
  const maxRequestCount = Math.max(1, ...pendingRequestTrend.map((item) => item.count))

  return (
    <>
      <SiteNav />
      <main className="cw-page">
        <header className="cw-hero">
          <span className="cw-kicker">{workspaceTitle.toUpperCase()}</span>
          <h1>{workspaceTitle}</h1>
          <p>{workspaceDescription}</p>
          <div className="cw-hero-meta"><span>{organizationId ? 'Approved organization access' : 'Organization access'}</span><span>{workspaceRole ? workspaceRole.replaceAll('_', ' ') : 'Member'}</span></div>
        </header>
        {approvedOrganizations.length > 1 && <section className="cw-panel cw-org-switcher"><label htmlFor="workspace-organization">Organization workspace</label><select id="workspace-organization" value={organizationId} onChange={(event) => { setOrganizationId(event.target.value); setTab('profile') }}>{approvedOrganizations.map((item) => <option key={item.organization_id} value={item.organization_id}>{item.organization_role.replaceAll('_', ' ')} · {item.organization_id}</option>)}</select></section>}
        {!organizationId && <section className="cw-panel"><div className="cw-panel-heading"><div><p className="cw-kicker">ORGANIZATION ACCESS</p><h2>No approved organization workspace yet</h2></div></div><p className="cw-help">Submit organization details from your account dashboard. An administrator must approve the application before private organization tools become available.</p><a className="cw-button primary" href="#organization-apply">Apply for organization access</a></section>}
        {error && <div className="cw-alert error" role="alert">{error}</div>}
        {notice && <div className="cw-alert success" role="status">{notice}</div>}
        {organizationId && <nav className="cw-tabs" aria-label="Organization tools">{tabs.map(([id, label]) => <button key={id} type="button" className={tab === id ? 'active' : ''} aria-pressed={tab === id} onClick={() => setTab(id)}>{label}</button>)}<button type="button" className="cw-tabs-action" onClick={() => setRefreshKey((value) => value + 1)} disabled={loading}>Refresh</button></nav>}
        {loading ? <div className="cw-state">Loading organization records…</div> : profile && tab === 'overview' && <section className="cw-panel cw-org-overview">
          <div className="cw-panel-heading"><div><p className="cw-kicker">{workspaceTitle.toUpperCase()}</p><h2>{profile.organization_name}</h2><p className="cw-help">Live operational summary for this approved organization.</p></div><span className="cw-status">{String(profile.status || '').replaceAll('_', ' ')}</span></div>
          <div className="cw-org-stat-grid">
            {isDaycare && <><article><span>Family applications</span><strong>{daycareEnrollments.length}</strong><small>Awaiting a staff decision</small></article><article><span>Registered capacity</span><strong>{profile.capacity ?? '—'}</strong><small>Places listed in the organization profile</small></article><article><span>Organization status</span><strong>{String(profile.status || 'unknown').replaceAll('_', ' ')}</strong><small>Verification status</small></article></>}
            {isOrphanage && <><article><span>Private case records</span><strong>{orphanageChildren.length}</strong><small>Visible to this approved organization</small></article><article><span>Published campaigns</span><strong>{campaigns.length}</strong><small>Organization fundraising</small></article><article><span>Item pledges</span><strong>{pledges.length}</strong><small>Track receipt and allocation</small></article></>}
            {isCareHome && <><article><span>Resident records</span><strong>{residents.length}</strong><small>Restricted to authorized care-home staff</small></article><article><span>Family check-ins</span><strong>{checkIns.length}</strong><small>For the selected resident</small></article><article><span>Organization status</span><strong>{String(profile.status || 'unknown').replaceAll('_', ' ')}</strong><small>Verification status</small></article></>}
          </div>
          {isDaycare && <div className="cw-org-chart"><div><p className="cw-kicker">ENROLLMENT QUEUE</p><h3>Pending applications received this week</h3><p className="cw-help">Only applications still awaiting review are counted here.</p></div><div className="cw-org-bars" role="img" aria-label={pendingRequestTrend.map((item) => `${item.label}: ${item.count} pending applications`).join('; ')}>{pendingRequestTrend.map((item) => <div className="cw-org-bar-column" key={item.label}><span>{item.count}</span><i style={{ height: `${Math.max(8, (item.count / maxRequestCount) * 100)}%` }} /><small>{item.label}</small></div>)}</div></div>}
          {isDaycare && <div className="cw-org-shortcuts"><a href="#organization-workspace" onClick={() => setTab('enrollments')}>Review family applications →</a><a href="#organization-workspace" onClick={() => setTab('profile')}>Update public profile →</a></div>}
        </section>}
        {loading ? null : profile && tab === 'profile' && <section className="cw-panel">
          <div className="cw-panel-heading"><div><p className="cw-kicker">PUBLIC DETAILS</p><h2>{profile.organization_name}</h2></div><span className="cw-status">{String(profile.status || '').replaceAll('_', ' ')}</span></div>
          <form className="cw-form" onSubmit={submitProfile}>
            <label>Organization name<input value={profileForm.organization_name || ''} maxLength={200} onChange={(event) => setProfileForm((s) => ({ ...s, organization_name: event.target.value }))} required /></label>
            <label>Location<input value={profileForm.location || ''} maxLength={255} onChange={(event) => setProfileForm((s) => ({ ...s, location: event.target.value }))} /></label>
            <label>Map latitude<input type="number" step="any" min="20.5" max="26.8" placeholder="e.g. 23.8103" value={profileForm.latitude ?? ''} onChange={(event) => setProfileForm((s) => ({ ...s, latitude: event.target.value }))} /></label>
            <label>Map longitude<input type="number" step="any" min="88" max="92.8" placeholder="e.g. 90.4125" value={profileForm.longitude ?? ''} onChange={(event) => setProfileForm((s) => ({ ...s, longitude: event.target.value }))} /></label>
            <div className="cw-full-field"><strong>Confirm the exact map location</strong><span className="cw-help">Zoom in and click the building or entrance. These coordinates are shared on public listings only after verification.</span><OrganizationSatelliteMap value={{ latitude: profileForm.latitude || null, longitude: profileForm.longitude || null }} onPick={({ latitude, longitude }) => setProfileForm((s) => ({ ...s, latitude: String(latitude), longitude: String(longitude) }))} />{profileForm.latitude && <small>Selected coordinates: {Number(profileForm.latitude).toFixed(6)}, {Number(profileForm.longitude).toFixed(6)}</small>}</div>
            <label>Public contact<input value={profileForm.contact || ''} maxLength={100} onChange={(event) => setProfileForm((s) => ({ ...s, contact: event.target.value }))} /></label>
            <label>Capacity<input type="number" min="0" value={profileForm.capacity ?? 0} onChange={(event) => setProfileForm((s) => ({ ...s, capacity: event.target.value }))} required /></label>
            <label>Age range<input value={profileForm.age_range || ''} maxLength={100} onChange={(event) => setProfileForm((s) => ({ ...s, age_range: event.target.value }))} /></label>
            <label>Opening hours<input value={profileForm.opening_hours || ''} maxLength={255} onChange={(event) => setProfileForm((s) => ({ ...s, opening_hours: event.target.value }))} /></label>
            <label className="cw-full-field">Description<textarea rows={3} maxLength={5000} value={profileForm.description || ''} onChange={(event) => setProfileForm((s) => ({ ...s, description: event.target.value }))} /></label>
            <label className="cw-full-field">Facilities<textarea rows={3} maxLength={5000} value={profileForm.facilities || ''} onChange={(event) => setProfileForm((s) => ({ ...s, facilities: event.target.value }))} /></label>
            <label className="cw-full-field">Fees<textarea rows={2} maxLength={2000} value={profileForm.fees || ''} onChange={(event) => setProfileForm((s) => ({ ...s, fees: event.target.value }))} /></label>
            <div className="cw-form-actions"><button className="cw-button primary" disabled={busy === 'profile'}>{busy === 'profile' ? 'Saving…' : 'Save organization profile'}</button></div>
          </form>
        </section>}
        {organizationId && !loading && !profile && <div className="cw-alert error" role="status">No editable organization profile was returned for this ID. Confirm the ID and that your staff role has access to it.</div>}
        {organizationId && !loading && isDaycare && tab === 'enrollments' && <section className="cw-panel">
          <div className="cw-panel-heading"><div><p className="cw-kicker">DAYCARE ENROLLMENT</p><h2>Review family applications</h2></div><span className="cw-status">{daycareEnrollments.length} awaiting review</span></div>
          <p className="cw-help">Parents and guardians create and manage child profiles, then send an enrollment request to your daycare. Staff can review requests here; this workspace does not create child profiles.</p>
          {!daycareEnrollments.length ? <div className="cw-empty"><strong>No enrollment requests are waiting.</strong><p>New family applications for this daycare will appear here.</p></div> :
            <div className="cw-record-list">{daycareEnrollments.map((item) => <article className="cw-record" key={item.id}>
              <div className="cw-record-main"><div className="cw-record-title-row"><h3>Family enrollment request</h3><span className="cw-pill warning">{item.status}</span></div>
                <p>Child record reference: {item.child_id}</p><small>Received {dateTime(item.requested_at)} · Request {item.id}</small>
              </div>
              <div className="cw-record-actions">
                {['pending', 'waitlisted'].includes(String(item.status).toLowerCase()) && <>
                  <button type="button" className="cw-button primary" disabled={busy === item.id} onClick={() => void reviewDaycareEnrollment(item.id, 'approved')}>Approve</button>
                  <button type="button" className="cw-button danger" disabled={busy === item.id} onClick={() => void reviewDaycareEnrollment(item.id, 'rejected')}>Reject</button>
                  <button type="button" className="cw-button" disabled={busy === item.id} onClick={() => void reviewDaycareEnrollment(item.id, 'waitlisted')}>Waitlist</button>
                </>}
              </div>
            </article>)}</div>}
          <div className="cw-alert">For a child who already attends, ask their parent or guardian to create or claim the child profile and submit an enrollment request. That keeps the family in control of the child’s information and consent.</div>
        </section>}
        {organizationId && !loading && isCareHome && tab === 'residents' && <section className="cw-panel">
          <div className="cw-panel-heading"><div><p className="cw-kicker">ELDER-CARE RESIDENTS</p><h2>Resident profiles & family check-ins</h2></div><span className="cw-status">{residents.length} profiles</span></div>
          <p className="cw-help">Remote check-in means an authorized family representative can send a brief written wellbeing update from their own account when away from the home. It is not location tracking, live video, or a medical assessment. Create the resident’s private record, verify the family member’s CareLife user ID with them, then grant consent before they can view or submit check-ins. Revoke consent when access should end.</p>
          <form className="cw-form" onSubmit={submitResident}>
            <label>Resident’s full name<input value={residentForm.full_name} maxLength={150} onChange={(event) => setResidentForm((s) => ({ ...s, full_name: event.target.value }))} required /></label>
            <label>Preferred name<input value={residentForm.preferred_name} maxLength={100} onChange={(event) => setResidentForm((s) => ({ ...s, preferred_name: event.target.value }))} /></label>
            <label>Date of birth<input type="date" max={new Date().toISOString().slice(0, 10)} value={residentForm.date_of_birth} onChange={(event) => setResidentForm((s) => ({ ...s, date_of_birth: event.target.value }))} /></label>
            <label>Room number<input value={residentForm.room_number} maxLength={50} onChange={(event) => setResidentForm((s) => ({ ...s, room_number: event.target.value }))} /></label>
            <label>Emergency contact name<input value={residentForm.emergency_contact_name} maxLength={150} onChange={(event) => setResidentForm((s) => ({ ...s, emergency_contact_name: event.target.value }))} /></label>
            <label>Emergency contact phone<input value={residentForm.emergency_contact_phone} maxLength={30} onChange={(event) => setResidentForm((s) => ({ ...s, emergency_contact_phone: event.target.value }))} /></label>
            <div className="cw-form-actions"><button className="cw-button primary" disabled={busy === 'resident'}>{busy === 'resident' ? 'Creating…' : 'Create resident profile'}</button></div>
          </form>
          <div className="cw-detail-grid cw-spaced">
            <section className="cw-subpanel"><h3>Residents</h3>{residents.map((item) => <button type="button" className={'cw-child-card ' + (selectedResidentId === item.id ? 'selected' : '')} key={item.id} onClick={() => setSelectedResidentId(item.id)}><span className="cw-child-avatar">{(item.preferred_name || item.full_name || '?').charAt(0).toUpperCase()}</span><span><strong>{item.preferred_name || item.full_name}</strong><small>{item.room_number ? 'Room ' + item.room_number : 'No room recorded'}</small><small>ID: {item.id}</small></span></button>)}{!residents.length && <p className="cw-muted">No resident profiles returned.</p>}</section>
            <section className="cw-subpanel"><h3>Consent & check-ins</h3>{selectedResidentId ? <>
              <form className="cw-form cw-single-column" onSubmit={submitConsent}>
                <label>Family representative CareLife user ID<input value={consentForm.family_representative_id} onChange={(event) => setConsentForm((s) => ({ ...s, family_representative_id: event.target.value }))} required /><small>Ask the family representative to share the user ID shown in their account profile. Confirm the ID with them before granting access.</small></label>
                <label>Consent action<select value={String(consentForm.consent_granted)} onChange={(event) => setConsentForm((s) => ({ ...s, consent_granted: event.target.value === 'true' }))}><option value="true">Grant consent</option><option value="false">Revoke consent</option></select></label>
                <div className="cw-form-actions"><button className="cw-button" disabled={busy === 'consent'}>{busy === 'consent' ? 'Saving…' : 'Save consent'}</button></div>
              </form>
              <p className="cw-help">Family representatives submit written wellbeing updates from their Family Check-ins page. This staff view manages permission and reviews this resident’s history. “Urgent” is a record label only and does not send an emergency alert; follow your care home’s direct escalation procedure.</p>
              <div className="cw-record-list cw-spaced">{checkIns.map((item) => <article className="cw-mini-record" key={item.id}><strong>{String(item.wellbeing_status || '').replaceAll('_', ' ')}</strong><span>{item.notes || 'No note recorded.'}</span><small>{dateTime(item.recorded_at)}</small></article>)}{!checkIns.length && <p className="cw-muted">No check-ins have been returned for this resident.</p>}</div>
            </> : <p className="cw-muted">Select a resident to manage consent and check-in history.</p>}</section>
          </div>
        </section>}
        {organizationId && !loading && isOrphanage && tab === 'children' && <section className="cw-panel">
          <div className="cw-panel-heading"><div><p className="cw-kicker">PRIVATE CHILD RECORDS</p><h2>Children & outcome records</h2></div><span className="cw-status">{orphanageChildren.length} child records</span></div>
          <p className="cw-help">These records use the orphanage staff API, not the public support board. Keep children’s information within authorized staff workflows. Adoption and guardianship outcomes are recorded for case tracking; CareLife does not make legal decisions.</p>
          <form className="cw-form" onSubmit={submitOrphanageChild}>
            <label>Child’s full name<input value={orphanageChildForm.full_name} maxLength={200} onChange={(event) => setOrphanageChildForm((s) => ({ ...s, full_name: event.target.value }))} required /></label>
            <label>Date of birth<input type="date" max={new Date().toISOString().slice(0, 10)} value={orphanageChildForm.date_of_birth} onChange={(event) => setOrphanageChildForm((s) => ({ ...s, date_of_birth: event.target.value }))} required /></label>
            <label>Gender<input value={orphanageChildForm.gender} maxLength={30} onChange={(event) => setOrphanageChildForm((s) => ({ ...s, gender: event.target.value }))} /></label>
            <label>Allergies<textarea rows={2} maxLength={1000} value={orphanageChildForm.allergies} onChange={(event) => setOrphanageChildForm((s) => ({ ...s, allergies: event.target.value }))} /></label>
            <label className="cw-full-field">Care notes<textarea rows={3} maxLength={2000} value={orphanageChildForm.medical_notes} onChange={(event) => setOrphanageChildForm((s) => ({ ...s, medical_notes: event.target.value }))} /></label>
            <div className="cw-form-actions"><button className="cw-button primary" disabled={busy === 'orphanage-child'}>{busy === 'orphanage-child' ? 'Creating…' : 'Create private child record'}</button></div>
          </form>
          <div className="cw-detail-grid cw-spaced">
            <section className="cw-subpanel"><h3>Orphanage records</h3>{orphanageChildren.map((child) => <button type="button" className={'cw-child-card ' + (selectedOrphanageChildId === child.id ? 'selected' : '')} key={child.id} onClick={() => setSelectedOrphanageChildId(child.id)}><span className="cw-child-avatar">{(child.full_name || '?').charAt(0).toUpperCase()}</span><span><strong>{child.full_name}</strong><small>Born {dateTime(child.date_of_birth)}</small><small>Child ID: {child.id}</small></span></button>)}{!orphanageChildren.length && <p className="cw-muted">No child records were returned for this organization.</p>}</section>
            <section className="cw-subpanel"><h3>Outcomes for selected child</h3>{selectedOrphanageChildId ? <>
              <form className="cw-form cw-single-column" onSubmit={submitOutcome}>
                <label>Outcome type<select value={outcomeForm.outcome_type} onChange={(event) => setOutcomeForm((s) => ({ ...s, outcome_type: event.target.value }))}><option value="adoption">Adoption</option><option value="guardianship">Guardianship</option></select></label>
                <label>Outcome date<input type="date" value={outcomeForm.outcome_date} onChange={(event) => setOutcomeForm((s) => ({ ...s, outcome_date: event.target.value }))} required /></label>
                <label>Case note<textarea rows={3} maxLength={2000} value={outcomeForm.notes} onChange={(event) => setOutcomeForm((s) => ({ ...s, notes: event.target.value }))} /></label>
                <div className="cw-form-actions"><button className="cw-button primary" disabled={busy === 'outcome'}>{busy === 'outcome' ? 'Submitting…' : 'Add outcome record'}</button></div>
              </form>
              <div className="cw-record-list cw-spaced">{outcomes.map((item) => <article className="cw-mini-record" key={item.id}><strong>{String(item.outcome_type || '').replaceAll('_', ' ')} · {String(item.outcome_status || '').replaceAll('_', ' ')}</strong><span>{item.notes || 'No case note recorded.'}</span><small>{dateTime(item.outcome_date)} · Outcome ID: {item.id}</small></article>)}{!outcomes.length && <p className="cw-muted">No outcome history returned for this child.</p>}</div>
            </> : <p className="cw-muted">Choose a child record to view or add outcomes.</p>}</section>
          </div>
        </section>}
        {organizationId && !loading && isOrphanage && tab === 'pledges' && <section className="cw-panel">
          <div className="cw-panel-heading"><div><p className="cw-kicker">DONOR COMMITMENTS</p><h2>In-kind item pledges</h2></div><span className="cw-status">{pledges.length} pledges</span></div>
          <p className="cw-help">Track pledges made against your organization’s published item needs. Mark a pledge as received when the items arrive; then mark it allocated when they have been distributed to their intended need. The backend records who changed the status and when.</p>
          {!pledges.length ? <div className="cw-empty"><strong>No item pledges have been returned.</strong><p>When someone pledges items against your public needs, the organization’s record appears here.</p></div> :
            <div className="cw-record-list">{pledges.map((item) => <article className="cw-record" key={item.id}>
              <div className="cw-record-main"><div className="cw-record-title-row"><h3>{item.need_title}</h3><span className={'cw-pill ' + (item.status === 'allocated' ? 'mint' : item.status === 'received' ? 'warning' : 'neutral')}>{item.status}</span></div>
                <p><strong>{item.quantity} {item.unit}</strong> · Donor ID {item.donor_id}</p>
                {item.notes && <p>{item.notes}</p>}
                <small>Submitted {dateTime(item.created_at)} · Pledge ID: {item.id}</small>
                {item.received_at && <small>Received {dateTime(item.received_at)}</small>}
                {item.allocated_at && <small>Allocated {dateTime(item.allocated_at)}</small>}
              </div>
              <div className="cw-record-actions">
                {item.status === 'pledged' && <button type="button" className="cw-button primary" disabled={busy === item.id} onClick={() => void updatePledge(item, 'received')}>{busy === item.id ? 'Saving…' : 'Mark received'}</button>}
                {item.status === 'received' && <button type="button" className="cw-button primary" disabled={busy === item.id} onClick={() => void updatePledge(item, 'allocated')}>{busy === item.id ? 'Saving…' : 'Mark allocated'}</button>}
              </div>
            </article>)}</div>}
        </section>}
        {organizationId && !loading && isOrphanage && tab === 'support' && <section className="cw-panel">
          <div className="cw-panel-heading"><div><p className="cw-kicker">DONATION CAMPAIGNS</p><h2>Publish a fundraising campaign</h2></div><span className="cw-status">{campaigns.length} campaigns</span></div>
          <form className="cw-form" onSubmit={submitCampaign}>
            <label>Campaign title<input value={campaignForm.title} maxLength={200} onChange={(event) => setCampaignForm((s) => ({ ...s, title: event.target.value }))} required /></label>
            <label>Target amount (BDT)<input type="number" min="0.01" step="0.01" value={campaignForm.target_amount} onChange={(event) => setCampaignForm((s) => ({ ...s, target_amount: event.target.value }))} required /></label>
            <label className="cw-full-field">What this campaign funds<textarea rows={3} maxLength={5000} value={campaignForm.description} onChange={(event) => setCampaignForm((s) => ({ ...s, description: event.target.value }))} /></label>
            <div className="cw-form-actions"><button className="cw-button primary" disabled={busy === 'campaign'}>{busy === 'campaign' ? 'Publishing…' : 'Publish campaign'}</button></div>
          </form>
          <div className="cw-record-list cw-spaced">{campaigns.map((item) => <article className="cw-record" key={item.id}><div className="cw-record-main"><h3>{item.title}</h3><p>{item.description}</p><small>Campaign ID: {item.id} · Target {item.currency || 'BDT'} {item.target_amount}</small></div><span className={'cw-pill ' + (item.is_active ? 'mint' : 'neutral')}>{item.is_active ? 'Active' : 'Inactive'}</span></article>)}</div>
          <div className="cw-divider" />
          <div className="cw-panel-heading"><div><p className="cw-kicker">PRACTICAL NEEDS</p><h2>Publish a donation need</h2></div><span className="cw-status">{needs.length} needs</span></div>
          <form className="cw-form" onSubmit={submitNeed}>
            <label>Need title<input value={needForm.title} maxLength={200} onChange={(event) => setNeedForm((s) => ({ ...s, title: event.target.value }))} required /></label>
            <label>Category<input value={needForm.category} maxLength={100} onChange={(event) => setNeedForm((s) => ({ ...s, category: event.target.value }))} required placeholder="Food, clothing, education" /></label>
            <label>Need type<select value={needForm.need_type} onChange={(event) => setNeedForm((s) => ({ ...s, need_type: event.target.value }))}><option value="in_kind">In-kind items</option><option value="monetary">Money</option></select></label>
            {needForm.need_type === 'in_kind' ? <><label>Target quantity<input type="number" min="0.001" step="0.001" value={needForm.target_quantity} onChange={(event) => setNeedForm((s) => ({ ...s, target_quantity: event.target.value }))} required /></label><label>Unit<input value={needForm.unit} maxLength={50} onChange={(event) => setNeedForm((s) => ({ ...s, unit: event.target.value }))} required placeholder="bags, kg, pieces" /></label></> : <label>Target amount (BDT)<input type="number" min="0.01" step="0.01" value={needForm.target_amount || ''} onChange={(event) => setNeedForm((s) => ({ ...s, target_amount: event.target.value }))} required /></label>}
            <label className="cw-full-field">Details<textarea rows={2} maxLength={5000} value={needForm.description} onChange={(event) => setNeedForm((s) => ({ ...s, description: event.target.value }))} /></label>
            <div className="cw-form-actions"><button className="cw-button primary" disabled={busy === 'need'}>{busy === 'need' ? 'Publishing…' : 'Publish need'}</button></div>
          </form>
          <div className="cw-record-list cw-spaced">{needs.map((item) => <article className="cw-record" key={item.id}><div className="cw-record-main"><h3>{item.title}</h3><p>{item.description}</p><small>{item.category} · {item.need_type} · ID: {item.id}</small></div></article>)}</div>
          <div className="cw-divider" />
          <div className="cw-panel-heading"><div><p className="cw-kicker">PUBLISHED IMPACT</p><h2>Submit an impact update</h2></div><span className="cw-status">{updates.length} updates</span></div>
          <form className="cw-form" onSubmit={submitImpact}>
            <label>Update title<input value={impactForm.title} minLength={3} maxLength={200} onChange={(event) => setImpactForm((s) => ({ ...s, title: event.target.value }))} required /></label>
            <label className="cw-full-field">Update details<textarea rows={4} minLength={10} maxLength={5000} value={impactForm.content} onChange={(event) => setImpactForm((s) => ({ ...s, content: event.target.value }))} required /></label>
            <div className="cw-form-actions"><button className="cw-button primary" disabled={busy === 'impact'}>{busy === 'impact' ? 'Submitting…' : 'Submit impact update'}</button></div>
          </form>
          <div className="cw-record-list cw-spaced">{updates.map((item) => <article className="cw-record" key={item.id}><div className="cw-record-main"><h3>{item.title}</h3><p>{item.content}</p><small>{item.status} · {dateTime(item.published_at || item.created_at)} · ID: {item.id}</small></div><span className="cw-pill warning">{item.status}</span></article>)}</div>
          <div className="cw-divider" />
          <div className="cw-panel-heading"><div><p className="cw-kicker">IMPACT MEDIA</p><h2>Attach a photo or video to an update</h2></div></div>
          <p className="cw-help">Choose an update from this organization. Uploaded media is attached to that impact record and follows the backend moderation workflow. Maximum file size: 30 MB.</p>
          <form className="cw-form" onSubmit={submitMedia}>
            <label>Impact update ID<input value={mediaUpdateId} onChange={(event) => setMediaUpdateId(event.target.value)} maxLength={100} required placeholder="Use the ID returned when the update was submitted" /></label>
            <label>Image or video file<input type="file" accept="image/*,video/*" onChange={(event) => setMediaFile(event.target.files?.[0] || null)} required /></label>
            {mediaFile && <span className="cw-muted">{mediaFile.name} · {(mediaFile.size / (1024 * 1024)).toFixed(2)} MB</span>}
            <div className="cw-form-actions"><button className="cw-button primary" disabled={busy === 'media' || !updates.length}>{busy === 'media' ? 'Uploading…' : 'Upload impact media'}</button></div>
          </form>
        </section>}
        {organizationId && !loading && isDaycare && tab === 'profile' && <div className="cw-alert">Families manage child profiles. Use <strong>Enrollment review</strong> to approve or reject applications sent to your daycare.</div>}
      </main>
    </>
  )
}
