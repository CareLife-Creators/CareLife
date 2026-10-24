import { useCallback, useEffect, useState } from 'react'
import AdminNav from '../components/AdminNav'
import { getAdminOrganizationTracking } from '../api/organizationApproval'
import { getAdminRoleRequests } from '../api/roleRequests'
import { getAdminAuditLogs, getAdminUsers, getPendingCaregivers, getPendingImpactUpdates } from '../api/workspace'
import { BANGLADESH_DIVISIONS } from '../data/bangladeshMap'
import OrganizationSatelliteMap from '../components/OrganizationSatelliteMap'
import './AdminWorkspacePage.css'

const workQueues = [
  { key: 'organizations', href: '#organization-approval', icon: '◇', title: 'Organization reviews', detail: 'Review care organizations and their submitted details.', action: 'Review organizations', tone: 'mint' },
  { key: 'staff', href: '#admin-role-requests', icon: '✓', title: 'Staff access', detail: 'Decide who can use daycare, children’s home, or care-home tools.', action: 'Review staff requests', tone: 'peach' },
  { key: 'caregivers', href: '#admin-operations?tab=caregivers', icon: '♡', title: 'Caregiver profiles', detail: 'Check caregiver submissions and supporting documents.', action: 'Review caregivers', tone: 'lavender' },
  { key: 'impact', href: '#admin-operations?tab=impact', icon: '✳', title: 'Impact updates', detail: 'Review children’s-home updates before they are shared.', action: 'Review updates', tone: 'mint' },
]

