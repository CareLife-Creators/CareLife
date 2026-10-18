import { useState } from 'react'
import { getOrganizationVerification } from '../../api/organizationVerification'
import { logout } from '../../api/auth'
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
  const [organizationId, setOrganizationId] = useState(
    localStorage.getItem('carelife_organization_id') || ''
  )
  const [organization, setOrganization] = useState(null)
  const [loading, setLoading] = useState(false)
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


  const status = String(organization?.status || 'pending').toLowerCase()
  const label = statusLabel(status)
  const email = localStorage.getItem('carelife_user') || 'Signed-in member'

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <a className="brand verification-brand" href="#home">
          <span className="brand-icon">C</span>
          <span className="verification-brand-copy">
            <strong>CareLife</strong>
            <small>Care management</small>
          </span>
        </a>

        <nav className="navigation" aria-label="Organization navigation">
          <a href="#home" className="nav-item"><span aria-hidden="true">⌂</span> Home</a>
          <a href="#daycare-directory" className="nav-item"><span aria-hidden="true">⌕</span> Daycare directory</a>
          <a href="#verification" className="nav-item active" aria-current="page"><span aria-hidden="true">✓</span> Verification status</a>
          <a href="#organization-approval" className="nav-item"><span aria-hidden="true">◎</span> Admin approvals</a>
        </nav>

        <div className="sidebar-bottom">
          <div className="help-box">
            <strong>Need help?</strong>
            <p>Use the organization ID provided by your CareLife administrator to check verification.</p>
            <span className="verification-help-caption">Ask your CareLife administrator if you need help finding your organization ID.</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="breadcrumb">Organization / Verification</p>
            <h2>Verification status</h2>
          </div>
          <div className="profile">
            <div className="profile-avatar" aria-hidden="true">{email.charAt(0).toUpperCase()}</div>
            <div className="verification-profile-copy">
              <strong>{email}</strong>
              <span>Signed-in account</span>
            </div>
            <button type="button" onClick={() => { void logout() }}>Sign out</button>
          </div>
        </header>

        <section className="page-content verification-page-content">
          <div className="verification-intro">
            <div>
              <span className="section-label">ORGANIZATION WORKSPACE</span>
              <h3>Know where your verification stands.</h3>
              <p>Enter the organization ID you are authorized to view. CareLife will load the saved status from the service.</p>
            </div>
          </div>

          <section className="card verification-lookup-card">
            <div className="card-header">
              <div>
                <span className="section-label">LOOK UP STATUS</span>
                <h4>Organization ID</h4>
              </div>
            </div>
            <form className="verification-lookup" onSubmit={loadVerification}>
              <div className="verification-field">
                <label htmlFor="verification-organization-id">Organization ID</label>
                <input
                  id="verification-organization-id"
                  name="organizationId"
                  value={organizationId}
                  onChange={(event) => setOrganizationId(event.target.value)}
                  placeholder="Enter your organization ID"
                  autoComplete="off"
                  required
                />
              </div>
              <button type="submit" className="verification-submit" disabled={loading}>
                {loading ? 'Loading status…' : 'View status'}
              </button>
            </form>
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
  )
}

export default VerificationStatusPage
