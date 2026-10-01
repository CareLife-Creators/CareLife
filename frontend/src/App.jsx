import './App.css'

function App() {
  const organization = {
    name: 'Sunshine Daycare Center',
    type: 'Daycare Organization',
    status: 'Pending Verification',
    submittedDate: 'September 28, 2026',
    lastUpdated: 'October 1, 2026',
    message:
      'Your organization registration has been received and is currently being reviewed by the CareLife administration team.',
  }

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
            <p>Contact CareLife support if you have questions about your verification.</p>
            <button type="button">Contact Support</button>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="breadcrumb">Organization / Verification</p>
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
          <div className="intro">
            <div>
              <span className="section-label">ORGANIZATION VERIFICATION</span>
              <h3>{organization.name}</h3>
              <p>{organization.type}</p>
            </div>

            <button
              type="button"
              className="refresh-button"
              onClick={() => window.location.reload()}
            >
              ↻ Refresh Status
            </button>
          </div>

          <div className="status-hero">
            <div className="status-icon">!</div>

            <div className="status-content">
              <span className="status-label">CURRENT STATUS</span>
              <h4>{organization.status}</h4>
              <p>{organization.message}</p>
            </div>

            <span className="status-pill">Pending</span>
          </div>

          <div className="content-grid">
            <section className="card">
              <div className="card-header">
                <div>
                  <span className="section-label">VERIFICATION DETAILS</span>
                  <h4>Application Information</h4>
                </div>
              </div>

              <div className="details-grid">
                <div className="detail-item">
                  <span>Submitted Date</span>
                  <strong>{organization.submittedDate}</strong>
                </div>

                <div className="detail-item">
                  <span>Last Updated</span>
                  <strong>{organization.lastUpdated}</strong>
                </div>

                <div className="detail-item">
                  <span>Organization Type</span>
                  <strong>{organization.type}</strong>
                </div>

                <div className="detail-item">
                  <span>Verification Status</span>
                  <strong>{organization.status}</strong>
                </div>
              </div>
            </section>

            <section className="card">
              <div className="card-header">
                <div>
                  <span className="section-label">VERIFICATION PROGRESS</span>
                  <h4>Application Timeline</h4>
                </div>
              </div>

              <div className="timeline">
                <div className="timeline-item completed">
                  <div className="timeline-dot">✓</div>

                  <div>
                    <strong>Application Submitted</strong>
                    <span>September 28, 2026</span>
                  </div>
                </div>

                <div className="timeline-line"></div>

                <div className="timeline-item current">
                  <div className="timeline-dot">•</div>

                  <div>
                    <strong>Under Review</strong>
                    <span>Currently being reviewed</span>
                  </div>
                </div>

                <div className="timeline-line"></div>

                <div className="timeline-item upcoming">
                  <div className="timeline-dot">3</div>

                  <div>
                    <strong>Verification Decision</strong>
                    <span>Waiting for administration review</span>
                  </div>
                </div>
              </div>
            </section>
          </div>

          <div className="notice">
            <div className="notice-icon">i</div>

            <div>
              <strong>Keep your organization information up to date</strong>
              <p>
                Verification decisions are based on the information submitted
                by your organization. Make sure your profile information stays
                accurate.
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App