import { useState } from 'react'
import {
  confirmPasswordReset,
  requestPasswordReset,
} from '../../api/passwordReset'
import './Auth.css'

function ResetPasswordPage() {
  const token =
    new URLSearchParams(window.location.search).get('token') ||
    new URLSearchParams(
      window.location.hash.split('?')[1] || ''
    ).get('token')

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSuccess('')

    if (token && password !== confirmPassword) {
      setError('The passwords do not match.')
      return
    }

    setIsSubmitting(true)

    try {
      const result = token
        ? await confirmPasswordReset({
            token,
            newPassword: password,
          })
        : await requestPasswordReset(email)

      setSuccess(result.message)
      setPassword('')
      setConfirmPassword('')
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to process password reset'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-brand">
          <div className="auth-brand-icon">C</div>
          <span>CareLife</span>
        </div>

        <div className="auth-content">
          <p className="auth-eyebrow">ACCOUNT RECOVERY</p>

          <h1>{token ? 'Set a new password' : 'Reset your password'}</h1>

          <p className="auth-description">
            {token
              ? 'Choose a new password for your CareLife account.'
              : 'Enter your email address and we will send a reset link if an account exists.'}
          </p>

          {error && (
            <div className="auth-message auth-message-error">
              {error}
            </div>
          )}

          {success && (
            <div className="auth-message auth-message-success">
              {success}
            </div>
          )}

          <form className="auth-form" onSubmit={handleSubmit}>
            {token ? (
              <>
                <div className="form-field">
                  <label htmlFor="reset-password">New password</label>
                  <input
                    id="reset-password"
                    name="new-password"
                    type="password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    autoComplete="new-password"
                    minLength={8}
                    required
                  />
                </div>

                <div className="form-field">
                  <label htmlFor="confirm-reset-password">
                    Confirm new password
                  </label>
                  <input
                    id="confirm-reset-password"
                    name="confirm-password"
                    type="password"
                    value={confirmPassword}
                    onChange={(event) => setConfirmPassword(event.target.value)}
                    autoComplete="new-password"
                    minLength={8}
                    required
                  />
                </div>
              </>
            ) : (
              <div className="form-field">
                <label htmlFor="reset-email">Email address</label>
                <input
                  id="reset-email"
                  name="email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  autoComplete="email"
                  placeholder="you@example.com"
                  required
                />
              </div>
            )}

            <button
              type="submit"
              className="auth-submit"
              disabled={isSubmitting}
            >
              {isSubmitting
                ? 'Please wait...'
                : token
                  ? 'Update password'
                  : 'Send reset link'}
            </button>
          </form>

          <p className="auth-switch">
            Remembered your password?{' '}
            <button
              type="button"
              onClick={() => {
                window.location.href = '/#login'
              }}
            >
              Back to sign in
            </button>
          </p>
        </div>
      </section>
    </main>
  )
}

export default ResetPasswordPage
