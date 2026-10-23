import { useCallback, useEffect, useState } from 'react'
import PageLoader from './components/PageLoader'
import { shouldShowLoader } from './lib/loader'
import './App.css'
import LoginPage from './pages/auth/LoginPage'
import SignupPage from './pages/auth/SignupPage'
import PasswordResetPage from './pages/auth/PasswordResetPage'
import HomePage from './pages/HomePage'
import DashboardPage from './pages/DashboardPage'
import DaycareDirectoryPage from './pages/daycare/DaycareDirectoryPage'
import OrganizationApprovalDashboard from './pages/organization/OrganizationApprovalDashboard'
import VerificationStatusPage from './pages/organization/VerificationStatusPage'
import ElderCareDirectoryPage from './pages/elder-care/ElderCareDirectoryRoute'
import PublicOrganizationProfilePage from './pages/organization/PublicOrganizationProfilePage'
import CaregiverDirectoryPage from './pages/caregivers/CaregiverDirectoryPage'
import OrphanageSupportPage from './pages/orphanage/OrphanageSupportPage'
import ModuleLandingPage from './pages/modules/ModuleLandingPage'
import StaffAccessPage from './pages/staff-access/StaffAccessPage'
import AdminRoleRequestsPage from './pages/admin/AdminRoleRequestsPage'
import ChildrenWorkspacePage from './pages/ChildrenWorkspacePage'
import CareBookingsPage from './pages/CareBookingsPage'
import AccountPage from './pages/AccountPage'
import FamilyCheckInsPage from './pages/FamilyCheckInsPage'
import AdminOperationsPage from './pages/AdminOperationsPage'
import AdminUsersPage from './pages/admin/AdminUsersPage'
import CaregiverWorkspacePage from './pages/CaregiverWorkspacePage'
import OrganizationWorkspacePage from './pages/OrganizationWorkspacePage'
import OrganizationOnboardingPage from './pages/OrganizationOnboardingPage'
import SiteNav from './components/SiteNav'
import { refreshSession } from './api/auth'
import { canAccessRoute, isProtectedRoute } from './lib/roles'
import { useSession } from './lib/session'
import { ToastStack } from './components/ui'
import './CareLifeExperience.css'

const knownRoutes = new Set([
  '#home', '#dashboard', '#login', '#signup', '#for-organizations', '#password-reset',
  '#password-reset-confirm', '#daycare', '#orphanage', '#elderly-care',
  '#daycare-directory', '#elderly-care-directory', '#caregivers',
  '#orphanage-support', '#organization-approval', '#verification',
  '#staff-access', '#admin-role-requests', '#my-children', '#care-bookings', '#organization-profile',
  '#caregiver-workspace', '#account', '#notifications', '#messages', '#organization-workspace', '#admin-operations', '#admin-users', '#family-checkins',
])

function readRoute() {
  const rawHash = window.location.hash.trim()
  if (!rawHash || rawHash === '#') return '#home'
  const route = rawHash.split('?')[0]
  return knownRoutes.has(route) ? route : '#not-found'
}

function NotFoundPage() {
  return <><SiteNav /><main className="route-not-found">
    <span className="route-not-found-icon" aria-hidden="true">?</span>
    <p className="route-eyebrow">PAGE NOT FOUND</p><h1>Let’s get you back on track.</h1>
    <p>This address does not match a CareLife page. Choose a care module or return home to find the right place.</p>
    <div className="route-not-found-actions"><a className="route-primary-action" href="#home">Return home</a><a className="route-secondary-action" href="#daycare">Explore care modules</a></div>
  </main></>
}