export default function AdminWorkspacePage() {
  const [counts, setCounts] = useState({})
  const [organizations, setOrganizations] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [errors, setErrors] = useState([])
  const [refreshKey, setRefreshKey] = useState(0)
  const [selectedOrgArea, setSelectedOrgArea] = useState('all')
  const [selectedOrganizationId, setSelectedOrganizationId] = useState('')

  const load = useCallback(async () => {
    const results = await Promise.allSettled([
      getAdminOrganizationTracking(), getAdminRoleRequests('pending'), getPendingCaregivers(), getPendingImpactUpdates(), getAdminAuditLogs(), getAdminUsers(),
    ])
    const nextCounts = {}
    const nextErrors = []
    const keys = ['organizations', 'staff', 'caregivers', 'impact', 'audit', 'users']
    results.forEach((result, index) => {
      if (result.status === 'fulfilled') nextCounts[keys[index]] = Array.isArray(result.value) ? result.value.length : 0
      else nextErrors.push(keys[index])
    })
    if (results[0].status === 'fulfilled') {
      const records = Array.isArray(results[0].value) ? results[0].value : []
      setOrganizations(records)
      nextCounts.organizations = records.filter((organization) => ['pending', 'under_review', 'needs_correction'].includes(String(organization.status).toLowerCase())).length
    }
    if (results[5].status === 'fulfilled') setUsers(Array.isArray(results[5].value) ? results[5].value : [])
    setCounts(nextCounts)
    setErrors(nextErrors)
    setLoading(false)
  }, [])

  useEffect(() => {
    const timer = window.setTimeout(() => { void load() }, 0)
    return () => window.clearTimeout(timer)
  }, [load, refreshKey])

  const totalOpen = ['organizations', 'staff', 'caregivers', 'impact'].reduce((sum, key) => sum + (counts[key] || 0), 0)
  const roleCounts = users.reduce((totals, user) => ({ ...totals, [user.role]: (totals[user.role] || 0) + 1 }), {})
  const roleRows = Object.entries(roleCounts).sort((a, b) => b[1] - a[1])
  const maxRoleCount = Math.max(1, ...roleRows.map(([, count]) => count))
  const orgStatusCounts = organizations.reduce((totals, org) => ({ ...totals, [String(org.status || 'unknown')]: (totals[String(org.status || 'unknown')] || 0) + 1 }), {})
  const organizationAreas = BANGLADESH_DIVISIONS.map((division) => ({
    ...division,
    count: organizations.filter((organization) => division.aliases.some((alias) => String(organization.location || '').toLocaleLowerCase().includes(alias))).length,
  }))
  const visibleOrganizations = organizations.filter((organization) => {
    const area = organizationAreas.find((division) => division.id === selectedOrgArea)
    return !area || area.aliases.some((alias) => String(organization.location || '').toLocaleLowerCase().includes(alias))
  })

  return <>
    <AdminNav />
    <main className="admin-workspace">
      <header className="admin-workspace-head">
        <div><p className="admin-workspace-eyebrow">ADMINISTRATION / OVERVIEW</p><h1>Operations overview</h1><p>Review activity across organizations, access, caregiver profiles, and public updates.</p></div>
        <button type="button" className="admin-refresh" onClick={() => { setLoading(true); setRefreshKey((value) => value + 1) }} disabled={loading}>{loading ? 'Updating…' : 'Refresh data'}</button>
      </header>

      <section className="admin-workspace-summary" aria-label="Open review counts" aria-live="polite">
        <div><span>All users</span><strong>{loading ? '—' : errors.includes('users') ? '—' : users.length}</strong></div>
        <div><span>Active admins</span><strong>{loading ? '—' : errors.includes('users') ? '—' : users.filter((user) => user.role === 'carelife_admin' && user.is_active).length}</strong></div>
        <div><span>Open reviews</span><strong>{loading ? '—' : totalOpen}</strong></div>
        <div><span>Organizations</span><strong>{loading ? '—' : errors.includes('organizations') ? '—' : counts.organizations ?? 0}</strong></div>
        <div><span>Staff requests</span><strong>{loading ? '—' : errors.includes('staff') ? '—' : counts.staff ?? 0}</strong></div>
        <div><span>Caregiver profiles</span><strong>{loading ? '—' : errors.includes('caregivers') ? '—' : counts.caregivers ?? 0}</strong></div>
      </section>

      <section className="admin-analytics" aria-label="CareLife platform statistics">
        <article className="admin-chart-card"><div className="admin-chart-heading"><div><p className="admin-workspace-eyebrow">ACCOUNT MIX</p><h2>Users by access category</h2></div><a href="#admin-users">View accounts <span aria-hidden="true">→</span></a></div>
          {loading ? <p className="admin-chart-empty">Loading user statistics…</p> : errors.includes('users') ? <p className="admin-chart-empty">User statistics are unavailable. Refresh after checking the connection.</p> : roleRows.length ? <div className="admin-role-chart" role="img" aria-label={roleRows.map(([name, count]) => `${name.replaceAll('_', ' ')}: ${count} users`).join('; ')}>{roleRows.map(([name, count]) => <div className="admin-role-chart-row" key={name}><span>{name.replaceAll('_', ' ')}</span><div className="admin-chart-track"><i style={{ width: `${Math.max(6, (count / maxRoleCount) * 100)}%` }} /></div><strong>{count}</strong></div>)}</div> : <p className="admin-chart-empty">No user accounts were returned.</p>}
        </article>
        <article className="admin-chart-card"><div className="admin-chart-heading"><div><p className="admin-workspace-eyebrow">ORGANIZATION STATUS</p><h2>Verification overview</h2></div><a href="#organization-approval">Review queue <span aria-hidden="true">→</span></a></div>
          {loading ? <p className="admin-chart-empty">Loading organization statistics…</p> : errors.includes('organizations') ? <p className="admin-chart-empty">Organization statistics are unavailable.</p> : <div className="admin-status-chart">{Object.entries(orgStatusCounts).sort((a, b) => b[1] - a[1]).map(([name, count]) => <div className="admin-status-stat" key={name}><span className={'admin-status-dot ' + name.toLowerCase()} /><strong>{count}</strong><small>{name.replaceAll('_', ' ')}</small></div>)}</div>}
        </article>
      </section>

      <section className="admin-queues" aria-labelledby="admin-queues-title">
        <div className="admin-workspace-section-heading"><div><p className="admin-workspace-eyebrow">REVIEW WORK</p><h2 id="admin-queues-title">Queues</h2></div></div>
        {errors.length > 0 && <p className="admin-queue-error" role="status">Some review counts could not be loaded. The queues are still available to open; refresh after checking your connection.</p>}
        <div className="admin-queue-table" role="list">{workQueues.map((item) => <article className="admin-queue-row" key={item.key} role="listitem">
          <span className="admin-queue-icon" aria-hidden="true">{item.icon}</span><span className="admin-queue-main"><strong>{item.title}</strong><small>{item.detail}</small></span><span className={'admin-queue-count' + ((counts[item.key] || 0) > 0 ? ' has-pending' : '')}>{loading ? '—' : errors.includes(item.key) ? 'Unavailable' : `${counts[item.key] ?? 0} pending`}</span><a href={item.href}>{item.action}<span aria-hidden="true">→</span></a>
        </article>)}</div>
      </section>

      <section className="admin-org-tracking" aria-labelledby="admin-org-tracking-title">
        <div className="admin-tracking-heading"><div><p className="admin-workspace-eyebrow">ORGANIZATION TRACKING</p><h2 id="admin-org-tracking-title">Status, location, and review history</h2><p>See every submitted organization and the decisions recorded for it.</p></div><a href="#organization-approval">Open review queue <span aria-hidden="true">→</span></a></div>
        {errors.includes('organizations') ? <p className="admin-queue-error" role="alert">Organization tracking could not load. Refresh after checking the connection.</p> : <div className="admin-org-tracking-grid">
          <div className="admin-org-map-box"><div className="admin-org-map-title"><strong>Exact organization locations</strong><span>Satellite imagery · organization-submitted coordinates</span></div><OrganizationSatelliteMap organizations={visibleOrganizations} selectedId={selectedOrganizationId} onSelect={setSelectedOrganizationId}/><div className="admin-org-area-buttons"><button type="button" aria-pressed={selectedOrgArea === 'all'} className={selectedOrgArea === 'all' ? 'active' : ''} onClick={() => { setSelectedOrgArea('all'); setSelectedOrganizationId('') }}>All divisions <span>{organizations.length}</span></button>{organizationAreas.map((area) => <button type="button" key={area.id} aria-pressed={selectedOrgArea === area.id} className={selectedOrgArea === area.id ? 'active' : ''} onClick={() => { setSelectedOrgArea(area.id); setSelectedOrganizationId('') }}>{area.name}<span>{area.count}</span></button>)}</div><p className="admin-org-map-disclaimer">{visibleOrganizations.filter((org) => org.latitude != null && org.longitude != null).length} exact pins shown. {visibleOrganizations.length - visibleOrganizations.filter((org) => org.latitude != null && org.longitude != null).length} organizations have not submitted coordinates. Pins show submitted locations; they do not track people in real time.</p></div>
          <div className="admin-org-list"><div className="admin-org-list-head"><h3>{selectedOrgArea === 'all' ? 'All organizations' : `Organizations in ${organizationAreas.find((area) => area.id === selectedOrgArea)?.name}`}</h3><span>{loading ? 'Updating…' : visibleOrganizations.length}</span></div>{loading ? <p className="admin-org-empty">Loading organization records…</p> : visibleOrganizations.length ? visibleOrganizations.map((organization) => <article className="admin-org-row" key={organization.organization_id}><div className="admin-org-row-top"><div><strong>{organization.organization_name}</strong><small>{organization.organization_type.replaceAll('_', ' ')}</small></div><span className={'admin-org-status ' + String(organization.status).toLowerCase()}>{String(organization.status).replaceAll('_', ' ')}</span></div><p>{organization.location || 'Location not provided'} · Updated {new Date(organization.updated_at).toLocaleDateString()}</p>{organization.latitude != null && organization.longitude != null ? <button className="admin-org-locate" type="button" onClick={() => setSelectedOrganizationId(organization.organization_id)}>Show exact pin · {Number(organization.latitude).toFixed(5)}, {Number(organization.longitude).toFixed(5)}</button> : <p className="admin-org-no-pin">Exact map location not submitted</p>}<details><summary>Review history ({organization.review_history.length})</summary><ol>{organization.review_history.map((event, index) => <li key={`${organization.organization_id}-${event.reviewed_at}-${index}`}><strong>{String(event.status).replaceAll('_', ' ')}</strong><time>{new Date(event.reviewed_at).toLocaleString()}</time><span>{event.reviewer_name || 'Organization submitted'}</span>{event.notes && <p>{event.notes}</p>}</li>)}</ol></details></article>) : <p className="admin-org-empty">No organization records for this division yet.</p>}</div>
        </div>}
      </section>

      <section className="admin-workspace-lower" aria-label="Administration tools">
        <article className="admin-audit-card"><div><p className="admin-workspace-eyebrow">ACCOUNTABILITY</p><h2>Recent admin activity</h2><p>Review the audit trail for decisions and important changes.</p></div><strong>{loading ? '…' : errors.includes('audit') ? '—' : counts.audit ?? 0}<small> recorded events</small></strong><a href="#admin-operations?tab=audit">Open audit history <span aria-hidden="true">→</span></a></article>
        <aside className="admin-boundary-note"><span aria-hidden="true">i</span><p><strong>Decisions stay distinct.</strong> Staff access grants a person a role. Organization review checks an organization’s records. Each decision has its own audit trail.</p></aside>
      </section>
    </main>
  </>
}
