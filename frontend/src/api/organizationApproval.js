import { API_BASE_URL } from './config'


export async function getPendingOrganizations() {
  const response = await fetch(
    `${API_BASE_URL}/organizations/verification/pending`,
    {
      credentials: 'include',
    }
  )

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Authentication required')
    }

    if (response.status === 403) {
      throw new Error('Admin access required')
    }

    throw new Error('Unable to load pending organizations')
  }

  return response.json()
}

export async function approveOrganization(organizationId) {
  const response = await fetch(
    `${API_BASE_URL}/organizations/${organizationId}/verification/approve`,
    {
      method: 'POST',
      credentials: 'include',
    }
  )

  if (!response.ok) {
    throw new Error('Unable to approve organization')
  }

  return response.json()
}

export async function rejectOrganization(
  organizationId,
  message = null
) {
  const response = await fetch(
    `${API_BASE_URL}/organizations/${organizationId}/verification/reject`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        message,
      }),
    }
  )

  if (!response.ok) {
    throw new Error('Unable to reject organization')
  }

  return response.json()
}