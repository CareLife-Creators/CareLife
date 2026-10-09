const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  'http://127.0.0.1:8000'

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