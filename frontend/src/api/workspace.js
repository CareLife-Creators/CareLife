import { apiRequest } from './client'

const safe = (value) => encodeURIComponent(String(value ?? '').trim())
const json = (method, body) => ({ method, body: JSON.stringify(body) })

// Account, inbox and notifications
export const getMyProfile = () => apiRequest('/users/me/profile')
export const updateMyProfile = (body) => apiRequest('/users/me/profile', json('PATCH', body))
export const getMyNotifications = ({ unreadOnly = false } = {}) => apiRequest('/notifications?unread_only=' + String(Boolean(unreadOnly)) + '&limit=100')
export const markNotificationRead = (id) => apiRequest('/notifications/' + safe(id) + '/read', { method: 'PATCH' })
export const getMyConversations = () => apiRequest('/messages/conversations')
export const startConversation = (recipientUserId) => apiRequest('/messages/conversations', json('POST', { recipient_user_id: recipientUserId }))
export const getConversationMessages = (id) => apiRequest('/messages/conversations/' + safe(id) + '/messages')
export const sendConversationMessage = (id, body) => apiRequest('/messages/conversations/' + safe(id) + '/messages', json('POST', { body }))

// Child profiles, daycare enrollment, attendance and daily notes
export const getMyChildren = () => apiRequest('/children/daycare')
export const createChild = (body) => apiRequest('/children/daycare', json('POST', body))
export const updateChild = (id, body) => apiRequest('/children/daycare/' + safe(id), json('PUT', body))
export const getChildEmergencyContacts = (id) => apiRequest('/children/daycare/' + safe(id) + '/emergency-contacts')
export const addChildEmergencyContact = (id, body) => apiRequest('/children/daycare/' + safe(id) + '/emergency-contacts', json('POST', body))
export const getChildPickupPersons = (id) => apiRequest('/children/daycare/' + safe(id) + '/pickup-persons')
export const addChildPickupPerson = (id, body) => apiRequest('/children/daycare/' + safe(id) + '/pickup-persons', json('POST', body))
export const getMyEnrollments = () => apiRequest('/enrollments')
export const getPendingDaycareEnrollments = () => apiRequest('/enrollments/daycare/pending')
export const createEnrollment = (childId, daycareOrganizationId) => apiRequest('/enrollments', json('POST', { child_id: childId, daycare_organization_id: daycareOrganizationId }))
export const reviewEnrollment = (id, status, message = '') => apiRequest('/enrollments/' + safe(id) + '/review', json('POST', { status, message: message.trim() || null }))
export const cancelEnrollment = (id) => apiRequest('/enrollments/' + safe(id) + '/cancel', { method: 'POST' })
export const getChildAttendance = (childId) => apiRequest('/daycare/children/' + safe(childId) + '/attendance')
export const getChildDailyUpdates = (childId) => apiRequest('/daycare/children/' + safe(childId) + '/daily-updates')
export const addChildDailyUpdate = (childId, notes) => apiRequest('/daycare/children/' + safe(childId) + '/daily-updates', json('POST', { notes }))
export const checkInEnrollment = (enrollmentId) => apiRequest('/daycare/attendance/check-in', json('POST', { enrollment_id: enrollmentId }))
export const checkOutAttendance = (attendanceId) => apiRequest('/daycare/attendance/' + safe(attendanceId) + '/check-out', json('POST', {}))

// Independent caregiver profiles, availability and appointments
export const getMyCaregiverProfile = () => apiRequest('/caregivers/me/profile')
export const createMyCaregiverProfile = (body) => apiRequest('/caregivers/me/profile', json('POST', body))
export const updateMyCaregiverProfile = (body) => apiRequest('/caregivers/me/profile', json('PATCH', body))
export const submitCaregiverDocument = (body) => apiRequest('/caregivers/me/profile/documents', json('POST', body))
export const getMyAvailability = () => apiRequest('/caregivers/me/availability')
export const createAvailability = (body) => apiRequest('/caregivers/me/availability', json('POST', body))
export const getCaregiverAvailability = (id) => apiRequest('/caregivers/' + safe(id) + '/availability', { authenticated: false })
export const getMyCaregiverAppointments = () => apiRequest('/appointments/me')
export const createCaregiverAppointment = (availabilityId, message = '') => apiRequest('/appointments', json('POST', { availability_id: availabilityId, message: message.trim() || null }))
export const decideCaregiverAppointment = (id, status, message = '') => apiRequest('/appointments/' + safe(id) + '/decision', json('POST', { status, message: message.trim() || null }))

// Elder-care booking and resident check-in
export const getMyElderCareBookings = () => apiRequest('/elder-care/bookings')
export const createElderCareBooking = (body) => apiRequest('/elder-care/bookings', json('POST', body))
export const decideElderCareBooking = (id, status, note = '') => apiRequest('/elder-care/bookings/' + safe(id) + '/decision', json('POST', { status, note: note.trim() || null }))
export const cancelElderCareBooking = (id, note = '') => apiRequest('/elder-care/bookings/' + safe(id) + '/cancel', json('POST', { note: note.trim() || null }))
export const completeElderCareBooking = (id, note = '') => apiRequest('/elder-care/bookings/' + safe(id) + '/complete', json('POST', { note: note.trim() || null }))

