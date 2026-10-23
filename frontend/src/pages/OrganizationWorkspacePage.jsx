import { useEffect, useState } from 'react'
import SiteNav from '../components/SiteNav'
import OrganizationSatelliteMap from '../components/OrganizationSatelliteMap'
import { useSession } from '../lib/session'
import { publicOrganizationDescription, publicOrganizationName, publicOrganizationValue } from '../lib/publicDisplay'
import {
  registerOrganization, getOrganizationProfile, updateOrganizationProfile,
  getOrganizationCampaigns, createOrganizationCampaign, getOrganizationNeeds,
  createOrganizationNeed, getOrganizationImpactUpdates, createOrganizationImpactUpdate,
  getOrganizationResidents, createResidentProfile, setResidentConsent, getResidentCheckIns,
  getOrganizationOrphanageChildren, createOrphanageChild,
  getChildOutcomes, createChildOutcome, uploadImpactMedia,
  getOrganizationInKindPledges, updateInKindPledgeStatus,
} from '../api/workspace'
import './Workspace.css'

const ORG_KEY = 'carelife_active_organization_id'
const dateTime = (value) => {
  const date = new Date(value)
  return value && !Number.isNaN(date.getTime()) ? date.toLocaleString() : 'Not recorded'
}

function roleOrganizationType(role) {
  if (role === 'daycare_staff') return 'daycare'
  if (role === 'orphanage_staff') return 'orphanage'
  if (role === 'care_home_staff') return 'elderly_care'
  return 'daycare'
}

