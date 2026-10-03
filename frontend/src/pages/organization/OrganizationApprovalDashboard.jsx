import { useEffect, useState } from 'react'
import {
  approveOrganization,
  getPendingOrganizations,
  rejectOrganization,
} from '../../api/organizationApproval'
import './OrganizationApprovalDashboard.css'

function OrganizationApprovalDashboard() {
  const [organizations, setOrganizations] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionMessage, setActionMessage] = useState('')
  const [processingId, setProcessingId] = useState('')
  const [rejectingId, setRejectingId] = useState('')
  const [rejectMessage, setRejectMessage] = useState('')

  async function loadOrganizations() {
    setIsLoading(true)
    setError('')
    setActionMessage('')

    try {
      const data = await getPendingOrganizations()
      setOrganizations(data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load pending organizations'
      )
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    let cancelled = false

    getPendingOrganizations()
      .then((data) => {
        if (cancelled) {
          return
        }

        setOrganizations(data)
        setError('')
        setActionMessage('')
      })
      .catch((err) => {
        if (cancelled) {
          return
        }

        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load pending organizations'
        )
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  async function handleApprove(organizationId) {
    setProcessingId(organizationId)
    setError('')
    setActionMessage('')

    try {
      await approveOrganization(organizationId)

      setOrganizations((current) =>
        current.filter(
          (organization) =>
            organization.organization_id !== organizationId
        )
      )

      setActionMessage('Organization approved successfully.')
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to approve organization'
      )
    } finally {
      setProcessingId('')
    }
  }

  async function handleReject(organizationId) {
    setProcessingId(organizationId)
    setError('')
    setActionMessage('')

    try {
      await rejectOrganization(
        organizationId,
        rejectMessage.trim() || null
      )

      setOrganizations((current) =>
        current.filter(
          (organization) =>
            organization.organization_id !== organizationId
        )
      )

      setRejectingId('')
      setRejectMessage('')
      setActionMessage('Organization rejected successfully.')
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to reject organization'
      )
    } finally {
      setProcessingId('')
    }
  }

  function formatDate(value) {
    return new Date(value).toLocaleString()
  }

  return (
    <main className="approval-dashboard">
      <div className="approval-dashboard-container">
        <header className="approval-header">
          <div>
            <p className="approval-eyebrow">CareLife Admin</p>

            <h1>Organization Approval Dashboard</h1>

            <p className="approval-description">
              Review pending organizations and approve or reject
              their verification requests.
            </p>
          </div>

          <button
            type="button"
            className="approval-refresh-button"
            onClick={loadOrganizations}
            disabled={isLoading}
          >
            {isLoading ? 'Refreshing...' : 'Refresh'}
          </button>
        </header>

        <section className="approval-summary">
          <div className="approval-summary-card">
            <span>Pending organizations</span>
            <strong>{organizations.length}</strong>
          </div>
        </section>

        {error && (
          <div className="approval-message approval-message-error">
            {error}
          </div>
        )}

        {actionMessage && (
          <div className="approval-message approval-message-success">
            {actionMessage}
          </div>
        )}

        {isLoading ? (
          <div className="approval-empty-state">
            Loading pending organizations...
          </div>
        ) : error ? null : organizations.length === 0 ? (
          <div className="approval-empty-state">
            <h2>No pending organizations</h2>

            <p>
              There are currently no organization verification
              requests waiting for review.
            </p>
          </div>
        ) : (
          <section className="approval-list">
            {organizations.map((organization) => {
              const isProcessing =
                processingId === organization.organization_id

              const isRejecting =
                rejectingId === organization.organization_id

              return (
                <article
                  className="approval-card"
                  key={organization.organization_id}
                >
                  <div className="approval-card-content">
                    <div className="approval-card-heading">
                      <div>
                        <h2>{organization.organization_name}</h2>

                        <p>{organization.organization_type}</p>
                      </div>

                      <span className="approval-status">
                        {organization.status}
                      </span>
                    </div>

                    <div className="approval-details">
                      <div>
                        <span>Organization ID</span>

                        <strong>
                          {organization.organization_id}
                        </strong>
                      </div>

                      <div>
                        <span>Submitted</span>

                        <strong>
                          {formatDate(
                            organization.submitted_at
                          )}
                        </strong>
                      </div>

                      <div>
                        <span>Last updated</span>

                        <strong>
                          {formatDate(
                            organization.updated_at
                          )}
                        </strong>
                      </div>
                    </div>

                    {organization.message && (
                      <div className="approval-existing-message">
                        <span>Message</span>

                        <p>{organization.message}</p>
                      </div>
                    )}

                    {isRejecting && (
                      <div className="approval-reject-form">
                        <label
                          htmlFor={`reject-${organization.organization_id}`}
                        >
                          Rejection message
                        </label>

                        <textarea
                          id={`reject-${organization.organization_id}`}
                          value={rejectMessage}
                          onChange={(event) =>
                            setRejectMessage(
                              event.target.value
                            )
                          }
                          placeholder="Optional message for the organization"
                          rows={4}
                          disabled={isProcessing}
                        />
                      </div>
                    )}
                  </div>

                  <div className="approval-card-actions">
                    <button
                      type="button"
                      className="approval-approve-button"
                      onClick={() =>
                        handleApprove(
                          organization.organization_id
                        )
                      }
                      disabled={isProcessing}
                    >
                      {isProcessing && !isRejecting
                        ? 'Approving...'
                        : 'Approve'}
                    </button>

                    {!isRejecting ? (
                      <button
                        type="button"
                        className="approval-reject-button"
                        onClick={() => {
                          setRejectingId(
                            organization.organization_id
                          )
                          setRejectMessage('')
                        }}
                        disabled={isProcessing}
                      >
                        Reject
                      </button>
                    ) : (
                      <>
                        <button
                          type="button"
                          className="approval-reject-confirm-button"
                          onClick={() =>
                            handleReject(
                              organization.organization_id
                            )
                          }
                          disabled={isProcessing}
                        >
                          {isProcessing
                            ? 'Rejecting...'
                            : 'Confirm rejection'}
                        </button>

                        <button
                          type="button"
                          className="approval-cancel-button"
                          onClick={() => {
                            setRejectingId('')
                            setRejectMessage('')
                          }}
                          disabled={isProcessing}
                        >
                          Cancel
                        </button>
                      </>
                    )}
                  </div>
                </article>
              )
            })}
          </section>
        )}
      </div>
    </main>
  )
}

export default OrganizationApprovalDashboard