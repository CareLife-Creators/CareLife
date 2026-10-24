import { useState } from 'react'
import SiteNav from '../components/SiteNav'
import { useSession } from '../lib/session'
import { getResidentCheckIns, createResidentCheckIn } from '../api/workspace'
import './Workspace.css'

const showDate = (value) => {
  const date = new Date(value)
  return value && !Number.isNaN(date.getTime()) ? date.toLocaleString() : 'Time not recorded'
}

export default function FamilyCheckInsPage() {
  const { role } = useSession()
  const [residentId, setResidentId] = useState('')
  const [checkIns, setCheckIns] = useState([])
  const [form, setForm] = useState({ wellbeing_status: 'well', notes: '' })
  const [loading, setLoading] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  async function loadCheckIns(event) {
    event?.preventDefault()
    if (!residentId.trim()) return
    setLoading(true); setError(''); setNotice('')
    try {
      const data = await getResidentCheckIns(residentId.trim())
      setCheckIns(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Check-ins could not be loaded. Confirm the resident ID and your family authorization.')
      setCheckIns([])
    } finally { setLoading(false) }
  }

  async function recordCheckIn(event) {
    event.preventDefault()
    if (!residentId.trim()) return
    setBusy(true); setError(''); setNotice('')
    try {
      await createResidentCheckIn(residentId.trim(), {
        wellbeing_status: form.wellbeing_status,
        notes: form.notes.trim() || null,
      })
      setNotice('Your wellbeing check-in was recorded.')
      setForm({ wellbeing_status: 'well', notes: '' })
      const updated = await getResidentCheckIns(residentId.trim())
      setCheckIns(Array.isArray(updated) ? updated : [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Check-in could not be recorded. The care home must have an active consent record for your account.')
    } finally { setBusy(false) }
  }

  return (
    <>
      <SiteNav />
      <main className="cw-page">
        <header className="cw-hero">
          <span className="cw-kicker">FAMILY REPRESENTATIVE</span>
          <h1>Share a wellbeing update with the care home.</h1>
          <p>A remote check-in lets an approved family representative send a brief update from their own CareLife account, even when they are away from the care home. The care home must grant consent for this account and resident first.</p>
          <div className="cw-hero-meta"><span>{role ? role.replaceAll('_', ' ') : 'Family account'}</span><span>Resident access is consent-controlled</span></div>
        </header>
        <aside className="cw-alert"><strong>What “remote” means:</strong> this is a written wellbeing update, not GPS tracking, live video, continuous monitoring, or a medical assessment. Use the resident ID the care home shared with you. An “Urgent” entry does not contact emergency services or guarantee an immediate response; contact the care home or local emergency services directly when urgent help is needed.</aside>
        {error && <div className="cw-alert error" role="alert">{error}</div>}
        {notice && <div className="cw-alert success" role="status">{notice}</div>}
        <section className="cw-panel">
          <div className="cw-panel-heading"><div><p className="cw-kicker">STEP 1 · CARE HOME AUTHORIZATION</p><h2>Open the resident’s updates</h2></div></div>
          <form className="cw-inline-form" onSubmit={loadCheckIns}>
            <label>Resident ID<input value={residentId} onChange={(event) => setResidentId(event.target.value)} required placeholder="Enter the resident ID shared by the care home" /></label>
            <button className="cw-button primary" disabled={loading}>{loading ? 'Loading…' : 'View check-ins'}</button>
          </form>
          <div className="cw-record-list cw-spaced">
            {checkIns.map((item) => <article className="cw-record" key={item.id}>
              <div className="cw-record-main"><div className="cw-record-title-row"><h3>{String(item.wellbeing_status || '').replaceAll('_', ' ')}</h3><span className={'cw-pill ' + (item.wellbeing_status === 'well' ? 'mint' : 'warning')}>{item.wellbeing_status === 'urgent' ? 'Urgent' : item.wellbeing_status === 'needs_attention' ? 'Needs attention' : 'Well'}</span></div>
                <p>{item.notes || 'No additional note was recorded.'}</p><small>{showDate(item.recorded_at)} · Resident {item.resident_id}</small>
              </div>
            </article>)}
            {!loading && !checkIns.length && <div className="cw-empty"><strong>No check-ins displayed.</strong><p>Enter the resident ID and load history. If access is denied, ask the care home to confirm that your family representative ID has active consent.</p></div>}
          </div>
        </section>
        <section className="cw-panel">
          <div className="cw-panel-heading"><div><p className="cw-kicker">STEP 2 · FAMILY UPDATE</p><h2>Send a wellbeing check-in</h2></div></div>
          <form className="cw-form" onSubmit={recordCheckIn}>
            <label>Resident ID<input value={residentId} onChange={(event) => setResidentId(event.target.value)} required /></label>
            <label>Wellbeing status<select value={form.wellbeing_status} onChange={(event) => setForm((current) => ({ ...current, wellbeing_status: event.target.value }))}><option value="well">Well</option><option value="needs_attention">Needs attention</option><option value="urgent">Urgent</option></select></label>
            <label className="cw-full-field">Brief note for the care team<textarea rows={4} maxLength={2000} value={form.notes} onChange={(event) => setForm((current) => ({ ...current, notes: event.target.value }))} placeholder="Share a short, factual update. Do not include sensitive details that are not needed." /></label>
            <div className="cw-form-actions"><button className="cw-button primary" disabled={busy}>{busy ? 'Recording…' : 'Submit check-in'}</button></div>
          </form>
        </section>
      </main>
    </>
  )
}
