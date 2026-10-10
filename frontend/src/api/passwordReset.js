import { API_BASE_URL } from './config'

async function postPasswordReset(path, payload, fallbackMessage) {
  const response = await fetch(`${API_BASE_URL}/auth/password-reset/${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    throw new Error(data.detail || fallbackMessage)
  }

  return data
}

export function requestPasswordReset(email) {
  return postPasswordReset(
    'request',
    { email },
    'Unable to request a password reset'
  )
}

export function confirmPasswordReset({ token, newPassword }) {
  return postPasswordReset(
    'confirm',
    {
      token,
      new_password: newPassword,
    },
    'Unable to reset password'
  )
}
