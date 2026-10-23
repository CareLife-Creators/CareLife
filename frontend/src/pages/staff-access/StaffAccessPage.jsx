import { useEffect, useState } from 'react'
import SiteNav from '../../components/SiteNav'
import { createRoleRequest, getMyRoleRequests } from '../../api/roleRequests'
import { refreshSession } from '../../api/auth'
import { STAFF_ROLE_OPTIONS, isStaff, roleLabel } from '../../lib/roles'
import { useSession } from '../../lib/session'
import '../RoleRequests.css'

const STATUS_TEXT = { pending: 'Waiting for review', approved: 'Approved', rejected: 'Not approved' }

function formatDate(value) {
  const date = new Date(value)
  return value && !Number.isNaN(date.getTime()) ? date.toLocaleString() : ''
}

export default function StaffAccessPage() {
  const { role } = useSession()
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)
  const [requestedRole, setRequestedRole] = useState(STAFF_ROLE_OPTIONS[0].value)
  const [note, setNote] = useState('')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState(null)

  useEffect(() => {
    let cancelled = false
    getMyRoleRequests()
      .then((data) => {
        if (cancelled) return
        setRequests(Array.isArray(data) ? data : [])
        setLoadError('')
        // An approved request changes the role, so refresh it from the backend.
        void refreshSession()
      })
      .catch((err) => {
        if (!cancelled) setLoadError(err instanceof Error ? err.message : 'Unable to load your requests.')
      })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [reloadKey])

  const hasPending = requests.some((item) => item.status === 'pending')
  const alreadyStaff = isStaff(role)

  async function handleSubmit(event) {
    event.preventDefault()
    setBusy(true)
    setMessage(null)
    try {
      await createRoleRequest({ requestedRole, note })
      setNote('')
      setMessage({ type: 'success', text: 'Request sent. A CareLife administrator will review it.' })
      setLoading(true)
      setReloadKey((value) => value + 1)
    } catch (err) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Unable to send the request.' })
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <SiteNav />
      <main className="rr-page">
        <header className="rr-hero">
          <h1>Staff access</h1>
          <p>
            Staff roles give access to organization tools, so a CareLife administrator reviews every request.
            Until a request is approved, your account keeps its current role{role ? ': ' + roleLabel(role) : ''}.
          </p>
        </header>

        {alreadyStaff ? (
          <section className="rr-panel">
            <h2>You have staff access</h2>
            <p>Your account role is {roleLabel(role)}. You can open Verification from the menu.</p>
          </section>
        ) : (
          <section className="rr-panel">
            <h2>Request a staff role</h2>
            {hasPending ? (
              <p>You already have a request waiting for review. You can send a new one after it is decided.</p>
            ) : (
              <form className="rr-form" onSubmit={handleSubmit}>
                <div className="rr-field">
                  <label htmlFor="rr-role">Role you need</label>
                  <select id="rr-role" value={requestedRole} onChange={(event) => setRequestedRole(event.target.value)}>
                    {STAFF_ROLE_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>{option.label}</option>
                    ))}
                  </select>
                </div>
                <div className="rr-field">
                  <label htmlFor="rr-note">Note for the reviewer (optional)</label>
                  <textarea
                    id="rr-note"
                    rows={4}
                    maxLength={1000}
                    value={note}
                    onChange={(event) => setNote(event.target.value)}
                    placeholder="Name the organization you work for and your position."
                  />
                </div>
                <button type="submit" className="rr-btn" disabled={busy}>
                  {busy ? 'Sending…' : 'Send request'}
                </button>
              </form>
            )}
            {message && (
              <p className={'rr-message ' + message.type} role={message.type === 'error' ? 'alert' : 'status'}>
                {message.text}
              </p>
            )}
          </section>
        )}

        <section className="rr-panel">
          <h2>Your requests</h2>
          {loading && <p role="status">Loading your requests…</p>}
          {!loading && loadError && <p className="rr-message error" role="alert">{loadError}</p>}
          {!loading && !loadError && !requests.length && <p>You have not sent any requests yet.</p>}
          {!loading && !loadError && requests.length > 0 && (
            <ul className="rr-list">
              {requests.map((item) => (
                <li className="rr-item" key={item.id}>
                  <div>
                    <strong>{roleLabel(item.requested_role) || item.requested_role}</strong>
                    <small>Sent {formatDate(item.created_at)}</small>
                    {item.note && <p>{item.note}</p>}
                  </div>
                  <span className={'rr-status ' + item.status}>{STATUS_TEXT[item.status] || item.status}</span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </>
  )
}