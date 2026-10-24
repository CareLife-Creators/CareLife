const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
).replace(/\/+$/, '')

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function responseMessage(payload, status) {
  if (payload && typeof payload === 'object') {
    if (typeof payload.detail === 'string') {
      return payload.detail
    }

    if (Array.isArray(payload.detail)) {
      return payload.detail
        .map((item) => item && item.msg ? item.msg : '')
        .filter(Boolean)
        .join(' · ')
    }

    if (typeof payload.message === 'string') {
      return payload.message
    }

    if (typeof payload.error === 'string') {
      return payload.error
    }
  }

  if (typeof payload === 'string' && payload.trim()) {
    return payload.trim()
  }

  return 'Request failed (' + status + ')'
}

export async function apiRequest(path, options = {}) {
  const {
    authenticated = true,
    headers: suppliedHeaders,
    ...requestOptions
  } = options

  const headers = new Headers(suppliedHeaders || {})
  const token = localStorage.getItem('carelife_access_token')

  const isFormData = typeof FormData !== 'undefined' && requestOptions.body instanceof FormData
  if (requestOptions.body !== undefined && !isFormData && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  if (authenticated && token && !headers.has('Authorization')) {
    headers.set('Authorization', 'Bearer ' + token)
  }

  const response = await fetch(API_BASE_URL + path, {
    ...requestOptions,
    headers,
    credentials: 'include',
  })

  if (response.status === 204) {
    if (!response.ok) {
      throw new ApiError('Request failed (' + response.status + ')', response.status)
    }
    return null
  }

  const responseText = await response.text()
  let payload = null

  if (responseText) {
    try {
      payload = JSON.parse(responseText)
    } catch {
      payload = responseText
    }
  }

  if (!response.ok) {
    throw new ApiError(responseMessage(payload, response.status), response.status)
  }

  return payload
}

export { API_BASE_URL }
