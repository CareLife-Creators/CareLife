import { useEffect, useState } from 'react'
import SiteNav from '../../components/SiteNav'
import { approveRoleRequest, getAdminRoleRequests, rejectRoleRequest } from '../../api/roleRequests'
import { roleLabel } from '../../lib/roles'
import '../RoleRequests.css'

const TABS = [['pending', 'Pending'], ['approved', 'Approved'], ['rejected', 'Rejected']]

function formatDate(value) {
  const date = new Date(value)
  return value && !Number.isNaN(date.getTime()) ? date.toLocaleString() : ''
}

// The API returns the requester's id. If it also returns a name or email, show that instead.
function requesterName(item) {
  return item.requester_full_name || item.requester_email || 'User ' + String(item.user_id || '').slice(0, 8)
}

export default function AdminRoleRequestsPage() {
  const [status, setStatus] = useState('pending')
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [busyId, setBusyId] = useState('')
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    let cancelled = false
    getAdminRoleRequests(status)
      .then((data) => {
        if (cancelled) return
        setItems(Array.isArray(data) ? data : [])
        setError('')
      })
      .catch((err) => {
        if (cancelled) return
        setItems([])
        setError(err instanceof Error ? err.message : 'Unable to load requests.')
      })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [status, reloadKey])

  function changeStatus(next) {
    if (next === status) return
    setLoading(true)
    setError('')
    setNotice('')
    setStatus(next)
  }

  async function decide(item, action) {
    const label = roleLabel(item.requested_role) || item.requested_role
    if (!window.confirm('Are you sure you want to ' + action + ' this ' + label + ' request?')) return

    setBusyId(item.id)
    setError('')
    setNotice('')
    try {
      if (action === 'approve') {
        await approveRoleRequest(item.id)
      } else {
        await rejectRoleRequest(item.id)
      }
      setNotice(action === 'approve' ? 'Request approved. The user now has the role.' : 'Request rejected.')
      setLoading(true)
      setReloadKey((value) => value + 1)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to update the request.')
    } finally {
      setBusyId('')
    }
  }

  return (
    <>
      <SiteNav />
      <main className="rr-page">
        <header className="rr-hero">
          <h1>Staff access requests</h1>
          <p>Approve or reject requests for daycare, orphanage and care-home staff roles. Each decision is recorded in the audit log.</p>
        </header>

        <div className="rr-tabs" role="tablist" aria-label="Request status">
          {TABS.map(([value, label]) => (
            <button
              key={value}
              type="button"
              role="tab"
              aria-selected={status === value}
              className={status === value ? 'active' : ''}
              onClick={() => changeStatus(value)}
            >
              {label}
            </button>
          ))}
        </div>

        {notice && <p className="rr-message success" role="status">{notice}</p>}
        {error && <p className="rr-message error" role="alert">{error}</p>}
        {loading && <p role="status">Loading requests…</p>}
        {!loading && !error && !items.length && <p className="rr-panel">No {status} requests.</p>}

        {!loading && items.length > 0 && (
          <ul className="rr-list rr-panel">
            {items.map((item) => (
              <li className="rr-item" key={item.id}>
                <div>
                  <strong>{requesterName(item)}</strong>
                  <small>Wants: {roleLabel(item.requested_role) || item.requested_role} · Sent {formatDate(item.created_at)}</small>
                  {item.note && <p>{item.note}</p>}
                  {item.reviewed_at && <small>Reviewed {formatDate(item.reviewed_at)}</small>}
                </div>
                {item.status === 'pending' ? (
                  <div className="rr-actions">
                    <button type="button" className="rr-btn" disabled={busyId === item.id} onClick={() => { void decide(item, 'approve') }}>Approve</button>
                    <button type="button" className="rr-btn secondary" disabled={busyId === item.id} onClick={() => { void decide(item, 'reject') }}>Reject</button>
                  </div>
                ) : (
                  <span className={'rr-status ' + item.status}>{item.status === 'approved' ? 'Approved' : 'Rejected'}</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </main>
    </>
  )
}