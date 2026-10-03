
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

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
