import { useEffect, useState } from 'react'
import './App.css'

import LoginPage from './pages/auth/LoginPage'
import SignupPage from './pages/auth/SignupPage'
import HomePage from './pages/HomePage'
import DashboardPage from './pages/DashboardPage'
import DaycareDirectoryPage from './pages/daycare/DaycareDirectoryPage'
import OrganizationApprovalDashboard from './pages/organization/OrganizationApprovalDashboard'
import VerificationStatusPage from './pages/organization/VerificationStatusPage'
import SiteNav from './components/SiteNav'

const knownRoutes = new Set([
  '#home',
  '#dashboard',
  '#login',
  '#signup',
  '#daycare-directory',
  '#organization-approval',
  '#verification',
])

const authenticatedRoutes = new Set([
  '#dashboard',
  '#organization-approval',
  '#verification',
])

function readRoute() {
  const hash = window.location.hash.trim()

  if (!hash || hash === '#') {
    return '#home'
  }

  return knownRoutes.has(hash) ? hash : '#not-found'
}

function NotFoundPage() {
  return (
    <>
      <SiteNav />
      <main className="route-not-found">
        <span className="route-not-found-icon" aria-hidden="true">?</span>
        <p className="route-eyebrow">PAGE NOT FOUND</p>
        <h1>This page is not available yet.</h1>
        <p>
          The address may be outdated, or this page has not been added to
          the current CareLife frontend.
        </p>
        <a className="route-primary-action" href="#home">Return to CareLife</a>
      </main>
    </>
  )
}

function App() {
  const [route, setRoute] = useState(readRoute)

  useEffect(() => {
    const handleHashChange = () => setRoute(readRoute())
    window.addEventListener('hashchange', handleHashChange)

    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  const isAuthenticated = Boolean(localStorage.getItem('carelife_access_token'))
  const requiresAuthentication = authenticatedRoutes.has(route)

  useEffect(() => {
    if (requiresAuthentication && !isAuthenticated) {
      window.location.hash = '#login'
    }
  }, [requiresAuthentication, isAuthenticated])

  if (requiresAuthentication && !isAuthenticated) {
    return (
      <main className="route-redirect" aria-live="polite">
        <div className="route-redirect-mark" aria-hidden="true">C</div>
        <p>Taking you to sign in…</p>
        <a href="#login">Continue to sign in</a>
      </main>
    )
  }

  if (route === '#home') {
    return <HomePage />
  }

  if (route === '#dashboard') {
    return <DashboardPage />
  }

  if (route === '#daycare-directory') {
    return <DaycareDirectoryPage />
  }

  if (route === '#organization-approval') {
    return <OrganizationApprovalDashboard />
  }

  if (route === '#verification') {
    return <VerificationStatusPage />
  }

  if (route === '#login') {
    return <LoginPage onSignup={() => { window.location.hash = '#signup' }} />
  }

  if (route === '#signup') {
    return <SignupPage onLogin={() => { window.location.hash = '#login' }} />
  }

  return <NotFoundPage />
}

export default App
