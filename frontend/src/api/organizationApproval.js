import { apiRequest } from './client'

function explainApprovalError(error, fallback) {
  if (error.status === 401) {
    return new Error('Please sign in to continue.')
  }

  if (error.status === 403) {
    return new Error('Admin access is required to manage organization approvals.')
  }

  return new Error(error.message || fallback)
}

export async function getPendingOrganizations() {
  try {
    return await apiRequest('/organizations/verification/pending')
  } catch (error) {
    throw explainApprovalError(error, 'Unable to load pending organizations')
  }
}

export async function approveOrganization(organizationId) {
  try {
    return await apiRequest(
      '/organizations/' + encodeURIComponent(organizationId) + '/verification/approve',
      { method: 'POST' }
    )
  } catch (error) {
    throw explainApprovalError(error, 'Unable to approve organization')
  }
}

export async function rejectOrganization(organizationId, message = null) {
  try {
    return await apiRequest(
      '/organizations/' + encodeURIComponent(organizationId) + '/verification/reject',
      {
        method: 'POST',
        body: JSON.stringify({ message }),
      }
    )
  } catch (error) {
    throw explainApprovalError(error, 'Unable to reject organization')
  }
}
