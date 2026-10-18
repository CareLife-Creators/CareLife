import { useState } from 'react'
import { signup } from '../../api/auth'
import './Auth.css'

function SignupPage({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSuccess('')
    setIsSubmitting(true)

    try {
      const data = await signup({ email: email.trim(), password })
      setSuccess(
        data && data.message
          ? data.message
          : 'Account created. You can now sign in with your email and password.'
      )
      setEmail('')
      setPassword('')
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Unable to create account. Please try again.'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card">
        <a className="auth-brand" href="#home" aria-label="CareLife home">
          <span className="auth-brand-icon">C</span>
          <span>CareLife</span>
        </a>

        <div className="auth-content">
          <p className="auth-eyebrow">GET STARTED</p>
          <h1>Create your account</h1>
          <p className="auth-description">
            Set up your CareLife sign-in to access available workspaces.
          </p>

          {error && <div className="auth-message auth-message-error" role="alert">{error}</div>}
          {success && <div className="auth-message auth-message-success" role="status">{success}</div>}

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="form-field">
              <label htmlFor="signup-email">Email address</label>
              <input
                id="signup-email"
                name="email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="signup-password">Password</label>
              <input
                id="signup-password"
                name="password"
                type="password"
                autoComplete="new-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="At least 8 characters"
                minLength={8}
                required
              />
              <small>Password must contain at least 8 characters.</small>
            </div>

            <button type="submit" className="auth-submit" disabled={isSubmitting}>
              {isSubmitting ? 'Creating account…' : 'Create account'}
            </button>
          </form>

          <p className="auth-switch">
            Already have an account?{' '}
            <button type="button" onClick={onLogin}>Sign in</button>
          </p>
          <a className="auth-home-link" href="#home">← Back to CareLife</a>
        </div>
      </section>
    </main>
  )
}

export default SignupPage
