import { useEffect, useMemo, useState } from 'react'
import AdminNav from '../../components/AdminNav'
import { createAdminUser, getAdminUsers, setAdminUserActive } from '../../api/workspace'
import { useSession } from '../../lib/session'
import '../AdminConsolePages.css'
import './AdminUsersPage.css'

const roleName = (value = '') => value.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase())

export default function AdminUsersPage() {
  const session = useSession()
  const [users, setUsers] = useState([])
  const [query, setQuery] = useState('')
  const [role, setRole] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [busyId, setBusyId] = useState('')
  const [adminForm, setAdminForm] = useState({ full_name: '', email: '', password: '' })

  async function refreshUsers() {
    const records = await getAdminUsers()
    setUsers(Array.isArray(records) ? records : [])
  }

  async function submitAdmin(event) {
    event.preventDefault(); setError(''); setNotice(''); setBusyId('create')
    try {
      await createAdminUser(adminForm)
      setAdminForm({ full_name: '', email: '', password: '' })
      await refreshUsers()
      setNotice('Administrator account created. They can now sign in with their own email and password.')
    } catch (err) { setError(err instanceof Error ? err.message : 'Could not create administrator.') }
    finally { setBusyId('') }
  }

  async function changeStatus(user) {
    const next = !user.is_active
    if (!window.confirm(`${next ? 'Reactivate' : 'Deactivate'} ${user.full_name || user.email}? ${next ? '' : 'Their account access will be blocked; history and records will be retained.'}`)) return
    setError(''); setNotice(''); setBusyId(user.user_id)
    try { await setAdminUserActive(user.user_id, next); await refreshUsers(); setNotice(`Account ${next ? 'reactivated' : 'deactivated'} successfully.`) }
    catch (err) { setError(err instanceof Error ? err.message : 'Could not update this account.') }
    finally { setBusyId('') }
  }

  useEffect(() => {
    let cancelled = false
    getAdminUsers()
      .then((records) => { if (!cancelled) setUsers(Array.isArray(records) ? records : []) })
      .catch((err) => { if (!cancelled) setError(err instanceof Error ? err.message : 'Could not load accounts.') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  const roles = useMemo(() => [...new Set(users.map((user) => user.role))].sort(), [users])
  const visible = useMemo(() => users.filter((user) => {
    const matchesRole = role === 'all' || user.role === role
    const haystack = `${user.full_name || ''} ${user.email} ${user.user_id}`.toLowerCase()
    return matchesRole && haystack.includes(query.trim().toLowerCase())
  }), [users, role, query])
  const activeCount = users.filter((user) => user.is_active).length

  return <>
    <AdminNav />
    <main className="admin-users admin-console-page">
      <header className="admin-users-head">
        <div><p className="admin-users-eyebrow">ACCOUNT DIRECTORY</p><h1>Users & access</h1><p>Manage account access and the CareLife admin team. Account history stays available for audits.</p></div>
      </header>
      <section className="admin-users-stats" aria-label="Account totals">
        <article><span>Total accounts</span><strong>{loading ? '—' : users.length}</strong></article>
        <article><span>Active accounts</span><strong>{loading ? '—' : activeCount}</strong></article>
        <article><span>Access categories</span><strong>{loading ? '—' : roles.length}</strong></article>
        <article><span>CareLife admins</span><strong>{loading ? '—' : users.filter((user) => user.role === 'carelife_admin' && user.is_active).length}</strong></article>
      </section>
      <section className="admin-users-panel admin-users-admin-panel" aria-labelledby="admin-team-title">
        <div className="admin-users-panel-heading"><div><h2 id="admin-team-title">Add a CareLife administrator</h2><p>Each admin gets a separate account and can be identified in the audit log.</p></div></div>
        <form className="admin-users-create-form" onSubmit={submitAdmin}>
          <label>Full name<input required maxLength={200} autoComplete="name" value={adminForm.full_name} onChange={(event) => setAdminForm((form) => ({ ...form, full_name: event.target.value }))} /></label>
          <label>Email address<input required type="email" autoComplete="email" value={adminForm.email} onChange={(event) => setAdminForm((form) => ({ ...form, email: event.target.value }))} /></label>
          <label>Initial password<input required type="password" minLength={12} maxLength={128} autoComplete="new-password" value={adminForm.password} onChange={(event) => setAdminForm((form) => ({ ...form, password: event.target.value }))} /><small>At least 12 characters. Share the login details securely with this administrator.</small></label>
          <button type="submit" disabled={busyId === 'create'}>{busyId === 'create' ? 'Creating…' : 'Create admin account'}</button>
        </form>
      </section>
      <section className="admin-users-panel" aria-labelledby="accounts-title">
        <div className="admin-users-panel-heading"><div><h2 id="accounts-title">All accounts</h2><p>Account list from the CareLife database</p></div><span>{loading ? 'Loading…' : `${visible.length} shown`}</span></div>
        <div className="admin-users-filters"><label>Search accounts<input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Name, email, or user ID" /></label><label>Access category<select value={role} onChange={(event) => setRole(event.target.value)}><option value="all">All categories</option>{roles.map((item) => <option value={item} key={item}>{roleName(item)}</option>)}</select></label></div>
        {error && <p className="admin-users-error" role="alert">{error}</p>}{notice && <p className="admin-users-notice" role="status">{notice}</p>}
        {loading ? <p className="admin-users-empty" role="status">Loading accounts…</p> : !error && visible.length === 0 ? <p className="admin-users-empty">{users.length ? 'No accounts match these filters.' : 'No accounts were returned.'}</p> : !error && <div className="admin-users-table-wrap"><table><thead><tr><th>Name</th><th>Email</th><th>Access category</th><th>Organizations</th><th>Status</th><th>Joined</th><th>Actions</th></tr></thead><tbody>{visible.map((user) => <tr key={user.user_id}><td><strong>{user.full_name || 'Name not provided'}</strong><small>{user.user_id}</small></td><td>{user.email}</td><td><span className="admin-users-role">{roleName(user.role)}</span></td><td>{user.organization_ids?.length || '—'}</td><td><span className={'admin-users-status ' + (user.is_active ? 'active' : 'inactive')}>{user.is_active ? 'Active' : 'Inactive'}</span></td><td>{user.created_at ? new Date(user.created_at).toLocaleDateString() : '—'}</td><td><button className="admin-user-action" type="button" disabled={busyId === user.user_id || (user.email === session.email && user.is_active)} onClick={() => void changeStatus(user)}>{busyId === user.user_id ? 'Saving…' : user.is_active ? (user.email === session.email ? 'You' : 'Deactivate') : 'Reactivate'}</button></td></tr>)}</tbody></table></div>}
      </section>
    </main>
  </>
}