export default function OrganizationWorkspacePage() {
  const { role } = useSession()
  const organizationStorageKey = `${ORG_KEY}:${role || 'staff'}`
  const [tab, setTab] = useState('profile')
  const [organizationId, setOrganizationId] = useState(() => {
    try { return localStorage.getItem(`${ORG_KEY}:${role || 'staff'}`) || '' } catch { return '' }
  })
  const [registration, setRegistration] = useState(() => ({
    organization_name: '', organization_type: roleOrganizationType(role), description: '',
    location: '', contact: '', license_number: '', license_expiry_date: '',
    latitude: '', longitude: '',
  }))
  const [profile, setProfile] = useState(null)
  const [profileForm, setProfileForm] = useState({})
  const [campaigns, setCampaigns] = useState([])
  const [needs, setNeeds] = useState([])
  const [updates, setUpdates] = useState([])
  const [pledges, setPledges] = useState([])
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

  async function loadOrganization() {
    if (!organizationId.trim()) {
      setProfile(null); setCampaigns([]); setNeeds([]); setUpdates([]); setResidents([]); setPledges([]); setOrphanageChildren([]); setOutcomes([]); setLoading(false)
      return
    }
    setLoading(true)
    setError('')
    try { localStorage.setItem(organizationStorageKey, organizationId.trim()) } catch { /* Keep the typed ID usable for this session. */ }
    const results = await Promise.allSettled([
      getOrganizationProfile(organizationId.trim()),
      role === 'orphanage_staff' ? getOrganizationCampaigns(organizationId.trim()) : Promise.resolve([]),
      role === 'orphanage_staff' ? getOrganizationNeeds(organizationId.trim()) : Promise.resolve([]),
      role === 'orphanage_staff' ? getOrganizationImpactUpdates(organizationId.trim()) : Promise.resolve([]),
      role === 'care_home_staff' ? getOrganizationResidents(organizationId.trim()) : Promise.resolve([]),
      role === 'orphanage_staff' ? getOrganizationOrphanageChildren(organizationId.trim()) : Promise.resolve([]),
      role === 'orphanage_staff' ? getOrganizationInKindPledges(organizationId.trim()) : Promise.resolve([]),
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
    if (role === 'orphanage_staff' && results[5].status === 'fulfilled') {
      const rows = Array.isArray(results[5].value) ? results[5].value : []
      setOrphanageChildren(rows)
      setSelectedOrphanageChildId((current) => current && rows.some((item) => item.id === current) ? current : (rows[0]?.id || ''))
    }
    if (role === 'orphanage_staff' && results[6].status === 'fulfilled') setPledges(Array.isArray(results[6].value) ? results[6].value : [])
    setLoading(false)
  }

  // eslint-disable-next-line react-hooks/set-state-in-effect -- Load organization data when role, ID, or refresh token changes.
  useEffect(() => { void loadOrganization() }, [refreshKey, role, organizationId])

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
    if (!selectedOrphanageChildId || role !== 'orphanage_staff') { setOutcomes([]); return }
    let cancelled = false
    getChildOutcomes(selectedOrphanageChildId).then((data) => {
      if (!cancelled) setOutcomes(Array.isArray(data) ? data : [])
    }).catch(() => { if (!cancelled) setOutcomes([]) })
    return () => { cancelled = true }
  }, [selectedOrphanageChildId, refreshKey, role])
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

  async function submitRegistration(event) {
    event.preventDefault()
    setBusy('registration'); setError(''); setNotice('')
    try {
      const result = await registerOrganization({ ...registration, organization_name: registration.organization_name.trim(), license_expiry_date: registration.license_expiry_date, latitude: registration.latitude === '' ? null : Number(registration.latitude), longitude: registration.longitude === '' ? null : Number(registration.longitude) })
      const id = result.organization_id || result.id || ''
      if (id) {
        setOrganizationId(id)
        try { localStorage.setItem(organizationStorageKey, id) } catch { /* The displayed ID remains available. */ }
      }
      setNotice(id ? 'Registration submitted. Organization ID saved for this workspace.' : 'Registration submitted. Copy the organization ID from the response if one was returned.')
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Organization registration could not be submitted.')
    } finally { setBusy('') }
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



  const isOrphanage = role === 'orphanage_staff'
  const isCareHome = role === 'care_home_staff'
  const isDaycare = role === 'daycare_staff'
  const workspaceTitle = isDaycare ? 'Daycare operations' : isOrphanage ? 'Children’s home operations' : 'Care-home operations'
  const workspaceDescription = isDaycare
    ? 'Manage your daycare’s public information, enrollment requests, attendance, daily updates and pickup permissions.'
    : isOrphanage
      ? 'Manage children’s home information, private child records, fundraising, item pledges and published impact updates.'
      : 'Manage your care home’s public information, resident records, family consent and wellbeing check-ins.'
  const tabs = [
    ['profile', 'Organization profile'],
    ...(isDaycare ? [['children', 'Children & attendance']] : []),
    ...(isCareHome ? [['residents', 'Residents & check-ins']] : []),
    ...(isOrphanage ? [['children', 'Children & outcomes'], ['support', 'Campaigns & impact'], ['pledges', 'Item pledges']] : []),
  ]

  return (
    <>
      <SiteNav />
      <main className="cw-page">
        <header className="cw-hero">
          <span className="cw-kicker">{workspaceTitle.toUpperCase()}</span>
          <h1>{workspaceTitle}</h1>
          <p>{workspaceDescription}</p>
          <div className="cw-hero-meta"><span>{organizationId ? 'Organization connected' : 'Setup required'}</span><span>{role ? role.replaceAll('_', ' ') : 'Staff'}</span></div>
        </header>
        {!organizationId && <section className="cw-panel">
          <div className="cw-panel-heading"><div><p className="cw-kicker">REGISTER AN ORGANIZATION</p><h2>Submit organization details</h2></div></div>
          <p className="cw-help">The organization type is tied to the signed-in staff role. The backend requires a valid license expiry date and reviews the submission before it appears in public listings.</p>
          <form className="cw-form" onSubmit={submitRegistration}>
            <label>Organization name<input value={registration.organization_name} maxLength={200} onChange={(event) => setRegistration((s) => ({ ...s, organization_name: event.target.value }))} required /></label>
            <label>Organization type<input value={registration.organization_type.replaceAll('_', ' ')} disabled /></label>
            <label>Location<input value={registration.location} maxLength={255} onChange={(event) => setRegistration((s) => ({ ...s, location: event.target.value }))} /></label>
            <label>Map latitude<input type="number" step="any" min="20.5" max="26.8" placeholder="e.g. 23.8103" value={registration.latitude} onChange={(event) => setRegistration((s) => ({ ...s, latitude: event.target.value }))} /></label>
            <label>Map longitude<input type="number" step="any" min="88" max="92.8" placeholder="e.g. 90.4125" value={registration.longitude} onChange={(event) => setRegistration((s) => ({ ...s, longitude: event.target.value }))} /></label>
            <div className="cw-full-field"><strong>Pin your organization on the satellite map</strong><span className="cw-help">Zoom in and click the exact entrance or building location. Your address remains visible in directory listings.</span><OrganizationSatelliteMap value={{ latitude: registration.latitude || null, longitude: registration.longitude || null }} onPick={({ latitude, longitude }) => setRegistration((s) => ({ ...s, latitude: String(latitude), longitude: String(longitude) }))} />{registration.latitude && <small>Selected coordinates: {Number(registration.latitude).toFixed(6)}, {Number(registration.longitude).toFixed(6)}</small>}</div>
            <label>Contact details<input value={registration.contact} maxLength={100} onChange={(event) => setRegistration((s) => ({ ...s, contact: event.target.value }))} /></label>
            <label>License number<input value={registration.license_number} maxLength={100} onChange={(event) => setRegistration((s) => ({ ...s, license_number: event.target.value }))} required /></label>
            <label>License expiry date<input type="date" min={new Date().toISOString().slice(0, 10)} value={registration.license_expiry_date} onChange={(event) => setRegistration((s) => ({ ...s, license_expiry_date: event.target.value }))} required /></label>
            <label className="cw-full-field">Description<textarea rows={3} maxLength={5000} value={registration.description} onChange={(event) => setRegistration((s) => ({ ...s, description: event.target.value }))} /></label>
            <div className="cw-form-actions"><button className="cw-button primary" disabled={busy === 'registration'}>{busy === 'registration' ? 'Submitting…' : 'Submit for verification'}</button></div>
          </form>
        </section>}
        <section className="cw-panel">
          <div className="cw-panel-heading"><div><p className="cw-kicker">WORKSPACE TARGET</p><h2>{organizationId ? 'Load your organization' : 'Have an existing organization ID?'}</h2></div></div>
          <form className="cw-inline-form" onSubmit={(event) => { event.preventDefault(); try { localStorage.setItem(organizationStorageKey, organizationId.trim()) } catch { /* Use current field value. */ } setRefreshKey((value) => value + 1) }}>
            <label>Organization ID<input value={organizationId} onChange={(event) => setOrganizationId(event.target.value)} placeholder="Enter the organization ID returned at registration" required /></label>
            <button className="cw-button primary" disabled={loading}>{loading ? 'Loading…' : 'Load organization'}</button>
            {organizationId && <button type="button" className="cw-button" onClick={() => { setOrganizationId(''); setProfile(null); setCampaigns([]); setNeeds([]); setUpdates([]); setResidents([]); setOrphanageChildren([]); setOutcomes([]); try { localStorage.removeItem(organizationStorageKey) } catch { /* Ignore blocked storage. */ } }}>Clear ID</button>}
          </form>
        </section>
        {error && <div className="cw-alert error" role="alert">{error}</div>}
        {notice && <div className="cw-alert success" role="status">{notice}</div>}
        {organizationId && <nav className="cw-tabs" aria-label="Organization tools">{tabs.map(([id, label]) => <button key={id} type="button" className={tab === id ? 'active' : ''} aria-pressed={tab === id} onClick={() => setTab(id)}>{label}</button>)}<button type="button" className="cw-tabs-action" onClick={() => setRefreshKey((value) => value + 1)} disabled={loading}>Refresh</button></nav>}
        {loading ? <div className="cw-state">Loading organization records…</div> : profile && tab === 'profile' && <section className="cw-panel">
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
        {organizationId && !loading && isDaycare && tab === 'children' && <section className="cw-panel">
          <div className="cw-panel-heading"><div><p className="cw-kicker">DAYCARE OPERATIONS</p><h2>Children, enrollment & attendance</h2></div></div>
          <p className="cw-help">Review enrollment requests, manage attendance and daily updates, and maintain emergency contacts and authorized pickup permissions for children connected to your daycare.</p>
          <a className="cw-button primary" href="#my-children">Open children & attendance <span aria-hidden="true">→</span></a>
        </section>}
        {organizationId && !loading && isCareHome && tab === 'residents' && <section className="cw-panel">
          <div className="cw-panel-heading"><div><p className="cw-kicker">ELDER-CARE RESIDENTS</p><h2>Resident profiles & family check-ins</h2></div><span className="cw-status">{residents.length} profiles</span></div>
          <p className="cw-help">Use the organization ID for this care home. Create private resident records, record a named family representative’s consent, and then record wellbeing check-ins under the backend’s consent rules.</p>
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
                <label>Family representative user ID<input value={consentForm.family_representative_id} onChange={(event) => setConsentForm((s) => ({ ...s, family_representative_id: event.target.value }))} required /></label>
                <label>Consent action<select value={String(consentForm.consent_granted)} onChange={(event) => setConsentForm((s) => ({ ...s, consent_granted: event.target.value === 'true' }))}><option value="true">Grant consent</option><option value="false">Revoke consent</option></select></label>
                <div className="cw-form-actions"><button className="cw-button" disabled={busy === 'consent'}>{busy === 'consent' ? 'Saving…' : 'Save consent'}</button></div>
              </form>
              <p className="cw-help">Family representatives submit wellbeing check-ins from their Family Check-ins page. This staff view is for managing consent and reviewing the check-in history returned for this resident.</p>
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
        {organizationId && !loading && isDaycare && tab === 'profile' && <div className="cw-alert">Daycare child profiles, enrollment, attendance, emergency contacts and pickup permissions are available in <a href="#my-children">Children & attendance</a>.</div>}
      </main>
    </>
  )
}
