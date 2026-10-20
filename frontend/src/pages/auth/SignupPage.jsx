import { useState } from 'react'
import { signup } from '../../api/auth'
import { SIGNUP_ROLE_OPTIONS } from '../../lib/roles'
import './Auth.css'

function isValidPhone(value) {
  const digits = value.replace(/\D/g, '')
  return /^[+()\d.\-\s]+$/.test(value) && digits.length >= 7 && digits.length <= 15
}

function SignupPage({ onLogin }) {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [role, setRole] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')

    if (!role) {
      setError('Choose how you will use CareLife.')
      return
    }
    if (!isValidPhone(phone.trim())) {
      setError('Enter a phone number with 7 to 15 digits.')
      return
    }
    if (password !== confirmPassword) {
      setError('The two passwords do not match.')
      return
    }

    setIsSubmitting(true)

    try {
      await signup({
        email: email.trim(),
        password,
        fullName: fullName.trim(),
        phone: phone.trim(),
        role,
      })
      setSubmitted(true)
      setPassword('')
      setConfirmPassword('')
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
          {submitted ? (
            <div className="auth-success-panel" role="status">
              <h1>Request received</h1>
              <p>
                Your details were submitted. Sign in with your email and password to continue.
                If you already had an account with this email, use your existing password.
              </p>
              <button type="button" className="auth-submit" onClick={onLogin}>
                Go to sign in
              </button>
            </div>
          ) : (
            <>
              <p className="auth-eyebrow">GET STARTED</p>
              <h1>Create your account</h1>
              <p className="auth-description">
                Tell us who you are so CareLife can show the right tools.
              </p>

              {error && (
                <div className="auth-message auth-message-error" role="alert">{error}</div>
              )}

              <form className="auth-form" onSubmit={handleSubmit}>
                <div className="form-field">
                  <label htmlFor="signup-name">Full name</label>
                  <input
                    id="signup-name"
                    name="full_name"
                    type="text"
                    autoComplete="name"
                    value={fullName}
                    onChange={(event) => setFullName(event.target.value)}
                    placeholder="Your full name"
                    maxLength={200}
                    required
                  />
                </div>

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
                  <label htmlFor="signup-phone">Phone number</label>
                  <input
                    id="signup-phone"
                    name="phone"
                    type="tel"
                    autoComplete="tel"
                    value={phone}
                    onChange={(event) => setPhone(event.target.value)}
                    placeholder="+8801XXXXXXXXX"
                    maxLength={30}
                    required
                  />
                </div>

                <fieldset className="role-fieldset">
                  <legend>I am joining as</legend>
                  <div className="role-options">
                    {SIGNUP_ROLE_OPTIONS.map((option) => (
                      <label
                        key={option.value}
                        className={role === option.value ? 'role-option selected' : 'role-option'}
                      >
                        <input
                          type="radio"
                          name="role"
                          value={option.value}
                          checked={role === option.value}
                          onChange={() => setRole(option.value)}
                          required
                        />
                        <span>
                          <strong>{option.label}</strong>
                          <small>{option.hint}</small>
                        </span>
                      </label>
                    ))}
                  </div>
                </fieldset>

                <p className="auth-staff-note">
                  Work at a daycare, orphanage or care home? Create your account first, then
                  request staff access after you sign in. A CareLife administrator reviews each request.
                </p>

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
                </div>

                <div className="form-field">
                  <label htmlFor="signup-confirm">Confirm password</label>
                  <input
                    id="signup-confirm"
                    name="confirm_password"
                    type="password"
                    autoComplete="new-password"
                    value={confirmPassword}
                    onChange={(event) => setConfirmPassword(event.target.value)}
                    placeholder="Type the password again"
                    minLength={8}
                    required
                  />
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
            </>
          )}
        </div>
      </section>
    </main>
  )
}

export default SignupPage