import { useCallback, useEffect, useState } from 'react'
import PageLoader from './components/PageLoader'
import { shouldShowLoader } from './lib/loader'
import './App.css'
import LoginPage from './pages/auth/LoginPage'
import SignupPage from './pages/auth/SignupPage'
import HomePage from './pages/HomePage'
import DashboardPage from './pages/DashboardPage'
import DaycareDirectoryPage from './pages/daycare/DaycareDirectoryPage'
import OrganizationApprovalDashboard from './pages/organization/OrganizationApprovalDashboard'
import VerificationStatusPage from './pages/organization/VerificationStatusPage'
import ElderCareDirectoryPage from './pages/elder-care/ElderCareDirectoryPage'
import CaregiverDirectoryPage from './pages/caregivers/CaregiverDirectoryPage'
import OrphanageSupportPage from './pages/orphanage/OrphanageSupportPage'
import ModuleLandingPage from './pages/modules/ModuleLandingPage'
import StaffAccessPage from './pages/staff-access/StaffAccessPage'
import AdminRoleRequestsPage from './pages/admin/AdminRoleRequestsPage'
import SiteNav from './components/SiteNav'
import { refreshSession } from './api/auth'
import { canAccessRoute, isProtectedRoute } from './lib/roles'
import { useSession } from './lib/session'

const knownRoutes = new Set([
  '#home', '#dashboard', '#login', '#signup', '#daycare', '#orphanage',
  '#elderly-care', '#daycare-directory', '#elderly-care-directory',
  '#caregivers', '#orphanage-support', '#organization-approval', '#verification',
  '#staff-access', '#admin-role-requests',
])

function readRoute() {
  const hash = window.location.hash.trim()
  if (!hash || hash === '#') return '#home'
  return knownRoutes.has(hash) ? hash : '#not-found'
}

function NotFoundPage() {
  return <><SiteNav /><main className="route-not-found">
    <span className="route-not-found-icon" aria-hidden="true">?</span>
    <p className="route-eyebrow">PAGE NOT FOUND</p><h1>Let’s get you back on track.</h1>
    <p>This address does not match a CareLife page. Choose a care module or return home to find the right place.</p>
    <div className="route-not-found-actions"><a className="route-primary-action" href="#home">Return home</a><a className="route-secondary-action" href="#daycare">Explore care modules</a></div>
  </main></>
}

function AppRoutes() {
  const [route, setRoute] = useState(readRoute)
  const [checkedToken, setCheckedToken] = useState('')
  const { token, signedIn, role } = useSession()

  useEffect(() => {
    const onHashChange = () => setRoute(readRoute())
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  // Load the real role from the backend after sign-in, and again whenever the window regains focus.
  useEffect(() => {
    if (!token) return undefined
    let cancelled = false
    refreshSession().finally(() => { if (!cancelled) setCheckedToken(token) })
    const onFocus = () => { void refreshSession() }
    window.addEventListener('focus', onFocus)
    return () => {
      cancelled = true
      window.removeEventListener('focus', onFocus)
    }
  }, [token])

  const needsSignIn = isProtectedRoute(route)
  const roleReady = !signedIn || checkedToken === token

  useEffect(() => {
    if (needsSignIn && !signedIn) window.location.hash = '#login'
  }, [needsSignIn, signedIn])

  useEffect(() => {
    if (signedIn && (route === '#login' || route === '#signup' || route === '#home')) window.location.hash = '#dashboard'
  }, [signedIn, route])

  if (needsSignIn && !signedIn) return <main className="route-redirect" aria-live="polite"><div className="route-redirect-mark">C</div><p>Taking you to sign in…</p><a href="#login">Continue to sign in</a></main>
  if (needsSignIn && !roleReady) return <main className="route-redirect" aria-live="polite"><div className="route-redirect-mark">C</div><p>Checking your access…</p></main>
  // A page the user's role cannot use looks the same as a page that does not exist.
  if (needsSignIn && !canAccessRoute(route, role)) return <NotFoundPage />

  if (route === '#home') return <HomePage />
  if (route === '#dashboard') return <DashboardPage />
  if (route === '#daycare') return <ModuleLandingPage moduleKey="daycare" />
  if (route === '#orphanage') return <ModuleLandingPage moduleKey="orphanage" />
  if (route === '#elderly-care') return <ModuleLandingPage moduleKey="elderly-care" />
  if (route === '#daycare-directory') return <DaycareDirectoryPage />
  if (route === '#elderly-care-directory') return <ElderCareDirectoryPage />
  if (route === '#caregivers') return <CaregiverDirectoryPage />
  if (route === '#orphanage-support') return <OrphanageSupportPage />
  if (route === '#organization-approval') return <OrganizationApprovalDashboard />
  if (route === '#verification') return <VerificationStatusPage />
  if (route === '#staff-access') return <StaffAccessPage />
  if (route === '#admin-role-requests') return <AdminRoleRequestsPage />
  if (route === '#login') return <LoginPage onSignup={() => { window.location.hash = '#signup' }} />
  if (route === '#signup') return <SignupPage onLogin={() => { window.location.hash = '#login' }} />
  return <NotFoundPage />
}

function App() {
  const [showLoader, setShowLoader] = useState(shouldShowLoader)
  const hideLoader = useCallback(() => setShowLoader(false), [])
  return <>{showLoader && <PageLoader onDone={hideLoader} />}<AppRoutes /></>
}

export default App