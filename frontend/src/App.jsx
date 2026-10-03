import { useEffect, useState } from 'react'
import './App.css'
import {
  getOrganizationVerification,
} from './api/organizationVerification'
import OrganizationApprovalDashboard from './pages/organization/OrganizationApprovalDashboard'

const organizationId = 'daycare-1'

function formatDate(value) {
  if (!value) {
    return '—'
  }

  return new Date(value).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

function getStatusLabel(status) {
  const labels = {
    pending: 'Pending Verification',
    approved: 'Approved',
    rejected: 'Rejected',
    expired: 'Expired',
  }

  return labels[status] || status
}

function App() {
  const [organization, setOrganization] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const isApprovalDashboard =
    window.location.hash === '#organization-approval'

  async function loadVerificationStatus() {
    try {
      setLoading(true)
      setError('')

      const data = await getOrganizationVerification(
        organizationId
      )

      setOrganization(data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load verification status'
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isApprovalDashboard) {
      return undefined
    }

    let cancelled = false

    getOrganizationVerification(organizationId)
      .then((data) => {
        if (cancelled) {
          return
        }

        setOrganization(data)
        setError('')
      })
      .catch((err) => {
        if (cancelled) {
          return
        }

        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load verification status'
        )
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [isApprovalDashboard])

  if (isApprovalDashboard) {
    return <OrganizationApprovalDashboard />
  }

  const status = organization?.status || 'pending'
  const statusLabel = getStatusLabel(status)

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">C</div>

          <div>
            <h1>CareLife</h1>
            <p>Care Management</p>
          </div>
        </div>

        <nav className="navigation">
          <a href="#" className="nav-item">
            <span>⌂</span>
            Dashboard
          </a>

          <a href="#" className="nav-item active">
            <span>✓</span>
            Verification
          </a>

          <a href="#" className="nav-item">
            <span>▣</span>
            Organization Profile
          </a>

          <a href="#" className="nav-item">
            <span>⚙</span>
            Settings
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="help-box">
            <strong>Need help?</strong>

            <p>
              Contact CareLife support if you have questions
              about your verification.
            </p>

            <button type="button">Contact Support</button>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="breadcrumb">
              Organization / Verification
            </p>

            <h2>Verification Status</h2>
          </div>

          <div className="profile">
            <div className="profile-avatar">OS</div>

            <div>
              <strong>Organization Staff</strong>
              <span>Staff Account</span>
            </div>
          </div>
        </header>

        <section className="page-content">
          {loading && (
            <div className="notice">
              <div className="notice-icon">i</div>

              <div>
                <strong>
                  Loading verification status
                </strong>

                <p>
                  CareLife is retrieving the latest saved
                  verification information.
                </p>
              </div>
            </div>
          )}

          {!loading && error && (
            <div className="notice">
              <div className="notice-icon">!</div>

              <div>
                <strong>
                  Unable to load verification status
                </strong>

                <p>{error}</p>
              </div>
            </div>
          )}

          {!loading && !error && organization && (
            <>
              <div className="intro">
                <div>
                  <span className="section-label">
                    ORGANIZATION VERIFICATION
                  </span>

                  <h3>{organization.organization_name}</h3>

                  <p>{organization.organization_type}</p>
                </div>

                <button
                  type="button"
                  className="refresh-button"
                  onClick={loadVerificationStatus}
                >
                  ↻ Refresh Status
                </button>
              </div>

              <div className="status-hero">
                <div className="status-icon">
                  {status === 'approved'
                    ? '✓'
                    : status === 'rejected'
                      ? '!'
                      : status === 'expired'
                        ? '!'
                        : '•'}
                </div>

                <div className="status-content">
                  <span className="status-label">
                    CURRENT STATUS
                  </span>

                  <h4>{statusLabel}</h4>

                  <p>
                    {organization.message ||
                      'No additional verification message is available.'}
                  </p>
                </div>

                <span className="status-pill">
                  {status}
                </span>
              </div>

              <div className="content-grid">
                <section className="card">
                  <div className="card-header">
                    <div>
                      <span className="section-label">
                        VERIFICATION DETAILS
                      </span>

                      <h4>Application Information</h4>
                    </div>
                  </div>

                  <div className="details-grid">
                    <div className="detail-item">
                      <span>Submitted Date</span>

                      <strong>
                        {formatDate(
                          organization.submitted_at
                        )}
                      </strong>
                    </div>

                    <div className="detail-item">
                      <span>Last Updated</span>

                      <strong>
                        {formatDate(
                          organization.updated_at
                        )}
                      </strong>
                    </div>

                    <div className="detail-item">
                      <span>Organization Type</span>

                      <strong>
                        {organization.organization_type}
                      </strong>
                    </div>

                    <div className="detail-item">
                      <span>Verification Status</span>

                      <strong>{statusLabel}</strong>
                    </div>
                  </div>
                </section>

                <section className="card">
                  <div className="card-header">
                    <div>
                      <span className="section-label">
                        VERIFICATION PROGRESS
                      </span>

                      <h4>Application Timeline</h4>
                    </div>
                  </div>

                  <div className="timeline">
                    <div className="timeline-item completed">
                      <div className="timeline-dot">
                        ✓
                      </div>

                      <div>
                        <strong>
                          Application Submitted
                        </strong>

                        <span>
                          {formatDate(
                            organization.submitted_at
                          )}
                        </span>
                      </div>
                    </div>

                    <div className="timeline-line"></div>

                    <div
                      className={
                        status === 'pending'
                          ? 'timeline-item current'
                          : 'timeline-item completed'
                      }
                    >
                      <div className="timeline-dot">
                        {status === 'pending' ? '•' : '✓'}
                      </div>

                      <div>
                        <strong>Under Review</strong>

                        <span>
                          {status === 'pending'
                            ? 'Currently being reviewed'
                            : 'Review stage completed'}
                        </span>
                      </div>
                    </div>

                    <div className="timeline-line"></div>

                    <div
                      className={
                        status === 'pending'
                          ? 'timeline-item upcoming'
                          : 'timeline-item completed'
                      }
                    >
                      <div className="timeline-dot">
                        {status === 'pending'
                          ? '3'
                          : '✓'}
                      </div>

                      <div>
                        <strong>
                          Verification Decision
                        </strong>

                        <span>
                          {status === 'pending'
                            ? 'Waiting for administration review'
                            : `Current result: ${statusLabel}`}
                        </span>
                      </div>
                    </div>
                  </div>
                </section>
              </div>

              <div className="notice">
                <div className="notice-icon">i</div>

                <div>
                  <strong>
                    Keep your organization information up to
                    date
                  </strong>

                  <p>
                    Verification decisions are based on the
                    information submitted by your
                    organization. Make sure your profile
                    information stays accurate.
                  </p>
                </div>
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  )
}

export default App