import { useState } from 'react'
import { signup } from '../../api/auth'
import './Auth.css'

function SignupPage({ onLogin }) {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [dateOfBirth, setDateOfBirth] = useState('')
  const [gender, setGender] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const passwordsMatch =
    confirmPassword.length > 0 && password === confirmPassword

  async function handleSubmit(event) {
    event.preventDefault()

    setError('')
    setSuccess('')

    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setIsSubmitting(true)

    try {
      const data = await signup({
        username,
        email,
        dateOfBirth,
        gender,
        password,
      })

      setSuccess(data.message)

      setUsername('')
      setEmail('')
      setDateOfBirth('')
      setGender('')
      setPassword('')
      setConfirmPassword('')
    } catch (err) {
      setError(err.message)
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
          <p className="auth-eyebrow">GET STARTED</p>

          <h1>Create your CareLife account</h1>

          <p className="auth-description">
            Create an account to get started with CareLife.
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
            <div className="form-field">
              <label htmlFor="signup-username">Username</label>

              <input
                id="signup-username"
                name="username"
                type="text"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="Enter your username"
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="signup-email">Email address</label>

              <input
                id="signup-email"
                name="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="signup-date-of-birth">
                Date of Birth
              </label>

              <input
                id="signup-date-of-birth"
                name="dateOfBirth"
                type="date"
                value={dateOfBirth}
                onChange={(event) => setDateOfBirth(event.target.value)}
                required
              />
            </div>

            <div className="form-field">
              <label htmlFor="signup-gender">Gender</label>

              <select
                id="signup-gender"
                name="gender"
                value={gender}
                onChange={(event) => setGender(event.target.value)}
                required
              >
                <option value="" disabled>
                  Select your gender
                </option>

                <option value="female">Female</option>

                <option value="male">Male</option>

                <option value="other">Other</option>

                <option value="prefer_not_to_say">
                  Prefer not to say
                </option>
              </select>
            </div>

            <div className="form-field">
              <label htmlFor="signup-password">Password</label>

              <div className="password-input">
                <input
                  id="signup-password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="At least 8 characters"
                  minLength={8}
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword((current) => !current)
                  }
                  aria-label={
                    showPassword ? 'Hide password' : 'Show password'
                  }
                >
                  {showPassword ? 'Hide' : 'Show'}
                </button>
              </div>

              <small>
                Password must contain at least 8 characters.
              </small>
            </div>

            <div className="form-field">
              <label htmlFor="signup-confirm-password">
                Confirm Password
              </label>

              <div className="password-input">
                <input
                  id="signup-confirm-password"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(event) =>
                    setConfirmPassword(event.target.value)
                  }
                  placeholder="Re-enter your password"
                  minLength={8}
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowConfirmPassword((current) => !current)
                  }
                  aria-label={
                    showConfirmPassword
                      ? 'Hide confirm password'
                      : 'Show confirm password'
                  }
                >
                  {showConfirmPassword ? 'Hide' : 'Show'}
                </button>
              </div>

              {passwordsMatch && (
                <small className="password-match">
                  ✓ Passwords match
                </small>
              )}
            </div>

            <button
              type="submit"
              className="auth-submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Creating account...' : 'Sign Up'}
            </button>
          </form>

          <p className="auth-switch">
            Already have an account?{' '}
            <button type="button" onClick={onLogin}>
              Login
            </button>
          </p>
        </div>
      </section>
    </main>
  )
}

export default SignupPage