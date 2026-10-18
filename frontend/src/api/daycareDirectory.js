import { apiRequest } from './client'

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
  const path = query
    ? '/organizations/daycare?' + query
    : '/organizations/daycare'

  try {
    return await apiRequest(path, { authenticated: false })
  } catch (error) {
    throw new Error(
      error.status === 404
        ? 'The daycare directory is not available right now.'
        : 'Unable to load daycare directory. Please check your connection and try again.'
    )
  }
}

export async function getPublicDaycare(organizationId) {
  const safeId = encodeURIComponent(organizationId)

  try {
    return await apiRequest('/organizations/daycare/' + safeId, {
      authenticated: false,
    })
  } catch (error) {
    if (error.status === 404) {
      throw new Error('Verified daycare not found')
    }

    throw new Error('Unable to load daycare details. Please try again.')
  }
}