// Organization registration and management
export const registerOrganization = (body) => apiRequest('/organizations/register', json('POST', body))
export const getOrganizationProfile = (id) => apiRequest('/organizations/' + safe(id) + '/profile')
export const updateOrganizationProfile = (id, body) => apiRequest('/organizations/' + safe(id) + '/profile', json('PATCH', body))
export const getOrganizationCampaigns = (id) => apiRequest('/organizations/' + safe(id) + '/donation-campaigns')
export const createOrganizationCampaign = (id, body) => apiRequest('/organizations/' + safe(id) + '/donation-campaigns', json('POST', body))
export const updateOrganizationCampaign = (orgId, campaignId, body) => apiRequest('/organizations/' + safe(orgId) + '/donation-campaigns/' + safe(campaignId), json('PATCH', body))
export const getOrganizationNeeds = (id) => apiRequest('/organizations/' + safe(id) + '/donation-needs')
export const createOrganizationNeed = (id, body) => apiRequest('/organizations/' + safe(id) + '/donation-needs', json('POST', body))
export const updateOrganizationNeed = (orgId, needId, body) => apiRequest('/organizations/' + safe(orgId) + '/donation-needs/' + safe(needId), json('PATCH', body))
export const getOrganizationImpactUpdates = (id) => apiRequest('/organizations/' + safe(id) + '/impact-updates')
export const createOrganizationImpactUpdate = (id, body) => apiRequest('/organizations/' + safe(id) + '/impact-updates', json('POST', body))

// Resident profiles and consent-controlled family check-ins
export const getOrganizationResidents = (organizationId) => apiRequest('/elder-care/organizations/' + safe(organizationId) + '/residents')
export const createResidentProfile = (organizationId, body) => apiRequest('/elder-care/organizations/' + safe(organizationId) + '/residents', json('POST', body))
export const updateResidentProfile = (organizationId, residentId, body) => apiRequest('/elder-care/organizations/' + safe(organizationId) + '/residents/' + safe(residentId), json('PATCH', body))
export const getResidentCheckIns = (residentId) => apiRequest('/elder-care/residents/' + safe(residentId) + '/check-ins')
export const createResidentCheckIn = (residentId, body) => apiRequest('/elder-care/residents/' + safe(residentId) + '/check-ins', json('POST', body))
export const setResidentConsent = (organizationId, residentId, body) => apiRequest('/elder-care/organizations/' + safe(organizationId) + '/residents/' + safe(residentId) + '/consent', json('POST', body))

// CareLife administration
export const getPendingCaregivers = () => apiRequest('/caregivers/verification/pending')
export const reviewCaregiver = (id, status, message = '') => apiRequest('/caregivers/' + safe(id) + '/verification', json('POST', { status, message: message.trim() || null }))
export const getAdminAuditLogs = (limit = 100) => apiRequest('/admin/audit-logs?limit=' + encodeURIComponent(limit))

// bKash payment checkout and receipts
export const startBkashPayment = (campaignId, amount) => apiRequest('/donation-campaigns/' + safe(campaignId) + '/bkash-payments', json('POST', { amount }))
export const getMyDonationPayments = () => apiRequest('/donations/payments/me')
export const verifyDonationPayment = (paymentId) => apiRequest('/donations/payments/' + safe(paymentId) + '/verify', { method: 'POST' })

// Account recovery
export const requestPasswordReset = (email) => apiRequest('/auth/password-reset/request', { ...json('POST', { email }), authenticated: false })
export const confirmPasswordReset = (token, newPassword) => apiRequest('/auth/password-reset/confirm', { ...json('POST', { token, new_password: newPassword }), authenticated: false })

// Orphanage child records and case outcomes (staff-only backend routes)
export const getOrganizationOrphanageChildren = (organizationId) =>
  apiRequest('/children/orphanages/' + safe(organizationId))
export const createOrphanageChild = (organizationId, body) =>
  apiRequest('/children/orphanages/' + safe(organizationId) + '/children', json('POST', body))
export const getChildOutcomes = (childId) => apiRequest('/children/' + safe(childId) + '/outcomes')
export const createChildOutcome = (childId, body) =>
  apiRequest('/children/' + safe(childId) + '/outcomes', json('POST', body))
export const updateChildOutcome = (outcomeId, body) =>
  apiRequest('/children/outcomes/' + safe(outcomeId), json('PUT', body))
export const deleteChildOutcome = (outcomeId) =>
  apiRequest('/children/outcomes/' + safe(outcomeId), { method: 'DELETE' })

// Administrator moderation queue for impact posts
export const getPendingImpactUpdates = () => apiRequest('/admin/impact-updates')
export const reviewImpactUpdate = (updateId, decision, privacyConfirmed, reviewNotes = '') =>
  apiRequest('/admin/impact-updates/' + safe(updateId) + '/review', json('POST', {
    decision,
    privacy_confirmed: Boolean(privacyConfirmed),
    review_notes: reviewNotes.trim() || null,
  }))

// Caregiver media can be submitted only as a multipart payload.
export const uploadImpactMedia = (organizationId, updateId, file) => {
  const body = new FormData()
  body.append('file', file)
  return apiRequest('/organizations/' + safe(organizationId) + '/impact-updates/' + safe(updateId) + '/media', {
    method: 'POST',
    body,
  })
}

// In-kind donation pledge tracking for donors and organization staff
export const getMyInKindPledges = () => apiRequest('/my/in-kind-pledges')
export const getOrganizationInKindPledges = (organizationId) =>
  apiRequest('/organizations/' + safe(organizationId) + '/in-kind-pledges')
export const updateInKindPledgeStatus = (organizationId, pledgeId, status) =>
  apiRequest('/organizations/' + safe(organizationId) + '/in-kind-pledges/' + safe(pledgeId) + '/status', json('PATCH', { status }))
