import { apiRequest } from './client'
import { clearSession, getToken, saveSession, setOrganizationRoles, setRole } from '../lib/session'

function cleanMessage(message) {
    return String(message || '').replace(/^Value error,\s*/i, '')
}

function translateAuthError(error, action) {
    if (!error.status) {
        return new Error('Cannot reach the CareLife server. Check that the backend is running.')
    }

    if (action === 'login' && error.status === 401) {
        return new Error('Invalid email or password')
    }

    if (error.status === 422) {
        return new Error(cleanMessage(error.message) || 'Please check the details you entered')
    }

    return new Error(
        action === 'signup' ?
        'Unable to create account: ' + error.message :
        'Unable to sign in: ' + error.message
    )
}

export async function signup({ email, password, fullName, phone, role }) {
    try {
        return await apiRequest('/auth/signup', {
            method: 'POST',
            authenticated: false,
            body: JSON.stringify({
                email,
                password,
                full_name: fullName,
                phone,
                role,
            }),
        })
    } catch (error) {
        throw translateAuthError(error, 'signup')
    }
}

export async function login({ email, password }) {
    let data

    try {
        data = await apiRequest('/auth/login', {
            method: 'POST',
            authenticated: false,
            body: JSON.stringify({ email, password }),
        })
    } catch (error) {
        throw translateAuthError(error, 'login')
    }

    if (!data || !data.access_token) {
        throw new Error('Sign in succeeded but no access token was returned.')
    }

    saveSession({
        token: data.access_token,
        email: data.email || email,
        role: data.role || '',
    })

    return data
}

export async function logout() {
    try {
        if (getToken()) {
            await apiRequest('/auth/logout', { method: 'POST' })
        }
    } catch {
        // Always clear the local session, even when the API is unavailable.
    } finally {
        clearSession()
        window.location.hash = '#home'
    }
}

// Reads the current role from the backend, so approvals take effect without signing in again.
export async function refreshSession() {
    if (!getToken()) return null

    try {
        const profile = await apiRequest('/users/me/profile')
        if (profile && profile.role) setRole(profile.role)
        const organizations = await apiRequest('/organizations/mine')
        setOrganizationRoles(Array.isArray(organizations) ? organizations : [])
        return profile
    } catch (error) {
        if (error && error.status === 401) clearSession()
        return null
    }
}
