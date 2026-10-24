import { useEffect, useState } from 'react'
import { getOrganizationVerification } from '../../api/organizationVerification'
import SiteNav from '../../components/SiteNav'
import { useSession } from '../../lib/session'
import './VerificationStatusPage.css'

function formatDate(value) {
  if (!value) return 'Not provided'

  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return 'Not provided'

  return parsed.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function statusLabel(status) {
  const labels = {
    pending: 'Pending review',
    approved: 'Verified',
    rejected: 'Needs attention',
    expired: 'Verification expired',
  }
  return labels[String(status || '').toLowerCase()] || 'Status unavailable'
}

function VerificationStatusPage() {
  const { organizationRoles = [] } = useSession()
  const [selectedOrganizationId, setSelectedOrganizationId] = useState(
    organizationRoles[0]?.organization_id || ''
  )
  const organizationId = organizationRoles.some((item) => item.organization_id === selectedOrganizationId)
    ? selectedOrganizationId
    : (organizationRoles[0]?.organization_id || '')
  const [organization, setOrganization] = useState(null)
  const [loading, setLoading] = useState(Boolean(organizationRoles[0]?.organization_id))
  const [error, setError] = useState('')

  async function loadVerification(event) {
    if (event) event.preventDefault()

    const requestedId = organizationId.trim()
    if (!requestedId) {
      setError('Enter your organization ID to continue.')
      setOrganization(null)
      return
    }

    setLoading(true)
    setError('')
    setOrganization(null)

    try {
      const data = await getOrganizationVerification(requestedId)
      setOrganization(data)
      localStorage.setItem('carelife_organization_id', requestedId)
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'Unable to load verification status. Please try again.'
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!organizationId.trim()) return undefined
    let cancelled = false
    getOrganizationVerification(organizationId.trim())
      .then((data) => {
        if (cancelled) return
        setOrganization(data)
        setError('')
        localStorage.setItem('carelife_organization_id', organizationId.trim())
      })
      .catch((requestError) => {
        if (!cancelled) setError(requestError instanceof Error ? requestError.message : 'Unable to load verification status. Please try again.')
      })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [organizationId])


  const status = String(organization?.status || 'pending').toLowerCase()
  const label = statusLabel(status)

  return (
    <>
      <SiteNav />
      <div className="app-layout verification-shell">
      <main className="main-content">
        <section className="page-content verification-page-content">
          <div className="verification-intro">
            <div>
              <span className="section-label">ORGANIZATION WORKSPACE</span>
              <h3>Organization verification</h3>
              <p>Check the review status for an organization you are authorized to manage.</p>
              <a className="verification-workspace-link" href="#organization-workspace">Back to organization workspace</a>
            </div>
          </div>

          <section className="card verification-lookup-card">
            <div className="card-header">
              <div>
                <span className="section-label">LOOK UP STATUS</span>
                <h4>Organization ID</h4>
              </div>
            </div>
            {organizationRoles.length > 1 && <label className="verification-field">Organization<select value={organizationId} onChange={(event) => { setLoading(true); setOrganization(null); setSelectedOrganizationId(event.target.value) }}>{organizationRoles.map((item) => <option key={item.organization_id} value={item.organization_id}>{String(item.organization_role).replaceAll('_', ' ')} · {item.organization_id}</option>)}</select></label>}
            {!organizationId && <p className="verification-error" role="status">No approved organization access is linked to this account yet. Submitted applications can be tracked from the organization application page.</p>}
            {organizationId && <p className="verification-org-id">Organization reference: {organizationId}</p>}
            {error && <p className="verification-error" role="alert">{error}</p>}
          </section>

          {loading && (
            <div className="verification-state-card" role="status">
              <span className="verification-spinner" aria-hidden="true" />
              <div><strong>Loading verification</strong><p>Retrieving the latest saved organization status.</p></div>
            </div>
          )}

          {!loading && organization && (
            <>
              <div className="intro verification-result-intro">
                <div>
                  <span className="section-label">VERIFICATION RESULT</span>
                  <h3>{organization.organization_name || 'Organization verification'}</h3>
                  <p>{organization.organization_type || 'Organization'}</p>
                </div>
                <button type="button" className="refresh-button" onClick={() => { void loadVerification() }}>
                  Refresh status
                </button>
              </div>

              <div className={'status-hero verification-status-' + status}>
                <div className="status-icon" aria-hidden="true">
                  {status === 'approved' ? '✓' : status === 'rejected' || status === 'expired' ? '!' : '…'}
                </div>
                <div className="status-content">
                  <span className="status-label">CURRENT STATUS</span>
                  <h4>{label}</h4>
                  <p>{organization.message || 'No additional verification message is available.'}</p>
                </div>
                <span className="status-pill">{label}</span>
              </div>

              <div className="content-grid">
                <section className="card">
                  <div className="card-header">
                    <div>
                      <span className="section-label">APPLICATION DETAILS</span>
                      <h4>Verification information</h4>
                    </div>
                  </div>
                  <div className="details-grid">
                    <div className="detail-item"><span>Organization ID</span><strong>{organizationId}</strong></div>
                    <div className="detail-item"><span>Submitted date</span><strong>{formatDate(organization.submitted_at)}</strong></div>
                    <div className="detail-item"><span>Last updated</span><strong>{formatDate(organization.updated_at)}</strong></div>
                    <div className="detail-item"><span>Organization type</span><strong>{organization.organization_type || 'Not provided'}</strong></div>
                  </div>
                </section>

                <section className="card">
                  <div className="card-header">
                    <div>
                      <span className="section-label">WHAT HAPPENS NEXT</span>
                      <h4>Verification progress</h4>
                    </div>
                  </div>
                  <div className="verification-next-step">
                    <span className="verification-next-icon" aria-hidden="true">
                      {status === 'approved' ? '✓' : status === 'rejected' ? '!' : status === 'expired' ? '!' : '↗'}
                    </span>
                    <div>
                      <strong>
                        {status === 'approved' ? 'Your organization is verified'
                          : status === 'rejected' ? 'Review the administrator message'
                            : status === 'expired' ? 'Update the expired verification documents'
                              : 'Await the administrator decision'}
                      </strong>
                      <p>
                        {status === 'approved' ? 'Keep the public organization information up to date.'
                          : status === 'rejected' ? 'Use the decision message to understand what needs attention.'
                            : status === 'expired' ? 'Contact your organization administrator about renewal.'
                              : 'You can return to this page later to refresh the saved status.'}
                      </p>
                    </div>
                  </div>
                </section>
              </div>
            </>
          )}
        </section>
      </main>
      </div>
    </>
  )
}

export default VerificationStatusPage
