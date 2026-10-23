import { useEffect, useState } from 'react'
import SiteNav from '../components/SiteNav'
import { useSession } from '../lib/session'
import { getCaregiverDirectory } from '../api/discovery'
import { getElderCareDirectory } from '../api/discovery'
import {
  getCaregiverAvailability, createCaregiverAppointment, getMyCaregiverAppointments,
  getMyElderCareBookings, createElderCareBooking, cancelElderCareBooking,
  decideElderCareBooking, decideCaregiverAppointment,
} from '../api/workspace'
import { isAdmin } from '../lib/roles'
import './Workspace.css'

const dateTime = (value) => {
  const date = new Date(value)
  return value && !Number.isNaN(date.getTime()) ? date.toLocaleString() : 'Time not provided'
}
const statusTone = (value) => ['approved', 'accepted', 'completed'].includes(String(value || '').toLowerCase()) ? 'mint' : ['rejected', 'cancelled'].includes(String(value || '').toLowerCase()) ? 'danger' : 'warning'

export default function CareBookingsPage() {
  const { role } = useSession()
  const [tab, setTab] = useState('caregivers')
  const [caregivers, setCaregivers] = useState([])
  const [careHomes, setCareHomes] = useState([])
  const [appointments, setAppointments] = useState([])
  const [bookings, setBookings] = useState([])
  const [slotsByCaregiver, setSlotsByCaregiver] = useState({})
  const [selectedSlot, setSelectedSlot] = useState('')
  const [selectedProvider, setSelectedProvider] = useState('')
  const [residentId, setResidentId] = useState('')
  const [serviceType, setServiceType] = useState('Home visit')
  const [startsAt, setStartsAt] = useState('')
  const [endsAt, setEndsAt] = useState('')
  const [bookingMessage, setBookingMessage] = useState('')
  const [appointmentMessage, setAppointmentMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [refreshKey, setRefreshKey] = useState(0)

  async function load() {
    setLoading(true)
    setError('')
    const results = await Promise.allSettled([
      getCaregiverDirectory(), getElderCareDirectory(), getMyCaregiverAppointments(), getMyElderCareBookings(),
    ])
    if (results[0].status === 'fulfilled') setCaregivers(Array.isArray(results[0].value) ? results[0].value : [])
    if (results[1].status === 'fulfilled') setCareHomes(Array.isArray(results[1].value) ? results[1].value : [])
    if (results[2].status === 'fulfilled') setAppointments(Array.isArray(results[2].value) ? results[2].value : [])
    if (results[3].status === 'fulfilled') setBookings(Array.isArray(results[3].value) ? results[3].value : [])
    if (results.every((item) => item.status === 'rejected')) setError('Booking data could not be loaded. Sign in with the role that owns these bookings, then retry.')
    setLoading(false)
  }

  useEffect(() => { void load() }, [refreshKey])

  async function loadSlots(caregiverId) {
    setBusy('slots:' + caregiverId)
    setError('')
    try {
      const data = await getCaregiverAvailability(caregiverId)
      setSlotsByCaregiver((current) => ({ ...current, [caregiverId]: Array.isArray(data) ? data : [] }))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Availability could not be loaded.')
    } finally {
      setBusy('')
    }
  }

  async function submitAppointment(event) {
    event.preventDefault()
    setBusy('appointment')
    setError('')
    setNotice('')
    try {
      await createCaregiverAppointment(selectedSlot, appointmentMessage)
      setSelectedSlot('')
      setAppointmentMessage('')
      setNotice('Appointment request sent to the caregiver.')
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Appointment request was not submitted.')
    } finally {
      setBusy('')
    }
  }

  async function submitHomeBooking(event) {
    event.preventDefault()
    setBusy('booking')
    setError('')
    setNotice('')
    const [providerType, providerId] = selectedProvider.split(':')
    if (!residentId.trim() || !providerType || !providerId) {
      setError('Choose a resident ID and a care provider before submitting.')
      setBusy('')
      return
    }
    if (!startsAt || !endsAt || new Date(endsAt) <= new Date(startsAt)) {
      setError('The end time must be later than the start time.')
      setBusy('')
      return
    }
    try {
      await createElderCareBooking({
        resident_id: residentId.trim(),
        provider_type: providerType,
        provider_id: providerId,
        service_type: serviceType.trim(),
        starts_at: new Date(startsAt).toISOString(),
        ends_at: new Date(endsAt).toISOString(),
        message: bookingMessage.trim() || null,
      })
      setNotice('Elder-care booking request submitted.')
      setResidentId('')
      setBookingMessage('')
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Elder-care booking was not submitted.')
    } finally {
      setBusy('')
    }
  }

  async function cancelBooking(id) {
    setBusy(id)
    setError('')
    try {
      await cancelElderCareBooking(id)
      setNotice('Booking cancelled.')
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Booking could not be cancelled.')
    } finally {
      setBusy('')
    }
  }

  async function decideBooking(id, status) {
    setBusy(id)
    setError('')
    try {
      await decideElderCareBooking(id, status)
      setNotice('Booking marked ' + status + '.')
      setRefreshKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Booking decision could not be saved.')
    } finally {
      setBusy('')
    }
  }

  async function decideAppointment(id, status) {
    setBusy(id)
    setError('')
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

  const staffCanReview = role === 'care_home_staff' || isAdmin(role)
  const caregiverCanReview = role === 'independent_caregiver' || isAdmin(role)
  const familyView = role === 'parent_guardian'

  return (
    <>
      <SiteNav />
      <main className={'cw-page ' + (familyView ? 'cw-family-bookings-page' : '')}>
        <header className={'cw-hero ' + (familyView ? 'cw-family-bookings-hero' : '')}>
          <span className="cw-kicker">{familyView ? 'CARE FOR YOUR FAMILY' : 'ELDERLY CARE · APPOINTMENTS'}</span>
          <h1>{familyView ? 'Find a care professional and manage requests.' : 'Arrange care around the person, not the paperwork.'}</h1>
          <p>{familyView ? 'See available caregiver times and follow your appointment requests. Daycare applications and child updates are in My children.' : 'Request an independent caregiver, choose an available time, or submit an elder-care booking with a resident reference and a named provider.'}</p>
          {familyView && <div className="cw-carebooking-shortcuts"><a href="#daycare-directory">Find a daycare <span aria-hidden="true">→</span></a><a href="#my-children">My child’s care <span aria-hidden="true">→</span></a></div>}
          <div className="cw-hero-meta"><span>{caregivers.length} caregiver profiles</span><span>{careHomes.length} care homes listed</span><span>{appointments.length + bookings.length} booking records</span></div>
        </header>
        <nav className="cw-tabs" aria-label="Care booking sections">
          <button type="button" className={tab === 'caregivers' ? 'active' : ''} aria-pressed={tab === 'caregivers'} onClick={() => setTab('caregivers')}>{familyView ? 'Find a caregiver' : 'Caregiver availability'}</button>
          {!familyView && <button type="button" className={tab === 'home-booking' ? 'active' : ''} aria-pressed={tab === 'home-booking'} onClick={() => setTab('home-booking')}>Care-home booking</button>}
          <button type="button" className={tab === 'my-bookings' ? 'active' : ''} aria-pressed={tab === 'my-bookings'} onClick={() => setTab('my-bookings')}>My bookings</button>
        </nav>
        {error && <div className="cw-alert error" role="alert">{error}</div>}
        {notice && <div className="cw-alert success" role="status">{notice}</div>}
        {loading ? <div className="cw-state">Loading providers and bookings…</div> : <>
          {tab === 'caregivers' && <section className="cw-panel">
            <div className="cw-panel-heading"><div><p className="cw-kicker">INDEPENDENT CAREGIVERS</p><h2>Available care</h2></div><span className="cw-status">{caregivers.length} profiles</span></div>
            {!caregivers.length ? <div className="cw-empty"><strong>No public caregiver profiles are available yet.</strong><p>When care professionals publish their availability, you can compare times and send a request here.</p><div className="cw-carebooking-empty-links"><a href="#caregivers" className="cw-button">Browse caregivers</a>{familyView && <a href="#daycare-directory" className="cw-button">Find a daycare</a>}</div></div> :
              <div className="cw-provider-grid">{caregivers.map((caregiver) => <article className="cw-provider-card" key={caregiver.caregiver_id}>
                <div className="cw-provider-top"><span className="cw-provider-avatar" aria-hidden="true">{(caregiver.full_name || 'C').trim().charAt(0).toUpperCase()}</span><span className="cw-pill mint">{String(caregiver.service_type || '').replaceAll('_', ' ')}</span></div>
                <h3>{caregiver.full_name || 'Independent caregiver'}</h3><p>{caregiver.bio || 'No profile biography was submitted.'}</p><div className="cw-provider-meta"><span>{caregiver.experience_years} years’ experience</span><span>{caregiver.location || 'Location not listed'}</span></div>
                <button type="button" className="cw-button primary" disabled={busy === 'slots:' + caregiver.caregiver_id} onClick={() => { setSelectedProvider(caregiver.caregiver_id); void loadSlots(caregiver.caregiver_id) }}>{busy === 'slots:' + caregiver.caregiver_id ? 'Loading times…' : 'View available times'}</button>
                {slotsByCaregiver[caregiver.caregiver_id] && <div className="cw-slot-list"><strong>Available times</strong>{!slotsByCaregiver[caregiver.caregiver_id].length ? <p className="cw-muted">No availability slots are published.</p> : slotsByCaregiver[caregiver.caregiver_id].map((slot) => <label className="cw-slot" key={slot.id}><input type="radio" name="caregiver-slot" checked={selectedSlot === slot.id} onChange={() => setSelectedSlot(slot.id)} /><span><strong>{dateTime(slot.starts_at)}</strong><small>Until {dateTime(slot.ends_at)}</small></span></label>)}</div>}
              </article>)}</div>}
            {selectedSlot && <form className="cw-inline-form cw-spaced" onSubmit={submitAppointment}><label>Message to the caregiver<textarea rows={2} maxLength={1000} value={appointmentMessage} onChange={(event) => setAppointmentMessage(event.target.value)} placeholder="Describe the care request or preferred arrangement." /></label><button className="cw-button primary" disabled={busy === 'appointment'}>{busy === 'appointment' ? 'Submitting…' : 'Request selected time'}</button></form>}
          </section>}
          {tab === 'home-booking' && <section className="cw-panel">
            <div className="cw-panel-heading"><div><p className="cw-kicker">CARE-HOME BOOKING</p><h2>Request a scheduled service</h2></div></div>
            <p className="cw-help">The booking API requires a resident ID supplied by the care home or family authorization. Select a provider from the live directory below.</p>
            <form className="cw-form" onSubmit={submitHomeBooking}>
              <label>Resident ID<input value={residentId} onChange={(event) => setResidentId(event.target.value)} required placeholder="Resident ID from the care home" /></label>
              <label>Care provider<select value={selectedProvider} onChange={(event) => setSelectedProvider(event.target.value)} required><option value="">Choose a provider</option><optgroup label="Care homes">{careHomes.map((home) => <option key={home.organization_id} value={'care_home:' + home.organization_id}>{home.organization_name}{home.location ? ' — ' + home.location : ''}</option>)}</optgroup><optgroup label="Caregivers">{caregivers.map((caregiver) => <option key={caregiver.caregiver_id} value={'caregiver:' + caregiver.caregiver_id}>{caregiver.full_name || caregiver.caregiver_id} · {caregiver.service_type}</option>)}</optgroup></select></label>
              <label>Service type<input value={serviceType} onChange={(event) => setServiceType(event.target.value)} minLength={2} maxLength={100} required /></label>
              <label>Start time<input type="datetime-local" value={startsAt} onChange={(event) => setStartsAt(event.target.value)} required /></label>
              <label>End time<input type="datetime-local" value={endsAt} onChange={(event) => setEndsAt(event.target.value)} required /></label>
              <label className="cw-full-field">Details for the provider<textarea rows={3} maxLength={1000} value={bookingMessage} onChange={(event) => setBookingMessage(event.target.value)} placeholder="Share scheduling or service details relevant to this booking." /></label>
              <div className="cw-form-actions"><button className="cw-button primary" disabled={busy === 'booking'}>{busy === 'booking' ? 'Sending request…' : 'Submit booking request'}</button></div>
            </form>
          </section>}
          {tab === 'my-bookings' && <section className="cw-panel">
            <div className="cw-panel-heading"><div><p className="cw-kicker">YOUR SCHEDULE</p><h2>Care booking requests</h2></div><button type="button" className="cw-button" onClick={() => setRefreshKey((value) => value + 1)}>Refresh</button></div>
            <p className="cw-booking-intro">Check the time and status of each request here. Updates appear as the provider responds.</p>
            <div className="cw-family-booking-groups">
              <section className="cw-family-booking-group" aria-labelledby="family-care-home-bookings">
                <div className="cw-family-booking-heading"><div><span className="cw-family-booking-icon" aria-hidden="true">⌂</span><h3 id="family-care-home-bookings">Care-home bookings</h3></div><span className="cw-status">{bookings.length} {bookings.length === 1 ? 'request' : 'requests'}</span></div>
                {!bookings.length ? <div className="cw-empty"><strong>No care-home bookings yet</strong><p>Requests for a resident’s scheduled service will appear here.</p></div> : <div className="cw-record-list">{bookings.map((item) => <article className="cw-record cw-family-booking-record" key={item.id}><div className="cw-record-main"><div className="cw-record-title-row"><h3>{item.service_type}</h3><span className={'cw-pill ' + statusTone(item.status)}>{item.status}</span></div><p>{dateTime(item.starts_at)} – {dateTime(item.ends_at)}</p><small>Resident {item.resident_id} · Provider {item.provider_id} · {item.provider_type.replaceAll('_', ' ')}</small>{item.decision_message && <p>{item.decision_message}</p>}</div><div className="cw-record-actions">{staffCanReview && item.status === 'requested' && <><button className="cw-button primary" disabled={busy === item.id} onClick={() => void decideBooking(item.id, 'approved')}>Approve</button><button className="cw-button danger" disabled={busy === item.id} onClick={() => void decideBooking(item.id, 'rejected')}>Reject</button></>}{!staffCanReview && ['requested', 'approved'].includes(item.status) && <button className="cw-button danger" disabled={busy === item.id} onClick={() => void cancelBooking(item.id)}>Cancel request</button>}</div></article>)}</div>}
              </section>
              <section className="cw-family-booking-group" aria-labelledby="family-caregiver-appointments">
                <div className="cw-family-booking-heading"><div><span className="cw-family-booking-icon caregiver" aria-hidden="true">♡</span><h3 id="family-caregiver-appointments">Caregiver appointments</h3></div><span className="cw-status">{appointments.length} {appointments.length === 1 ? 'request' : 'requests'}</span></div>
                {!appointments.length ? <div className="cw-empty"><strong>No caregiver appointments yet</strong><p>Choose an available time to send your first request.</p><a href="#caregivers" className="cw-button">Find a caregiver</a></div> : <div className="cw-record-list">{appointments.map((item) => <article className="cw-record cw-family-booking-record" key={item.id}><div className="cw-record-main"><div className="cw-record-title-row"><h3>{item.service_type.replaceAll('_', ' ')}</h3><span className={'cw-pill ' + statusTone(item.status)}>{item.status}</span></div><p>{dateTime(item.starts_at)} – {dateTime(item.ends_at)}</p><small>Appointment ID: {item.id}</small>{item.message && <p>{item.message}</p>}{item.decision_message && <p>{item.decision_message}</p>}</div>{caregiverCanReview && item.status === 'pending' && <div className="cw-record-actions"><button className="cw-button primary" disabled={busy === item.id} onClick={() => void decideAppointment(item.id, 'accepted')}>Accept</button><button className="cw-button danger" disabled={busy === item.id} onClick={() => void decideAppointment(item.id, 'rejected')}>Decline</button></div>}</article>)}</div>}
              </section>
            </div>
          </section>}
        </>}
      </main>
    </>
  )
}
