import { apiRequest } from './client'

export async function createRoleRequest({ requestedRole, note }) {
    return apiRequest('/users/me/role-requests', {
        method: 'POST',
        body: JSON.stringify({
            requested_role: requestedRole,
            note: note && note.trim() ? note.trim() : null,
        }),
    })
}

export async function getMyRoleRequests() {
    return apiRequest('/users/me/role-requests')
}

export async function getAdminRoleRequests(status = 'pending') {
    return apiRequest('/admin/role-requests?status=' + encodeURIComponent(status))
}

export async function approveRoleRequest(requestId) {
    return apiRequest('/admin/role-requests/' + encodeURIComponent(requestId) + '/approve', {
        method: 'POST',
    })
}

export async function rejectRoleRequest(requestId) {
    return apiRequest('/admin/role-requests/' + encodeURIComponent(requestId) + '/reject', {
        method: 'POST',
    })
}