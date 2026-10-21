import { useEffect, useState } from 'react'
import SiteNav from '../components/SiteNav'
import { getPendingCaregivers, reviewCaregiver, getAdminAuditLogs, getPendingImpactUpdates, reviewImpactUpdate } from '../api/workspace'
import { API_BASE_URL } from '../api/client'
import { getToken } from '../lib/session'
import './Workspace.css'

const dateTime = (value) => {
  const date = new Date(value)
  return value && !Number.isNaN(date.getTime()) ? date.toLocaleString() : 'Date not recorded'
}


function ProtectedImpactMedia({ media }) {
  const [src, setSrc] = useState('')
  const [mediaError, setMediaError] = useState('')

  useEffect(() => {
    let objectUrl = ''
    let cancelled = false
    const token = getToken()
    const headers = token ? { Authorization: 'Bearer ' + token } : {}
    fetch(API_BASE_URL + media.url, { headers, credentials: 'include' })
      .then((response) => {
        if (!response.ok) throw new Error('Protected media preview is unavailable (' + response.status + ').')
        return response.blob()
      })
      .then((blob) => {
        if (cancelled) return
        objectUrl = URL.createObjectURL(blob)
        setSrc(objectUrl)
      })
      .catch((err) => { if (!cancelled) setMediaError(err instanceof Error ? err.message : 'Media preview could not be loaded.') })
    return () => {
      cancelled = true
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [media.id, media.url])

  return <div className="cw-impact-media">
    {media.media_type === 'video' ? (src ? <video controls preload="metadata" src={src} /> : <span>{mediaError || 'Loading protected video…'}</span>) : (src ? <img src={src} alt="Impact update attachment under review" /> : <span>{mediaError || 'Loading protected image…'}</span>)}
    <small>{media.media_type} · {media.content_type} · {(Number(media.file_size) / (1024 * 1024)).toFixed(2)} MB</small>
  </div>
}

export default function AdminOperationsPage() {
  const [tab, setTab] = useState('caregivers')
  const [caregivers, setCaregivers] = useState([])
  const [logs, setLogs] = useState([])
  const [pendingUpdates, setPendingUpdates] = useState([])
  const [reviewNotes, setReviewNotes] = useState({})
  const [privacyConfirmed, setPrivacyConfirmed] = useState({})
  const [loading, setLoading] = useState(true)
  const [busyId, setBusyId] = useState('')
  const [decisionMessages, setDecisionMessages] = useState({})
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    const [caregiverResult, logResult, impactResult] = await Promise.allSettled([getPendingCaregivers(), getAdminAuditLogs(), getPendingImpactUpdates()])
    if (caregiverResult.status === 'fulfilled') setCaregivers(Array.isArray(caregiverResult.value) ? caregiverResult.value : [])
    if (logResult.status === 'fulfilled') setLogs(Array.isArray(logResult.value) ? logResult.value : [])
    if (impactResult.status === 'fulfilled') setPendingUpdates(Array.isArray(impactResult.value) ? impactResult.value : [])
    if (caregiverResult.status === 'rejected' && logResult.status === 'rejected' && impactResult.status === 'rejected') {
      setError('Admin data could not be loaded. Confirm your administrator session and retry.')
    } else if (caregiverResult.status === 'rejected' && tab === 'caregivers') {
      setError(caregiverResult.reason instanceof Error ? caregiverResult.reason.message : 'Caregiver review queue is unavailable.')
    } else if (logResult.status === 'rejected' && tab === 'audit') {
      setError(logResult.reason instanceof Error ? logResult.reason.message : 'Audit history is unavailable.')
    } else if (impactResult.status === 'rejected' && tab === 'impact') {
      setError(impactResult.reason instanceof Error ? impactResult.reason.message : 'Impact review queue is unavailable.')
    }
    setLoading(false)
  }

  useEffect(() => { void load() }, [])

  async function decideImpact(update, decision) {
    if (decision === 'approved' && !privacyConfirmed[update.id]) {
      setError('Confirm that you checked the update for identifying child details before approving it.')
      return
    }
    setBusyId(update.id)
    setError('')
    setNotice('')
    try {
      await reviewImpactUpdate(update.id, decision, Boolean(privacyConfirmed[update.id]), reviewNotes[update.id] || '')
      setPendingUpdates((current) => current.filter((item) => item.id !== update.id))
      setNotice('Impact update ' + decision + '.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Impact review decision could not be saved.')
    } finally { setBusyId('') }
  }

  async function decide(caregiver, status) {
    setBusyId(caregiver.user_id)
    setError('')
    setNotice('')
    try {
      await reviewCaregiver(caregiver.user_id, status, decisionMessages[caregiver.user_id] || '')
      setCaregivers((current) => current.filter((item) => item.user_id !== caregiver.user_id))
      setNotice((caregiver.full_name || caregiver.user_id) + ' marked ' + status + '.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The review was not saved.')
    } finally {
      setBusyId('')
    }
  }

  return (
    <>
      <SiteNav />
      <main className="cw-page">
        <header className="cw-hero admin">
          <span className="cw-kicker">CARELIFE ADMINISTRATION</span>
          <h1>Review access. Keep a clear record.</h1>
          <p>Review submitted caregiver profiles and inspect the audit trail of actions performed in the platform.</p>
          <div className="cw-hero-meta"><span>{caregivers.length} caregiver reviews waiting</span><span>{logs.length} audit events · {pendingUpdates.length} impact updates awaiting review</span></div>
        </header>
        <nav className="cw-tabs" aria-label="Admin sections">
          <button type="button" className={tab === 'caregivers' ? 'active' : ''} aria-pressed={tab === 'caregivers'} onClick={() => { setTab('caregivers'); setError('') }}>Caregiver verification</button>
          <button type="button" className={tab === 'impact' ? 'active' : ''} aria-pressed={tab === 'impact'} onClick={() => { setTab('impact'); setError('') }}>Impact moderation</button>
          <button type="button" className={tab === 'audit' ? 'active' : ''} aria-pressed={tab === 'audit'} onClick={() => { setTab('audit'); setError('') }}>Audit log</button>
          <button type="button" className="cw-tabs-action" onClick={() => void load()} disabled={loading}>{loading ? 'Refreshing…' : 'Refresh data'}</button>
        </nav>
        {error && <div className="cw-alert error" role="alert">{error}</div>}
        {notice && <div className="cw-alert success" role="status">{notice}</div>}
        {loading ? <div className="cw-state">Loading admin records…</div> : tab === 'caregivers' ? <section className="cw-panel">
          <div className="cw-panel-heading"><div><p className="cw-kicker">PENDING REVIEW</p><h2>Caregiver profiles</h2></div><span className="cw-status">{caregivers.length} pending</span></div>
          {!caregivers.length ? <div className="cw-empty"><strong>No caregiver profiles are awaiting review.</strong><p>When a caregiver submits their profile and supporting document references, it will appear in this queue.</p></div> :
            <div className="cw-record-list">{caregivers.map((item) => <article className="cw-record stacked" key={item.user_id}>
              <div className="cw-record-main"><div className="cw-record-title-row"><h3>{item.full_name || 'Caregiver profile'}</h3><span className="cw-pill warning">{item.verification_status || 'pending'}</span></div>
                <p>{String(item.service_type || '').replaceAll('_', ' ')} · {item.experience_years ?? 0} years of experience</p>
                <p>{item.bio || 'No biography submitted.'}</p>
                <small>{item.location || 'Location not supplied'} · User ID: {item.user_id}</small>
                {!!item.documents?.length && <div className="cw-document-list"><strong>Submitted document references</strong>{item.documents.map((doc) => <span key={doc.id}>{doc.document_type.replaceAll('_', ' ')} · {doc.document_reference}</span>)}</div>}
              </div>
              <label className="cw-full-field">Reviewer note (optional)<textarea rows={2} maxLength={2000} value={decisionMessages[item.user_id] || ''} onChange={(event) => setDecisionMessages((current) => ({ ...current, [item.user_id]: event.target.value }))} placeholder="Record a specific reason if you reject the submission." /></label>
              <div className="cw-form-actions"><button type="button" className="cw-button primary" disabled={busyId === item.user_id} onClick={() => void decide(item, 'approved')}>{busyId === item.user_id ? 'Saving…' : 'Approve profile'}</button><button type="button" className="cw-button danger" disabled={busyId === item.user_id} onClick={() => void decide(item, 'rejected')}>Reject profile</button></div>
            </article>)}</div>}
        </section> : tab === 'impact' ? <section className="cw-panel">
          <div className="cw-panel-heading"><div><p className="cw-kicker">PENDING REVIEW</p><h2>Orphanage impact updates</h2></div><span className="cw-status">{pendingUpdates.length} awaiting review</span></div>
          <p className="cw-help">Check the update content and any attached media for personal information that could identify a child. Approval publishes the update; rejection keeps it out of the public board.</p>
          {!pendingUpdates.length ? <div className="cw-empty"><strong>No impact updates are waiting for review.</strong><p>New updates from orphanage staff will appear here after they are submitted.</p></div> :
            <div className="cw-record-list">{pendingUpdates.map((item) => <article className="cw-record stacked" key={item.id}>
              <div className="cw-record-main"><div className="cw-record-title-row"><h3>{item.title}</h3><span className="cw-pill warning">{String(item.status || 'pending_review').replaceAll('_', ' ')}</span></div>
                <p>{item.content}</p><small>{item.organization_name} · Created {dateTime(item.created_at)} · Update ID: {item.id}</small>
              </div>
              {item.media?.length > 0 && <div className="cw-detail-grid">{item.media.map((media) => <ProtectedImpactMedia key={media.id} media={media} />)}</div>}
              <label className="cw-full-field">Reviewer note<textarea rows={2} maxLength={2000} value={reviewNotes[item.id] || ''} onChange={(event) => setReviewNotes((current) => ({ ...current, [item.id]: event.target.value }))} placeholder="Record the reason for approval or rejection." /></label>
              <label className="cw-consent-check"><input type="checkbox" checked={Boolean(privacyConfirmed[item.id])} onChange={(event) => setPrivacyConfirmed((current) => ({ ...current, [item.id]: event.target.checked }))} /><span>I checked the content and attached media for identifying child details before publication.</span></label>
              <div className="cw-form-actions"><button type="button" className="cw-button primary" disabled={busyId === item.id} onClick={() => void decideImpact(item, 'approved')}>{busyId === item.id ? 'Saving…' : 'Approve & publish'}</button><button type="button" className="cw-button danger" disabled={busyId === item.id} onClick={() => void decideImpact(item, 'rejected')}>Reject update</button></div>
            </article>)}</div>}
        </section> : <section className="cw-panel">
          <div className="cw-panel-heading"><div><p className="cw-kicker">RECENT ACTIVITY</p><h2>Audit log</h2></div><span className="cw-status">{logs.length} events</span></div>
          {!logs.length ? <div className="cw-empty"><strong>No audit events returned.</strong><p>When an auditable action is recorded, the actor, action, target and timestamp are shown here.</p></div> :
            <div className="cw-table-wrap"><table className="cw-table"><thead><tr><th>Action</th><th>Actor role</th><th>Target</th><th>Actor ID</th><th>Time</th></tr></thead><tbody>{logs.map((item) => <tr key={item.id}><td><strong>{String(item.action || '').replaceAll('_', ' ')}</strong></td><td>{String(item.actor_role || '').replaceAll('_', ' ')}</td><td>{item.target_type} <small>{item.target_id}</small></td><td>{item.actor_user_id}</td><td>{dateTime(item.created_at)}</td></tr>)}</tbody></table></div>}
        </section>}
      </main>
    </>
  )
}
