const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export async function getOrganizationVerification(
    organizationId
) {
    const response = await fetch(
        `${API_BASE_URL}/organizations/${organizationId}/verification-status`, {
            credentials: 'include',
        }
    )

    if (!response.ok) {
        if (response.status === 401) {
            throw new Error('Authentication required')
        }

        if (response.status === 403) {
            throw new Error(
                'You do not have access to this organization'
            )
        }

        if (response.status === 404) {
            throw new Error(
                'Verification information not found'
            )
        }

        throw new Error('Unable to load verification status')
    }

    return response.json()
}