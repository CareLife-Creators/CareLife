import { useEffect, useState } from 'react'
import CareLifeLogo from '../../components/CareLifeLogo'
import { confirmPasswordReset, requestPasswordReset } from '../../api/workspace'
import './Auth.css'

function readResetToken() {
  const hash = window.location.hash || ''
  const hashQuery = hash.includes('?') ? hash.slice(hash.indexOf('?') + 1) : ''
  const candidates = [window.location.search.slice(1), hashQuery]
  for (const query of candidates) {
    const token = new URLSearchParams(query).get('token')
    if (token) return token
  }
  return ''
}

export default function PasswordResetPage() {
  const [token, setToken] = useState(readResetToken)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmation, setConfirmation] = useState('')
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    const sync = () => setToken(readResetToken())
    window.addEventListener('hashchange', sync)
    return () => window.removeEventListener('hashchange', sync)
  }, [])

  async function submitRequest(event) {
    event.preventDefault()
    setBusy(true)
    setMessage('')
    setError('')
    try {
      const result = await requestPasswordReset(email.trim())
      setMessage(result?.message || 'If that address belongs to a CareLife account, follow the reset instructions sent to it.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The reset request could not be submitted.')
    } finally {
      setBusy(false)
    }
  }

  async function submitConfirmation(event) {
    event.preventDefault()
    setMessage('')
    setError('')
    if (password !== confirmation) {
      setError('The passwords do not match.')
      return
    }
    setBusy(true)
    try {
      const result = await confirmPasswordReset(token, password)
      setMessage(result?.message || 'Password updated. Sign in with your new password.')
      setPassword('')
      setConfirmation('')
      setToken('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The reset link could not be used.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-shell">
        <aside className="auth-side" aria-label="CareLife account recovery">
          <a className="auth-side-brand" href="#home" aria-label="CareLife home"><CareLifeLogo size={34} /><span>CareLife</span></a>
          <div className="auth-side-body">
            <p className="auth-eyebrow">ACCOUNT SECURITY</p>
            <h2>Get back into your CareLife account.</h2>
            <p>Use the email address on your account to request a reset link. A reset token is required before a new password can be saved.</p>
          </div>
          <p className="auth-side-foot">CareLife account recovery</p>
        </aside>
        <section className="auth-card">
          <a className="auth-brand" href="#home" aria-label="CareLife home"><CareLifeLogo size={36} /><span>CareLife</span></a>
          <div className="auth-content">
            <p className="auth-eyebrow">PASSWORD RESET</p>
            <h1>{token ? 'Choose a new password' : 'Reset your password'}</h1>
            <p className="auth-description">{token ? 'Your reset link is ready. Choose a password with at least eight characters.' : 'We will send reset instructions to the email address linked to your account.'}</p>
            {error && <div className="auth-message auth-message-error" role="alert">{error}</div>}
            {message && <div className="auth-message auth-message-success" role="status">{message}</div>}
            {token ? (
              <form className="auth-form" onSubmit={submitConfirmation}>
                <div className="form-field"><label htmlFor="reset-password">New password</label><input id="reset-password" type="password" autoComplete="new-password" minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} required /></div>
                <div className="form-field"><label htmlFor="reset-confirm">Confirm new password</label><input id="reset-confirm" type="password" autoComplete="new-password" minLength={8} value={confirmation} onChange={(event) => setConfirmation(event.target.value)} required /></div>
                <button type="submit" className="auth-submit" disabled={busy}>{busy ? 'Updating password…' : 'Save new password'}</button>
              </form>
            ) : (
              <form className="auth-form" onSubmit={submitRequest}>
                <div className="form-field"><label htmlFor="reset-email">Email address</label><input id="reset-email" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" required /></div>
                <button type="submit" className="auth-submit" disabled={busy}>{busy ? 'Sending request…' : 'Send reset instructions'}</button>
              </form>
            )}
            <a className="auth-home-link" href="#login">← Back to sign in</a>
          </div>
        </section>
      </section>
    </main>
  )
}
