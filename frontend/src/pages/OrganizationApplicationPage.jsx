import { useCallback, useEffect, useState } from 'react'
import SiteNav from '../components/SiteNav'
import OrganizationSatelliteMap from '../components/OrganizationSatelliteMap'
import { getMyOrganizationApplications, registerOrganization } from '../api/workspace'
import './OrganizationApplicationPage.css'

const blankApplication = {
  organization_name: '', organization_type: 'daycare', description: '', location: '', contact: '',
  license_number: '', license_expiry_date: '', latitude: '', longitude: '', capacity: '20',
  age_range: '', opening_hours: '', facilities: '', fees: '',
}

const orgTypeName = (type) => ({ daycare: 'Daycare', orphanage: 'Children’s home', elderly_care: 'Elder-care home' }[type] || 'Care organization')

export default function OrganizationApplicationPage() {
  const [form, setForm] = useState(blankApplication)
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  const refreshApplications = useCallback(async () => {
    setLoading(true)
    try { setApplications(await getMyOrganizationApplications()) }
    catch (err) { setError(err instanceof Error ? err.message : 'Your applications could not be loaded.') }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { void refreshApplications() }, [refreshApplications])

  function update(field, value) { setForm((current) => ({ ...current, [field]: value })) }

  async function submit(event) {
    event.preventDefault()
    setSaving(true); setError(''); setNotice('')
    try {
      const result = await registerOrganization({
        ...form,
        capacity: Number(form.capacity),
        latitude: form.latitude === '' ? null : Number(form.latitude),
        longitude: form.longitude === '' ? null : Number(form.longitude),
      })
      setForm(blankApplication)
      setNotice(`Application submitted. Your organization ID is ${result.organization_id}. Save it for your records.`)
      await refreshApplications()
    } catch (err) { setError(err instanceof Error ? err.message : 'The organization application could not be submitted.') }
    finally { setSaving(false) }
  }

  return <>
    <SiteNav />
    <main className="org-application-page">
      <header className="org-application-hero">
        <p className="org-onboarding-eyebrow">FOR CARE ORGANIZATIONS</p>
        <h1>Apply to register your organization</h1>
        <p>Submit your organization’s details for CareLife administrator review. Workspace access is granted after approval.</p>
      </header>

      {error && <div className="org-application-message error" role="alert">{error}</div>}
      {notice && <div className="org-application-message success" role="status">{notice}</div>}

      <section className="org-application-panel" aria-labelledby="org-application-form-title">
        <div className="org-application-section-heading"><p className="org-onboarding-eyebrow">ORGANIZATION APPLICATION</p><h2 id="org-application-form-title">Organization details</h2><p>Use the legal organization name and current license information. Public listing details will be visible only after approval.</p></div>
        <form className="org-application-form" onSubmit={submit}>
          <label>Organization name<input value={form.organization_name} onChange={(e) => update('organization_name', e.target.value)} minLength={2} maxLength={200} required /></label>
          <label>Organization type<select value={form.organization_type} onChange={(e) => update('organization_type', e.target.value)}><option value="daycare">Daycare</option><option value="orphanage">Children’s home</option><option value="elderly_care">Elder-care home</option></select></label>
          <label className="org-application-full">Description<textarea rows={4} maxLength={5000} value={form.description} onChange={(e) => update('description', e.target.value)} placeholder="Describe the care and services your organization provides." /></label>
          <label>Public location/address<input value={form.location} maxLength={255} onChange={(e) => update('location', e.target.value)} required /></label>
          <label>Public contact number or email<input value={form.contact} maxLength={100} onChange={(e) => update('contact', e.target.value)} required /></label>
          <label>License or registration number<input value={form.license_number} maxLength={100} onChange={(e) => update('license_number', e.target.value)} required /></label>
          <label>License expiry date<input type="date" value={form.license_expiry_date} onChange={(e) => update('license_expiry_date', e.target.value)} required /></label>
          <label>Capacity<input type="number" min="0" max="100000" value={form.capacity} onChange={(e) => update('capacity', e.target.value)} required /></label>
          <label>Age range served<input value={form.age_range} maxLength={100} onChange={(e) => update('age_range', e.target.value)} placeholder="For example, 2–5 years" /></label>
          <label>Opening hours<input value={form.opening_hours} maxLength={255} onChange={(e) => update('opening_hours', e.target.value)} /></label>
          <label>Fees and payment information<textarea rows={2} maxLength={2000} value={form.fees} onChange={(e) => update('fees', e.target.value)} /></label>
          <label className="org-application-full">Facilities and services<textarea rows={3} maxLength={5000} value={form.facilities} onChange={(e) => update('facilities', e.target.value)} /></label>
          <div className="org-application-full org-application-map"><strong>Pin the organization entrance on the map</strong><p>Zoom in and select the building entrance. The location is used for the public directory after approval.</p>
            <OrganizationSatelliteMap value={{ latitude: form.latitude || null, longitude: form.longitude || null }} onPick={({ latitude, longitude }) => setForm((current) => ({ ...current, latitude: String(latitude), longitude: String(longitude) }))} />
            <div className="org-application-coordinates"><label>Latitude<input type="number" min="20.5" max="26.8" step="any" value={form.latitude} onChange={(e) => update('latitude', e.target.value)} required /></label><label>Longitude<input type="number" min="88" max="92.8" step="any" value={form.longitude} onChange={(e) => update('longitude', e.target.value)} required /></label></div>
          </div>
          <p className="org-application-privacy org-application-full">Do not include children’s names, resident records, medical details, or other confidential personal information in this application.</p>
          <div className="org-application-submit org-application-full"><button className="org-onboarding-primary" disabled={saving}>{saving ? 'Submitting application…' : 'Submit for administrator review'} <span aria-hidden="true">→</span></button></div>
        </form>
      </section>

      <section className="org-application-panel org-application-status" aria-labelledby="org-application-status-title">
        <div className="org-application-section-heading"><p className="org-onboarding-eyebrow">APPLICATION TRACKING</p><h2 id="org-application-status-title">Your submissions</h2><p>Organization IDs and review statuses are visible only to your signed-in account.</p></div>
        {loading ? <p role="status">Loading your applications…</p> : applications.length === 0 ? <p>You have not submitted an organization application yet.</p> : <div className="org-application-list">{applications.map((item) => <article key={item.organization_id} className="org-application-record"><div><h3>{item.organization_name}</h3><p>{orgTypeName(item.organization_type)} · ID: <code>{item.organization_id}</code></p><small>Submitted {new Date(item.submitted_at).toLocaleDateString()}</small>{item.message && <p>{item.message}</p>}</div><span className={'org-application-status-pill status-' + item.status}>{String(item.status).replaceAll('_', ' ')}</span>{item.status === 'verified' && <a className="org-onboarding-secondary" href="#organization-workspace">Open workspace →</a>}</article>)}</div>}
      </section>
    </main>
  </>
}
