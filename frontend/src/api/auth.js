import { apiRequest } from './client'

function translateAuthError(error, action) {
  if (error.status === 409) {
    return new Error('An account with this email already exists')
  }

  if (error.status === 422) {
    return new Error('Please enter a valid email and password')
  }

  if (action === 'login' && error.status === 401) {
    return new Error('Invalid email or password')
  }

  return new Error(
    action === 'signup' ? 'Unable to create account: ' + error.message
      : 'Unable to sign in: ' + error.message
  )
}

export async function signup({ email, password }) {
  try {
    return await apiRequest('/auth/signup', {
      method: 'POST',
      authenticated: false,
      body: JSON.stringify({ email, password }),
    })
  } catch (error) {
    throw translateAuthError(error, 'signup')
  }
}

export async function login({ email, password }) {
  try {
    return await apiRequest('/auth/login', {
      method: 'POST',
      authenticated: false,
      body: JSON.stringify({ email, password }),
    })
  } catch (error) {
    throw translateAuthError(error, 'login')
  }
}

export async function logout() {
  const token = localStorage.getItem('carelife_access_token')

  try {
    if (token) {
      await apiRequest('/auth/logout', { method: 'POST' })
    }
  } catch {
    // Always clear the local session, even when the API is unavailable.
  } finally {
    localStorage.removeItem('carelife_access_token')
    localStorage.removeItem('carelife_user')
    localStorage.removeItem('carelife_organization_id')
    window.location.hash = '#home'
  }
}
