import { API_BASE_URL } from './config'


export async function getDaycareDirectory({
  search = '',
  location = '',
} = {}) {
  const params = new URLSearchParams()

  if (search.trim()) {
    params.set('search', search.trim())
  }

  if (location.trim()) {
    params.set('location', location.trim())
  }

  const query = params.toString()

  const url = query
    ? `${API_BASE_URL}/organizations/daycare?${query}`
    : `${API_BASE_URL}/organizations/daycare`

  const response = await fetch(url)

  if (!response.ok) {
    throw new Error(
      'Unable to load daycare directory'
    )
  }

  return response.json()
}


export async function getPublicDaycare(
  organizationId
) {
  const response = await fetch(
    `${API_BASE_URL}/organizations/daycare/${organizationId}`
  )

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(
        'Verified daycare not found'
      )
    }

    throw new Error(
      'Unable to load daycare details'
    )
  }

  return response.json()
}