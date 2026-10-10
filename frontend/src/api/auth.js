import { API_BASE_URL } from './config'

export async function signup({ email, password }) {
  const response = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
    }),
  })

  const data = await response.json()

  if (!response.ok) {
    if (response.status === 409) {
      throw new Error(
        'An account with this email already exists'
      )
    }

    if (response.status === 422) {
      throw new Error(
        'Please enter a valid email and password'
      )
    }

    throw new Error('Unable to create account')
  }

  return data
}

export async function login({ email, password }) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
    }),
  })

  const data = await response.json()

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Invalid email or password')
    }

    if (response.status === 422) {
      throw new Error(
        'Please enter a valid email and password'
      )
    }

    throw new Error('Unable to sign in')
  }

  return data
}

export async function logout() {
  const token = localStorage.getItem('carelife_access_token')

  if (token) {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      throw new Error('Logout failed')
    }
  }

  localStorage.removeItem('carelife_access_token')
  localStorage.removeItem('carelife_user')

  window.location.hash = '#login'
}