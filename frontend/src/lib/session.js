import { useSyncExternalStore } from 'react'

const TOKEN_KEY = 'carelife_access_token'
const EMAIL_KEY = 'carelife_email'
const ROLE_KEY = 'carelife_role'
const ORGANIZATION_ROLES_KEY = 'carelife_organization_roles'
const listeners = new Set()

function readStorage() {
  if (typeof window === 'undefined') return { token: '', email: '', role: '', organizationRoles: [] }
  try {
    return {
      token: window.localStorage.getItem(TOKEN_KEY) || '',
      email: window.localStorage.getItem(EMAIL_KEY) || '',
      role: (window.localStorage.getItem(ROLE_KEY) || '').toLowerCase(),
      organizationRoles: JSON.parse(window.localStorage.getItem(ORGANIZATION_ROLES_KEY) || '[]'),
    }
  } catch {
    return { token: '', email: '', role: '', organizationRoles: [] }
  }
}

let snapshot = readStorage()

function refreshSnapshot() {
  snapshot = readStorage()
  listeners.forEach((listener) => listener())
}

function subscribe(listener) {
  listeners.add(listener)
  if (typeof window !== 'undefined') {
    window.addEventListener('storage', refreshSnapshot)
  }
  return () => {
    listeners.delete(listener)
    if (typeof window !== 'undefined') {
      window.removeEventListener('storage', refreshSnapshot)
    }
  }
}

function getSnapshot() {
  return snapshot
}

export function getToken() {
  return snapshot.token
}

export function saveSession({ token, email = '', role = '' }) {
  try {
    window.localStorage.setItem(TOKEN_KEY, token || '')
    window.localStorage.setItem(EMAIL_KEY, email || '')
    window.localStorage.setItem(ROLE_KEY, String(role || '').toLowerCase())
    window.localStorage.setItem(ORGANIZATION_ROLES_KEY, '[]')
  } catch {
    // The API request still succeeds, but this browser cannot persist the session.
  }
  refreshSnapshot()
}

export function setRole(role) {
  try {
    if (role) window.localStorage.setItem(ROLE_KEY, String(role).toLowerCase())
    else window.localStorage.removeItem(ROLE_KEY)
  } catch {
    // The next successful profile request can retry the role refresh.
  }
  refreshSnapshot()
}

export function setOrganizationRoles(organizationRoles) {
  const safeRoles = Array.isArray(organizationRoles)
    ? organizationRoles.filter((item) => item && item.organization_id && item.organization_role)
    : []
  try {
    window.localStorage.setItem(ORGANIZATION_ROLES_KEY, JSON.stringify(safeRoles))
  } catch {
    // Role checks are refreshed after the next authenticated profile request.
  }
  refreshSnapshot()
}

export function clearSession() {
  try {
    window.localStorage.removeItem(TOKEN_KEY)
    window.localStorage.removeItem(EMAIL_KEY)
    window.localStorage.removeItem(ROLE_KEY)
    window.localStorage.removeItem(ORGANIZATION_ROLES_KEY)
  } catch {
    // Keep the UI responsive when storage is blocked.
  }
  refreshSnapshot()
}

export function useSession() {
  const session = useSyncExternalStore(subscribe, getSnapshot, getSnapshot)
  return { ...session, signedIn: Boolean(session.token) }
}
