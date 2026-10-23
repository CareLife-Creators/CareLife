import { useEffect, useRef, useState } from 'react'
import SiteNav from '../components/SiteNav'
import {
  getMyCaregiverProfile, createMyCaregiverProfile, updateMyCaregiverProfile,
  submitCaregiverDocument, getMyAvailability, createAvailability,
  getMyCaregiverAppointments, decideCaregiverAppointment, startConversation,
} from '../api/workspace'
import './Workspace.css'

const showDate = (value) => {
  const date = new Date(value)
  return value && !Number.isNaN(date.getTime()) ? date.toLocaleString() : 'Time not recorded'
}

export default function CaregiverWorkspacePage({ initialSection = 'profile' }) {
  const [profile, setProfile] = useState(null)
  const [activeSection, setActiveSection] = useState(initialSection)
  const [form, setForm] = useState({ service_type: 'nanny', bio: '', experience_years: '0', location: '' })
  const [document, setDocument] = useState({ document_type: 'identity', file: null })
  const documentInput = useRef(null)
  const [availabilityForm, setAvailabilityForm] = useState({ starts_at: '', ends_at: '' })
  const [availability, setAvailability] = useState([])
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [refreshKey, setRefreshKey] = useState(0)

  async function load() {
    setLoading(true)
    setError('')
    const results = await Promise.allSettled([getMyCaregiverProfile(), getMyAvailability(), getMyCaregiverAppointments()])
    if (results[0].status === 'fulfilled') {
      const current = results[0].value
      setProfile(current)
      setForm({
        service_type: current.service_type || 'nanny',
        bio: current.bio || '',
        experience_years: String(current.experience_years ?? 0),
        location: current.location || '',
      })
    } else if (results[0].reason?.status !== 404) {
      setError(results[0].reason instanceof Error ? results[0].reason.message : 'Caregiver profile could not be loaded.')
    }
    if (results[1].status === 'fulfilled') setAvailability(Array.isArray(results[1].value) ? results[1].value : [])
    if (results[2].status === 'fulfilled') setAppointments(Array.isArray(results[2].value) ? results[2].value : [])
    if (results.every((item) => item.status === 'rejected')) setError('Caregiver workspace could not reach the backend. Check your sign-in and retry.')
    setLoading(false)
  }

  // eslint-disable-next-line react-hooks/set-state-in-effect -- Fetch remote caregiver profile, availability, and appointment data.
  useEffect(() => { void load() }, [refreshKey])

  async function saveProfile(event) {
    event.preventDefault()
    setBusy('profile')
    setError('')
    setNotice('')
    const payload = {
      service_type: form.service_type,
      bio: form.bio.trim() || null,
      experience_years: Number(form.experience_years),
      location: form.location.trim() || null,
    }
    try {
      const result = profile ? await updateMyCaregiverProfile(payload) : await createMyCaregiverProfile(payload)
      setProfile(result)
      setNotice(profile ? 'Caregiver profile updated.' : 'Caregiver profile created. Add verification documents when you are ready for review.')
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Caregiver profile could not be saved.')
    } finally {
      setBusy('')
    }
  }

  async function submitDocument(event) {
    event.preventDefault()
    setBusy('document')
    setError('')
    setNotice('')
    try {
      if (!document.file) throw new Error('Choose a document file to upload.')
      const result = await submitCaregiverDocument({ document_type: document.document_type, file: document.file })
      setProfile(result)
      setDocument((current) => ({ ...current, file: null }))
      if (documentInput.current) documentInput.current.value = ''
      setNotice('Document uploaded to your private verification record.')
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Document could not be uploaded.')
    } finally {
      setBusy('')
    }
  }

  async function submitAvailability(event) {
    event.preventDefault()
    setBusy('availability')
    setError('')
    setNotice('')
    if (new Date(availabilityForm.ends_at) <= new Date(availabilityForm.starts_at)) {
      setError('The end time must be later than the start time.')
      setBusy('')
      return
    }
    try {
      await createAvailability({
        starts_at: new Date(availabilityForm.starts_at).toISOString(),
        ends_at: new Date(availabilityForm.ends_at).toISOString(),
      })
      setAvailabilityForm({ starts_at: '', ends_at: '' })
      setNotice('Availability published.')
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Availability could not be published.')
    } finally {
      setBusy('')
    }
  }

  async function decideAppointment(id, status) {
    setBusy(id)
    setError('')
    setNotice('')
    try {
      await decideCaregiverAppointment(id, status)
      setNotice('Appointment marked ' + status + '.')
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Appointment decision could not be saved.')
    } finally {
      setBusy('')
    }
  }

  async function messageRequester(userId) {
    setBusy('message:' + userId)
    setError('')
    try {
      await startConversation(userId)
      window.sessionStorage.setItem('carelife_account_tab', 'messages')
      window.location.hash = '#account'
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not open this conversation.')
    } finally {
      setBusy('')
    }
  }

  return (
    <>
      <SiteNav />
      <main className="cw-page">
        <header className="cw-hero">
          <span className="cw-kicker">INDEPENDENT CAREGIVER</span>
          <h1>Your care practice, in one place.</h1>
          <p>Your professional profile, verification, working hours and appointment requests are managed here. Use the sections below to update one part of your care practice at a time.</p>
          <div className="cw-hero-meta"><span>{profile?.verification_status ? 'Verification: ' + profile.verification_status : 'Profile not submitted'}</span><span>{availability.length} availability slots</span><span>{appointments.length} appointments</span></div>
          <div className="cw-caregiver-hero-actions"><button type="button" onClick={() => setActiveSection('profile')}>Edit profile</button><button type="button" onClick={() => setActiveSection('availability')}>Set availability</button><button type="button" onClick={() => setActiveSection('requests')}>View requests {appointments.filter((item) => item.status === 'pending').length > 0 && <i>{appointments.filter((item) => item.status === 'pending').length}</i>}</button></div>
        </header>
        {error && <div className="cw-alert error" role="alert">{error}</div>}
        {notice && <div className="cw-alert success" role="status">{notice}</div>}
        {loading ? <div className="cw-state">Loading caregiver profile and appointments…</div> : <>
          <nav className="cw-tabs cw-caregiver-tabs" aria-label="Caregiver workspace sections">
            {[['profile', 'Profile & services'], ['verification', 'Verification'], ['availability', 'Availability'], ['requests', 'Appointment requests']].map(([id, label]) => <button key={id} type="button" className={activeSection === id ? 'active' : ''} aria-pressed={activeSection === id} onClick={() => setActiveSection(id)}>{label}{id === 'requests' && appointments.filter((item) => item.status === 'pending').length > 0 && <i>{appointments.filter((item) => item.status === 'pending').length}</i>}</button>)}
          </nav>
          {activeSection === 'profile' && <section className="cw-panel">
            <div className="cw-panel-heading"><div><p className="cw-kicker">PUBLIC PROFILE</p><h2>{profile ? 'Your caregiver details' : 'Create your caregiver profile'}</h2></div>{profile?.verification_status && <span className="cw-status">{profile.verification_status}</span>}</div>
            <form className="cw-form" onSubmit={saveProfile}>
              <label>Care service<select value={form.service_type} onChange={(event) => setForm((s) => ({ ...s, service_type: event.target.value }))}><option value="nanny">Nanny / child care</option><option value="elder_care_giver">Elder care</option></select></label>
              <label>Years of experience<input type="number" min="0" max="60" value={form.experience_years} onChange={(event) => setForm((s) => ({ ...s, experience_years: event.target.value }))} required /></label>
              <label>Location<input maxLength={255} value={form.location} onChange={(event) => setForm((s) => ({ ...s, location: event.target.value }))} placeholder="City or area" /></label>
              <label className="cw-full-field">Profile biography<textarea rows={4} maxLength={2000} value={form.bio} onChange={(event) => setForm((s) => ({ ...s, bio: event.target.value }))} placeholder="Describe your experience, services and availability." /></label>
              <div className="cw-form-actions"><button className="cw-button primary" disabled={busy === 'profile'}>{busy === 'profile' ? 'Saving…' : profile ? 'Update profile' : 'Create profile'}</button></div>
            </form>
            {profile?.review_message && <div className="cw-alert">{profile.review_message}</div>}
          </section>}

          {activeSection === 'verification' && <section className="cw-panel">
            <div className="cw-panel-heading"><div><p className="cw-kicker">VERIFICATION</p><h2>Verification documents</h2></div></div>
            <p className="cw-help">Upload a clear scan or photo of your identity or qualification document. Files are private to you and the CareLife review team.</p>
            <form className="cw-form" onSubmit={submitDocument}>
              <label>Document type<select value={document.document_type} onChange={(event) => setDocument((s) => ({ ...s, document_type: event.target.value }))}><option value="identity">Identity</option><option value="qualification">Qualification</option></select></label>
              <label>Choose file<input ref={documentInput} type="file" accept="application/pdf,image/jpeg,image/png,image/webp" onChange={(event) => setDocument((s) => ({ ...s, file: event.target.files?.[0] || null }))} required={!document.file} />{document.file && <small>{document.file.name} · {(document.file.size / 1024 / 1024).toFixed(2)} MB</small>}</label>
              <div className="cw-form-actions"><button className="cw-button primary" disabled={busy === 'document' || !profile || !document.file}>{busy === 'document' ? 'Uploading…' : 'Upload document'}</button><span className="cw-muted">PDF, JPG, PNG or WebP · up to 10 MB</span>{!profile && <span className="cw-muted">Create your profile first.</span>}</div>
            </form>
            {profile?.documents?.length > 0 && <div className="cw-document-list"><strong>Uploaded documents</strong>{profile.documents.map((item) => <span key={item.id}>{item.document_type.replaceAll('_', ' ')} · {item.file_name || item.document_reference} · {showDate(item.submitted_at)}</span>)}</div>}
          </section>}

          {activeSection === 'availability' && <section className="cw-panel">
            <div className="cw-panel-heading"><div><p className="cw-kicker">PUBLISHED SCHEDULE</p><h2>Availability</h2></div><span className="cw-status">{availability.length} slots</span></div>
            <form className="cw-form" onSubmit={submitAvailability}>
              <label>Starts at<input type="datetime-local" value={availabilityForm.starts_at} onChange={(event) => setAvailabilityForm((s) => ({ ...s, starts_at: event.target.value }))} required /></label>
              <label>Ends at<input type="datetime-local" value={availabilityForm.ends_at} onChange={(event) => setAvailabilityForm((s) => ({ ...s, ends_at: event.target.value }))} required /></label>
              <div className="cw-form-actions"><button className="cw-button primary" disabled={busy === 'availability' || !profile}>{busy === 'availability' ? 'Publishing…' : 'Publish availability'}</button></div>
            </form>
            <div className="cw-record-list cw-spaced">{availability.map((slot) => <article className="cw-record" key={slot.id}><div className="cw-record-main"><h3>{showDate(slot.starts_at)}</h3><p>Until {showDate(slot.ends_at)}</p><small>Availability ID: {slot.id}</small></div><span className="cw-pill mint">Published</span></article>)}{!availability.length && <p className="cw-muted">No times published yet.</p>}</div>
          </section>}

          {activeSection === 'requests' && <section className="cw-panel">
            <div className="cw-panel-heading"><div><p className="cw-kicker">APPOINTMENT INBOX</p><h2>Requests for your time</h2></div><button type="button" className="cw-button" onClick={() => setRefreshKey((value) => value + 1)}>Refresh</button></div>
            {!appointments.length ? <div className="cw-empty"><strong>No appointment requests yet.</strong><p>When a family requests one of your published times, the details and response options will appear here.</p></div> : <div className="cw-record-list">{appointments.map((item) => <article className="cw-record" key={item.id}><div className="cw-record-main"><div className="cw-record-title-row"><h3>{showDate(item.starts_at)}</h3><span className={'cw-pill ' + (item.status === 'accepted' ? 'mint' : item.status === 'rejected' ? 'danger' : 'warning')}>{item.status}</span></div><p>Until {showDate(item.ends_at)}</p>{item.message && <p>{item.message}</p>}{item.decision_message && <p>{item.decision_message}</p>}</div><div className="cw-record-actions"><button type="button" className="cw-button" disabled={busy === 'message:' + item.requester_user_id} onClick={() => void messageRequester(item.requester_user_id)}>{busy === 'message:' + item.requester_user_id ? 'Opening…' : 'Message family'}</button>{item.status === 'pending' && <><button type="button" className="cw-button primary" disabled={busy === item.id} onClick={() => void decideAppointment(item.id, 'accepted')}>Accept</button><button type="button" className="cw-button danger" disabled={busy === item.id} onClick={() => void decideAppointment(item.id, 'rejected')}>Decline</button></>}</div></article>)}</div>}
          </section>}
        </>}
      </main>
    </>
  )
}
