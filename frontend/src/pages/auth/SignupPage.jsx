import { useState } from 'react'
import CareLifeLogo from '../../components/CareLifeLogo'
import { signup } from '../../api/auth'
import { SIGNUP_ROLE_OPTIONS } from '../../lib/roles'
import './Auth.css'

function isValidPhone(value) {
  const digits = value.replace(/\D/g, '')
  return /^[+()\d.\-\s]+$/.test(value) && digits.length >= 7 && digits.length <= 15
}

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
      <section className="auth-shell">
        <AuthSide
          eyebrow="© 2026 CareLife"
          title="One account, three ways to care."
          description="Join CareLife to find daycare, support orphanages with transparent donations, or arrange elderly care — with verified organizations and real status tracking."
        />

        <section className="auth-card">
          <a className="auth-brand" href="#home" aria-label="CareLife home">
            <CareLifeLogo size={36} />
            <span>CareLife</span>
          </a>

          <div className="auth-content">
            {submitted ? (
              <div className="auth-success-panel" role="status">
                <div className="auth-success-icon" aria-hidden="true">
                  <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                    <path d="M4.5 12.5l5 5L19.5 7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </div>
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
      </section>
    </main>
  )
}

export default SignupPage