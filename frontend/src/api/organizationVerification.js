import { apiRequest } from './client'

export async function getOrganizationVerification(organizationId) {
  if (!organizationId || !String(organizationId).trim()) {
    throw new Error('Enter your organization ID to view verification status.')
  }
  const safeId = encodeURIComponent(String(organizationId).trim())
  try {
    return await apiRequest('/organizations/' + safeId + '/verification-status')
  } catch (error) {
    if (error.status === 401) throw new Error('Your session has expired. Please sign in again.', { cause: error })
    if (error.status === 403) throw new Error('You do not have access to this organization.', { cause: error })
    if (error.status === 404) throw new Error('Verification information was not found for that organization ID.', { cause: error })
    throw new Error('Unable to load verification status. Please try again.', { cause: error })
  }
}
