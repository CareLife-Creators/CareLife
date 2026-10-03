import { useState } from 'react'
import './Auth.css'

function LoginPage({ onSignup }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)

 function handleSubmit(event) {
  event.preventDefault()
}

  return (
    <main className="auth-page">
      <section className="auth-card">
        <div className="auth-brand">
          <div className="auth-brand-icon">C</div>
          <span>CareLife</span>
        </div>

        <div className="auth-content">
          <p className="auth-eyebrow">WELCOME BACK</p>

          <h1>Sign in to CareLife</h1>

          <p className="auth-description">
            Access your CareLife account and continue managing your
            organization.
          </p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="form-field">
              <label htmlFor="email">Email address</label>

              <input
                id="email"
                name="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>

            <div className="form-field">
              <div className="password-label-row">
                <label htmlFor="password">Password</label>

                <button
                  type="button"
                  className="forgot-password"
                  onClick={() => console.log('Forgot password')}
                >
                  Forgot password?
                </button>
              </div>

              <div className="password-input">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Enter your password"
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
            </div>

            <button type="submit" className="auth-submit">
              Sign in
            </button>
          </form>

          <p className="auth-switch">
            Don't have an account?{' '}
            <button type="button" onClick={onSignup}>
              Create an account
            </button>
          </p>
        </div>
      </section>
    </main>
  )
}

export default LoginPage