function AccessRestrictedPage({ route, role }) {
  const childPage = route === '#my-children'
  const destination = childPage && role === 'daycare_staff' ? '#organization-workspace' : '#dashboard'
  const subject = childPage ? 'Children & attendance' : 'Organization workspace'
  const explanation = childPage
    ? 'A parent or guardian account can manage child profiles. Daycare staff can manage enrollment and attendance from their organization workspace.'
    : 'This area is for approved daycare, children’s home, or care-home staff. Sign in with an approved organization staff account to manage its records.'
  return <><SiteNav /><main className="route-not-found">
    <span className="route-not-found-icon" aria-hidden="true">↗</span>
    <p className="route-eyebrow">ACCOUNT ACCESS</p><h1>{subject} is not available for this account.</h1>
    <p>{explanation}</p>
    <div className="route-not-found-actions"><a className="route-primary-action" href={destination}>Open my workspace</a><a className="route-secondary-action" href="#account">View account</a></div>
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

  useEffect(() => {
    if (!token) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- Reset the token validation marker when a session ends.
      setCheckedToken('')
      return undefined
    }
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
    if (needsSignIn && !signedIn) {
      try { window.sessionStorage.setItem('carelife_return_route', route) } catch { /* Ignore blocked storage. */ }
      window.location.hash = '#login'
    }
  }, [needsSignIn, signedIn, route])

  useEffect(() => {
    if (signedIn && (route === '#login' || route === '#signup' || route === '#home')) {
      let returnRoute = ''
      try {
        returnRoute = window.sessionStorage.getItem('carelife_return_route') || ''
        window.sessionStorage.removeItem('carelife_return_route')
      } catch { /* Ignore blocked storage. */ }
      window.location.hash = knownRoutes.has(returnRoute) && isProtectedRoute(returnRoute) ? returnRoute : '#dashboard'
    }
  }, [signedIn, route])

  if (needsSignIn && !signedIn) return <main className="route-redirect" aria-live="polite"><div className="route-redirect-mark">C</div><p>Taking you to sign in…</p><a href="#login">Continue to sign in</a></main>
  if (needsSignIn && !roleReady) return <main className="route-redirect" aria-live="polite"><div className="route-redirect-mark">C</div><p>Checking your access…</p></main>
  if (needsSignIn && !canAccessRoute(route, role)) return <AccessRestrictedPage route={route} role={role} />

  if (route === '#home' && signedIn) return <main className="route-redirect" aria-live="polite"><div className="route-redirect-mark">C</div><p>Opening your CareLife workspace…</p></main>
  if (route === '#home') return <HomePage />
  if (route === '#for-organizations') return <OrganizationOnboardingPage />
  if (route === '#dashboard') return <DashboardPage />
  if (route === '#daycare') return <ModuleLandingPage moduleKey="daycare" />
  if (route === '#orphanage') return <ModuleLandingPage moduleKey="orphanage" />
  if (route === '#elderly-care') return <ModuleLandingPage moduleKey="elderly-care" />
  if (route === '#daycare-directory') return <DaycareDirectoryPage />
  if (route === '#elderly-care-directory') return <ElderCareDirectoryPage />
  if (route === '#organization-profile') return <PublicOrganizationProfilePage />
  if (route === '#caregivers') return <CaregiverDirectoryPage />
  if (route === '#orphanage-support') return <OrphanageSupportPage />
  if (route === '#organization-approval') return <OrganizationApprovalDashboard />
  if (route === '#verification') return <VerificationStatusPage />
  if (route === '#staff-access') return <StaffAccessPage />
  if (route === '#admin-role-requests') return <AdminRoleRequestsPage />
  if (route === '#my-children') return <ChildrenWorkspacePage />
  if (route === '#care-bookings' && role === 'independent_caregiver') return <CaregiverWorkspacePage key="requests" initialSection="requests" />
  if (route === '#care-bookings') return <CareBookingsPage />
  if (route === '#caregiver-workspace') return <CaregiverWorkspacePage key="profile" />
  if (route === '#organization-workspace') return <OrganizationWorkspacePage key={role || 'staff'} />
  if (route === '#account') return <AccountPage />
  if (route === '#notifications') return <AccountPage initialTab="notifications" />
  if (route === '#messages') return <AccountPage initialTab="messages" />
  if (route === '#family-checkins') return <FamilyCheckInsPage />
  if (route === '#admin-operations') return <AdminOperationsPage />
  if (route === '#admin-users') return <AdminUsersPage />
  if (route === '#password-reset' || route === '#password-reset-confirm') return <PasswordResetPage />
  if (route === '#login') return <LoginPage onSignup={() => { window.location.hash = '#signup' }} />
  if (route === '#signup') return <SignupPage onLogin={() => { window.location.hash = '#login' }} />
  return <NotFoundPage />
}

function App() {
  const [showLoader, setShowLoader] = useState(shouldShowLoader)
  const hideLoader = useCallback(() => setShowLoader(false), [])
  return (
    <>
      {showLoader && <PageLoader onDone={hideLoader} />}
      <AppRoutes />
      <ToastStack />
    </>
  )
}

export default App
