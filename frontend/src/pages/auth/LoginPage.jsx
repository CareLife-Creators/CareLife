import { useState } from 'react'
import CareLifeLogo from '../../components/CareLifeLogo'
import { login } from '../../api/auth'
import './Auth.css'

function AuthSide({ eyebrow, title, description }) {
  return (
    <aside className="auth-side" aria-label="About CareLife">
      <a className="auth-side-brand" href="#home" aria-label="CareLife home">
        <CareLifeLogo size={34} />
        <span>CareLife</span>
      </a>

      <div className="auth-side-body">
        <h2>{title}</h2>
        <p>{description}</p>
        <ul className="auth-side-modules" aria-label="CareLife modules">
          <li>Daycare</li>
          <li>Orphanage</li>
          <li>Elderly care</li>
        </ul>
        <p className="auth-side-trust">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 2l7 3v6c0 5-3.4 8.6-7 10-3.6-1.4-7-5-7-10V5l7-3z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
            <path d="M8.5 12l2.4 2.4L15.5 9.8" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span>
            CareLife reviews organizations, and a CareLife administrator approves every
            staff account — so the people you connect with are who they say they are.
          </span>
        </p>
      </div>

      <p className="auth-side-foot">{eyebrow}</p>
    </aside>
  )
}

function LoginPage({ onSignup }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      // login() saves the token, email and role for the whole app.
      await login({ email: email.trim(), password })
      window.location.hash = '#dashboard'
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Unable to sign in. Please try again.'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-shell">
        <AuthSide
          eyebrow="© 2026 CareLife"
          title="Care you can check on."
          description="Daycares, orphanages and elderly-care homes on one trusted platform. Follow attendance, support real needs, and stay close to the people you care for."
        />

        <section className="auth-card">
          <a className="auth-brand" href="#home" aria-label="CareLife home">
            <CareLifeLogo size={36} />
            <span>CareLife</span>
          </a>

          <div className="auth-content">
            <p className="auth-eyebrow">WELCOME BACK</p>
            <h1>Sign in to CareLife</h1>
            <p className="auth-description">
              Access your account and continue to the CareLife workspace.
            </p>

            {error && (
              <div className="auth-message auth-message-error" role="alert">
                {error}
              </div>
            )}

            <form className="auth-form" onSubmit={handleSubmit}>
              <div className="form-field">
                <label htmlFor="login-email">Email address</label>
                <input
                  id="login-email"
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
                <div className="password-label-row">
                  <label htmlFor="login-password">Password</label>
                  <button
                    type="button"
                    className="forgot-password"
                    onClick={() => { window.location.hash = '#password-reset' }}
                  >
                    Forgot password?
                  </button>
                </div>

                <div className="password-input">
                  <input
                    id="login-password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Enter your password"
                    minLength={8}
                    required
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowPassword((current) => !current)}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                    aria-pressed={showPassword}
                  >
                    {showPassword ? 'Hide' : 'Show'}
                  </button>
                </div>
              </div>

              <button type="submit" className="auth-submit" disabled={isSubmitting}>
                {isSubmitting ? 'Signing in…' : 'Sign in'}
              </button>
            </form>

            <p className="auth-switch">
              Don’t have an account?{' '}
              <button type="button" onClick={onSignup}>Create an account</button>
            </p>
            <a className="auth-home-link" href="#home">← Back to CareLife</a>
          </div>
        </section>
      </section>
    </main>
  )
}

export default LoginPage