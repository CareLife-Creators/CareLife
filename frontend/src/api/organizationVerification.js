import { API_BASE_URL } from './config'

export async function getOrganizationVerification(
  organizationId
) {
  const response = await fetch(
    `${API_BASE_URL}/organizations/${organizationId}/verification-status`, {
      credentials: 'include',
    }
  )

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Authentication required')
    }

    if (response.status === 403) {
      throw new Error(
        'You do not have access to this organization'
      )
    }

    if (response.status === 404) {
      throw new Error(
        'Verification information not found'
      )
    }

    throw new Error('Unable to load verification status')
  }

  return response.json()
}