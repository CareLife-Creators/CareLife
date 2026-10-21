import { useEffect, useState } from 'react'
import SiteNav from '../components/SiteNav'
import { useSession } from '../lib/session'
import { getDaycareDirectory } from '../api/daycareDirectory'
import {
  getMyChildren, createChild, getMyEnrollments, getPendingDaycareEnrollments,
  createEnrollment, cancelEnrollment, reviewEnrollment, checkOutAttendance, getChildEmergencyContacts, addChildEmergencyContact,
  getChildPickupPersons, addChildPickupPerson, getChildAttendance, getChildDailyUpdates,
  addChildDailyUpdate, checkInEnrollment,
} from '../api/workspace'
import './Workspace.css'

const dateTimeLabel = (value) => {
  const date = new Date(value)
  return value && !Number.isNaN(date.getTime()) ? date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Time not recorded'
}
const dateLabel = (value) => {
  const date = new Date(value)
  return value && !Number.isNaN(date.getTime()) ? date.toLocaleDateString() : 'Date not recorded'
}
const statusTone = (value) => ['approved', 'active', 'completed'].includes(String(value || '').toLowerCase()) ? 'mint' : ['rejected', 'cancelled'].includes(String(value || '').toLowerCase()) ? 'danger' : 'warning'

export default function ChildrenWorkspacePage() {
  const { role } = useSession()
  const [children, setChildren] = useState([])
  const [daycares, setDaycares] = useState([])
  const [enrollments, setEnrollments] = useState([])
  const [pendingEnrollments, setPendingEnrollments] = useState([])
  const [selectedChildId, setSelectedChildId] = useState('')
  const [emergencyContacts, setEmergencyContacts] = useState([])
  const [pickupPersons, setPickupPersons] = useState([])
  const [attendance, setAttendance] = useState([])
  const [dailyUpdates, setDailyUpdates] = useState([])
  const [childForm, setChildForm] = useState({ full_name: '', date_of_birth: '', gender: '', allergies: '', medical_notes: '' })
  const [enrollmentForm, setEnrollmentForm] = useState({ child_id: '', daycare_organization_id: '' })
  const [contactType, setContactType] = useState('emergency')
  const [contactForm, setContactForm] = useState({ full_name: '', relationship_to_child: '', phone: '', email: '', address: '' })
  const [dailyNote, setDailyNote] = useState('')
  const [enrollmentId, setEnrollmentId] = useState('')
  const [loading, setLoading] = useState(true)
  const [detailLoading, setDetailLoading] = useState(false)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [refreshKey, setRefreshKey] = useState(0)

  async function load() {
    setLoading(true)
    setError('')
    const results = await Promise.allSettled([
      getMyChildren(), getDaycareDirectory(), getMyEnrollments(), getPendingDaycareEnrollments(),
    ])
    if (results[0].status === 'fulfilled') {
      const list = Array.isArray(results[0].value) ? results[0].value : []
      setChildren(list)
      setSelectedChildId((current) => current && list.some((item) => item.id === current) ? current : (list[0]?.id || ''))
      setEnrollmentForm((current) => ({ ...current, child_id: current.child_id || list[0]?.id || '' }))
    } else {
      setError(results[0].reason instanceof Error ? results[0].reason.message : 'Child profiles could not be loaded.')
    }
    if (results[1].status === 'fulfilled') setDaycares(Array.isArray(results[1].value) ? results[1].value : [])
    if (results[2].status === 'fulfilled') setEnrollments(Array.isArray(results[2].value) ? results[2].value : [])
    if (results[3].status === 'fulfilled') setPendingEnrollments(Array.isArray(results[3].value) ? results[3].value : [])
    setLoading(false)
  }

  useEffect(() => { void load() }, [refreshKey])

  useEffect(() => {
    if (!selectedChildId) {
      setEmergencyContacts([])
      setPickupPersons([])
      setAttendance([])
      setDailyUpdates([])
      return
    }
    let cancelled = false
    setDetailLoading(true)
    Promise.allSettled([
      getChildEmergencyContacts(selectedChildId),
      getChildPickupPersons(selectedChildId),
      getChildAttendance(selectedChildId),
      getChildDailyUpdates(selectedChildId),
    ]).then((results) => {
      if (cancelled) return
      setEmergencyContacts(results[0].status === 'fulfilled' && Array.isArray(results[0].value) ? results[0].value : [])
      setPickupPersons(results[1].status === 'fulfilled' && Array.isArray(results[1].value) ? results[1].value : [])
      setAttendance(results[2].status === 'fulfilled' && Array.isArray(results[2].value) ? results[2].value : [])
      setDailyUpdates(results[3].status === 'fulfilled' && Array.isArray(results[3].value) ? results[3].value : [])
    }).finally(() => { if (!cancelled) setDetailLoading(false) })
    return () => { cancelled = true }
  }, [selectedChildId, refreshKey])

  async function submitChild(event) {
    event.preventDefault()
    setBusy('child')
    setError('')
    setNotice('')
    try {
      const created = await createChild({
        full_name: childForm.full_name.trim(),
        date_of_birth: childForm.date_of_birth,
        gender: childForm.gender.trim() || null,
        allergies: childForm.allergies.trim() || null,
        medical_notes: childForm.medical_notes.trim() || null,
      })
      setChildren((current) => [created, ...current])
      setSelectedChildId(created.id)
      setEnrollmentForm((current) => ({ ...current, child_id: created.id }))
      setChildForm({ full_name: '', date_of_birth: '', gender: '', allergies: '', medical_notes: '' })
      setNotice('Child profile saved. Add emergency contacts and an authorized pickup person below.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Child profile could not be saved.')
    } finally {
      setBusy('')
    }
  }

  async function submitEnrollment(event) {
    event.preventDefault()
    setBusy('enrollment')
    setError('')
    setNotice('')
    try {
      await createEnrollment(enrollmentForm.child_id, enrollmentForm.daycare_organization_id)
      setNotice('Enrollment request submitted to the selected daycare.')
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Enrollment request could not be submitted.')
    } finally {
      setBusy('')
    }
  }

  async function cancelRequest(id) {
    setBusy(id)
    setError('')
    try {
      await cancelEnrollment(id)
      setNotice('Enrollment request cancelled.')
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The enrollment could not be cancelled.')
    } finally {
      setBusy('')
    }
  }

  async function decideEnrollment(id, status) {
    setBusy(id)
    setError('')
    setNotice('')
    try {
      await reviewEnrollment(id, status)
      setNotice('Enrollment request marked ' + status + '.')
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Enrollment decision could not be saved.')
    } finally {
      setBusy('')
    }
  }

  async function handleCheckOut(attendanceId) {
    setBusy('checkout:' + attendanceId)
    setError('')
    setNotice('')
    try {
      await checkOutAttendance(attendanceId)
      setNotice('Attendance check-out recorded.')
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Attendance check-out could not be recorded.')
    } finally {
      setBusy('')
    }
  }

  async function submitContact(event) {
    event.preventDefault()
    if (!selectedChildId) return
    setBusy('contact')
    setError('')
    setNotice('')
    const payload = {
      full_name: contactForm.full_name.trim(),
      relationship_to_child: contactForm.relationship_to_child.trim(),
      phone: contactForm.phone.trim(),
      email: contactForm.email.trim() || null,
      address: contactForm.address.trim() || null,
    }
    try {
      if (contactType === 'emergency') await addChildEmergencyContact(selectedChildId, payload)
      else await addChildPickupPerson(selectedChildId, payload)
      setContactForm({ full_name: '', relationship_to_child: '', phone: '', email: '', address: '' })
      setNotice(contactType === 'emergency' ? 'Emergency contact added.' : 'Authorized pickup person added.')
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Contact details could not be saved.')
    } finally {
      setBusy('')
    }
  }

  async function submitDailyNote(event) {
    event.preventDefault()
    setBusy('daily')
    setError('')
    try {
      await addChildDailyUpdate(selectedChildId, dailyNote.trim())
      setDailyNote('')
      setNotice('Daily note submitted for this child.')
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Daily note could not be saved.')
    } finally {
      setBusy('')
    }
  }

  async function checkIn(event) {
    event.preventDefault()
    setBusy('checkin')
    setError('')
    try {
      await checkInEnrollment(enrollmentId.trim())
      setEnrollmentId('')
      setNotice('Attendance check-in recorded.')
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Check-in could not be recorded.')
    } finally {
      setBusy('')
    }
  }

  const selectedChild = children.find((item) => item.id === selectedChildId)
  const staffCanRecord = role === 'daycare_staff'

  return (
    <>
      <SiteNav />
      <main className="cw-page">
        <header className="cw-hero">
          <span className="cw-kicker">DAYCARE · CHILD SAFETY</span>
          <h1>Every child, with the right people around them.</h1>
          <p>Keep child details private, send enrollment requests to a daycare, and maintain the emergency contacts and pickup permissions that staff need.</p>
          <div className="cw-hero-meta"><span>{children.length} child profiles</span><span>{enrollments.length} enrollment records</span><span>Private to authorized accounts</span></div>
        </header>
        {error && <div className="cw-alert error" role="alert">{error}</div>}
        {notice && <div className="cw-alert success" role="status">{notice}</div>}
        {loading ? <div className="cw-state">Loading child and enrollment records…</div> : <>
          <section className="cw-panel">
            <div className="cw-panel-heading"><div><p className="cw-kicker">CHILD PROFILES</p><h2>Children in your care</h2></div><button type="button" className="cw-button" onClick={() => setRefreshKey((value) => value + 1)}>Refresh</button></div>
            {!children.length ? <div className="cw-empty"><strong>No child profiles available yet.</strong><p>Create a profile for a child you are authorized to manage. Child details are not shown in public directories.</p></div> :
              <div className="cw-child-grid">{children.map((child) => <button type="button" key={child.id} className={'cw-child-card ' + (selectedChildId === child.id ? 'selected' : '')} onClick={() => setSelectedChildId(child.id)}><span className="cw-child-avatar" aria-hidden="true">{(child.full_name || '?').trim().charAt(0).toUpperCase()}</span><span><strong>{child.full_name}</strong><small>Born {dateLabel(child.date_of_birth)}</small><small>{child.gender || 'Gender not specified'}</small></span><span className="cw-child-arrow">→</span></button>)}</div>}
          </section>
          <section className="cw-panel">
            <div className="cw-panel-heading"><div><p className="cw-kicker">ADD A PROFILE</p><h2>Register a child</h2></div></div>
            <form className="cw-form" onSubmit={submitChild}>
              <label>Child’s full name<input value={childForm.full_name} onChange={(event) => setChildForm((s) => ({ ...s, full_name: event.target.value }))} minLength={2} maxLength={200} required /></label>
              <label>Date of birth<input type="date" value={childForm.date_of_birth} max={new Date().toISOString().slice(0, 10)} onChange={(event) => setChildForm((s) => ({ ...s, date_of_birth: event.target.value }))} required /></label>
              <label>Gender (optional)<input value={childForm.gender} maxLength={30} onChange={(event) => setChildForm((s) => ({ ...s, gender: event.target.value }))} /></label>
              <label>Allergies<textarea rows={2} maxLength={1000} value={childForm.allergies} onChange={(event) => setChildForm((s) => ({ ...s, allergies: event.target.value }))} placeholder="List known allergies for authorized care staff." /></label>
              <label className="cw-full-field">Care notes<textarea rows={3} maxLength={2000} value={childForm.medical_notes} onChange={(event) => setChildForm((s) => ({ ...s, medical_notes: event.target.value }))} placeholder="Information that helps authorized staff care for this child." /></label>
              <div className="cw-form-actions"><button className="cw-button primary" disabled={busy === 'child'}>{busy === 'child' ? 'Saving profile…' : 'Save child profile'}</button></div>
            </form>
          </section>
          <section className="cw-panel">
            <div className="cw-panel-heading"><div><p className="cw-kicker">DAYCARE APPLICATION</p><h2>Request enrollment</h2></div><span className="cw-status">{daycares.length} daycares listed</span></div>
            {!daycares.length ? <div className="cw-empty"><strong>No daycare listings returned.</strong><p>The enrollment form needs a daycare from the verified public directory. Open the daycare directory again when an organization is published.</p><a className="cw-button" href="#daycare-directory">Open daycare directory</a></div> :
              <form className="cw-form" onSubmit={submitEnrollment}>
                <label>Child<select value={enrollmentForm.child_id} onChange={(event) => setEnrollmentForm((s) => ({ ...s, child_id: event.target.value }))} required><option value="">Choose a child</option>{children.map((child) => <option value={child.id} key={child.id}>{child.full_name}</option>)}</select></label>
                <label>Daycare center<select value={enrollmentForm.daycare_organization_id} onChange={(event) => setEnrollmentForm((s) => ({ ...s, daycare_organization_id: event.target.value }))} required><option value="">Choose a daycare</option>{daycares.map((daycare) => <option value={daycare.organization_id} key={daycare.organization_id}>{daycare.organization_name}{daycare.location ? ' — ' + daycare.location : ''}</option>)}</select></label>
                <div className="cw-form-actions"><button className="cw-button primary" disabled={busy === 'enrollment' || !children.length}>{busy === 'enrollment' ? 'Submitting…' : 'Send enrollment request'}</button><a className="cw-button" href="#daycare-directory">View daycare details</a></div>
              </form>}
            <div className="cw-record-list cw-spaced">
              {enrollments.map((item) => <article className="cw-record" key={item.id}><div className="cw-record-main"><div className="cw-record-title-row"><h3>{children.find((child) => child.id === item.child_id)?.full_name || 'Child enrollment'}</h3><span className={'cw-pill ' + statusTone(item.status)}>{item.status}</span></div><p>Daycare ID: {item.daycare_organization_id}</p><small>Requested {dateLabel(item.requested_at)}{item.decision_message ? ' · ' + item.decision_message : ''}</small></div>{['pending', 'approved'].includes(String(item.status).toLowerCase()) && <button type="button" className="cw-button danger" disabled={busy === item.id} onClick={() => void cancelRequest(item.id)}>{busy === item.id ? 'Cancelling…' : 'Cancel request'}</button>}</article>)}
              {!enrollments.length && <p className="cw-muted">No enrollment requests have been returned for this account.</p>}
              {pendingEnrollments.length > 0 && staffCanRecord && <div className="cw-staff-alert"><strong>Daycare review queue</strong><span>{pendingEnrollments.length} enrollment requests are waiting for a decision.</span>{pendingEnrollments.map((item) => <article className="cw-mini-record" key={item.id}><strong>{children.find((child) => child.id === item.child_id)?.full_name || 'Enrollment request'}</strong><span>Daycare {item.daycare_organization_id} · Requested {dateLabel(item.requested_at)}</span><small>Request ID: {item.id}</small><div className="cw-record-actions"><button type="button" className="cw-button primary" disabled={busy === item.id} onClick={() => void decideEnrollment(item.id, 'approved')}>Approve</button><button type="button" className="cw-button danger" disabled={busy === item.id} onClick={() => void decideEnrollment(item.id, 'rejected')}>Reject</button><button type="button" className="cw-button" disabled={busy === item.id} onClick={() => void decideEnrollment(item.id, 'waitlisted')}>Waitlist</button></div></article>)}</div>}
            </div>
          </section>
          {selectedChild && <section className="cw-panel">
            <div className="cw-panel-heading"><div><p className="cw-kicker">SELECTED CHILD</p><h2>{selectedChild.full_name}</h2></div><span className="cw-status">Born {dateLabel(selectedChild.date_of_birth)}</span></div>
            <div className="cw-detail-grid">
              <section className="cw-subpanel"><h3>Emergency contacts</h3>{emergencyContacts.map((item) => <article className="cw-mini-record" key={item.id}><strong>{item.full_name}</strong><span>{item.relationship_to_child} · {item.phone}</span><small>{item.email || 'No email provided'}</small></article>)}{!emergencyContacts.length && <p className="cw-muted">No emergency contacts recorded.</p>}</section>
              <section className="cw-subpanel"><h3>Authorized pickup</h3>{pickupPersons.map((item) => <article className="cw-mini-record" key={item.id}><strong>{item.full_name}</strong><span>{item.relationship_to_child} · {item.phone}</span><small>{item.email || 'No email provided'}</small></article>)}{!pickupPersons.length && <p className="cw-muted">No pickup persons recorded.</p>}</section>
            </div>
            <form className="cw-form cw-contact-form" onSubmit={submitContact}>
              <label>Record type<select value={contactType} onChange={(event) => setContactType(event.target.value)}><option value="emergency">Emergency contact</option><option value="pickup">Authorized pickup person</option></select></label>
              <label>Full name<input value={contactForm.full_name} onChange={(event) => setContactForm((s) => ({ ...s, full_name: event.target.value }))} minLength={2} maxLength={200} required /></label>
              <label>Relationship to child<input value={contactForm.relationship_to_child} onChange={(event) => setContactForm((s) => ({ ...s, relationship_to_child: event.target.value }))} maxLength={100} required /></label>
              <label>Phone number<input type="tel" value={contactForm.phone} onChange={(event) => setContactForm((s) => ({ ...s, phone: event.target.value }))} maxLength={30} required /></label>
              <label>Email (optional)<input type="email" value={contactForm.email} onChange={(event) => setContactForm((s) => ({ ...s, email: event.target.value }))} maxLength={254} /></label>
              <label>Address (optional)<input value={contactForm.address} onChange={(event) => setContactForm((s) => ({ ...s, address: event.target.value }))} maxLength={500} /></label>
              <div className="cw-form-actions"><button className="cw-button primary" disabled={busy === 'contact'}>{busy === 'contact' ? 'Saving…' : contactType === 'emergency' ? 'Add emergency contact' : 'Add pickup person'}</button></div>
            </form>
            <div className="cw-detail-grid cw-spaced">
              <section className="cw-subpanel"><h3>Attendance history</h3>{detailLoading ? <p>Loading attendance…</p> : attendance.map((item) => <article className="cw-mini-record" key={item.id}><strong>{dateLabel(item.attendance_date)}</strong><span>Checked in {dateTimeLabel(item.check_in_at)}{item.check_out_at ? ' · checked out ' + dateTimeLabel(item.check_out_at) : ' · not checked out'}</span>{staffCanRecord && !item.check_out_at && <button type="button" className="cw-button" disabled={busy === 'checkout:' + item.id} onClick={() => void handleCheckOut(item.id)}>{busy === 'checkout:' + item.id ? 'Recording…' : 'Check out'}</button>}</article>)}{!detailLoading && !attendance.length && <p className="cw-muted">No attendance records available for this child.</p>}</section>
              <section className="cw-subpanel"><h3>Daily updates</h3>{detailLoading ? <p>Loading daily notes…</p> : dailyUpdates.map((item) => <article className="cw-mini-record" key={item.id}><strong>{dateLabel(item.update_date)}</strong><span>{item.notes}</span></article>)}{!detailLoading && !dailyUpdates.length && <p className="cw-muted">No daily updates have been recorded.</p>}</section>
            </div>
            {staffCanRecord && <form className="cw-inline-form cw-spaced" onSubmit={submitDailyNote}><label>Record a daily note for {selectedChild.full_name}<textarea rows={2} maxLength={2000} value={dailyNote} onChange={(event) => setDailyNote(event.target.value)} required placeholder="Write a factual care update for the child's authorized contacts." /></label><button className="cw-button primary" disabled={busy === 'daily'}>{busy === 'daily' ? 'Saving…' : 'Publish daily note'}</button></form>}
            {staffCanRecord && <form className="cw-inline-form cw-spaced" onSubmit={checkIn}><label>Record daycare attendance using an enrollment ID<input value={enrollmentId} onChange={(event) => setEnrollmentId(event.target.value)} required placeholder="Enrollment ID from the approved request" /></label><button className="cw-button primary" disabled={busy === 'checkin'}>{busy === 'checkin' ? 'Recording…' : 'Check in child'}</button></form>}
          </section>}
        </>}
      </main>
    </>
  )
}
