export const ROLE = Object.freeze({
  PARENT_GUARDIAN: 'parent_guardian',
  DONOR_SUPPORTER: 'donor_supporter',
  INDEPENDENT_CAREGIVER: 'independent_caregiver',
  FAMILY_REPRESENTATIVE: 'family_representative',
  DAYCARE_STAFF: 'daycare_staff',
  ORPHANAGE_STAFF: 'orphanage_staff',
  CARE_HOME_STAFF: 'care_home_staff',
  ADMIN: 'carelife_admin',
})

export const SIGNUP_ROLE_OPTIONS = [
  { value: ROLE.PARENT_GUARDIAN, label: 'Parent or guardian', hint: 'Manage child profiles, enrollments and attendance.' },
  { value: ROLE.DONOR_SUPPORTER, label: 'Donor or supporter', hint: 'Support campaigns and track payment receipts.' },
  { value: ROLE.INDEPENDENT_CAREGIVER, label: 'Independent caregiver', hint: 'Publish a care profile and manage appointment requests.' },
  { value: ROLE.FAMILY_REPRESENTATIVE, label: 'Family representative', hint: 'Coordinate care for an authorized family member.' },
]

export const STAFF_ROLE_OPTIONS = [
  { value: ROLE.DAYCARE_STAFF, label: 'Daycare staff', hint: 'Manage daycare enrollment and attendance.' },
  { value: ROLE.ORPHANAGE_STAFF, label: 'Orphanage staff', hint: 'Publish campaigns, item needs and impact updates.' },
  { value: ROLE.CARE_HOME_STAFF, label: 'Care-home staff', hint: 'Manage resident profiles and family check-ins.' },
]

const LABELS = {
  [ROLE.PARENT_GUARDIAN]: 'Parent / Guardian',
  [ROLE.DONOR_SUPPORTER]: 'Donor / Supporter',
  [ROLE.INDEPENDENT_CAREGIVER]: 'Independent Caregiver',
  [ROLE.FAMILY_REPRESENTATIVE]: 'Family Representative',
  [ROLE.DAYCARE_STAFF]: 'Daycare Staff',
  [ROLE.ORPHANAGE_STAFF]: 'Orphanage Staff',
  [ROLE.CARE_HOME_STAFF]: 'Care-home Staff',
  [ROLE.ADMIN]: 'CareLife Admin',
}

const STAFF = new Set([ROLE.DAYCARE_STAFF, ROLE.ORPHANAGE_STAFF, ROLE.CARE_HOME_STAFF])

export function roleLabel(role) {
  const key = String(role || '').toLowerCase()
  return LABELS[key] || (key ? key.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase()) : 'Member')
}

export function isAdmin(role) {
  return String(role || '').toLowerCase() === ROLE.ADMIN
}

export function isStaff(role) {
  return STAFF.has(String(role || '').toLowerCase())
}

export function canAccessRoute(route, role) {
  const key = String(role || '').toLowerCase()
  if (['#organization-approval', '#admin-role-requests', '#admin-operations'].includes(route)) return isAdmin(key)
  if (route === '#verification') return isStaff(key) || isAdmin(key)
  if (route === '#organization-workspace') return isStaff(key)
  if (route === '#caregiver-workspace') return key === ROLE.INDEPENDENT_CAREGIVER || isAdmin(key)
  if (route === '#my-children') return [ROLE.PARENT_GUARDIAN, ROLE.DAYCARE_STAFF, ROLE.ADMIN].includes(key)
  if (route === '#family-checkins') return [ROLE.FAMILY_REPRESENTATIVE, ROLE.ADMIN].includes(key)
  return true
}

const PRIVATE_ROUTES = new Set([
  '#dashboard', '#my-children', '#care-bookings', '#caregiver-workspace',
  '#account', '#organization-workspace', '#admin-operations',
  '#organization-approval', '#verification', '#staff-access', '#admin-role-requests', '#family-checkins',
])

export function isProtectedRoute(route) {
  return PRIVATE_ROUTES.has(route)
}

export function memberLinks(role) {
  const key = String(role || '').toLowerCase()
  const links = [{ href: '#dashboard', label: 'Workspace' }]

  if (key === ROLE.PARENT_GUARDIAN) {
    links.push(
      { href: '#my-children', label: 'My children' },
      { href: '#care-bookings', label: 'Care bookings' },
      { href: '#orphanage-support', label: 'Support board' },
    )
  } else if (key === ROLE.DONOR_SUPPORTER) {
    links.push({ href: '#orphanage-support', label: 'Support board' })
  } else if (key === ROLE.INDEPENDENT_CAREGIVER) {
    links.push(
      { href: '#caregiver-workspace', label: 'Caregiver workspace' },
      { href: '#care-bookings', label: 'Appointments' },
    )
  } else if (key === ROLE.FAMILY_REPRESENTATIVE) {
    links.push({ href: '#care-bookings', label: 'Care bookings' }, { href: '#family-checkins', label: 'Family check-ins' })
  } else if (key === ROLE.DAYCARE_STAFF) {
    links.push(
      { href: '#my-children', label: 'Children & attendance' },
      { href: '#organization-workspace', label: 'Organization tools' },
    )
  } else if (key === ROLE.ORPHANAGE_STAFF) {
    links.push(
      { href: '#organization-workspace', label: 'Organization tools' },
      { href: '#orphanage-support', label: 'Support board' },
    )
  } else if (key === ROLE.CARE_HOME_STAFF) {
    links.push(
      { href: '#care-bookings', label: 'Care bookings' },
      { href: '#organization-workspace', label: 'Organization tools' },
    )
  } else if (isAdmin(key)) {
    links.push(
      { href: '#organization-approval', label: 'Organization approvals' },
      { href: '#admin-role-requests', label: 'Staff access requests' },
      { href: '#admin-operations', label: 'Admin operations' },
    )
  } else {
    links.push({ href: '#staff-access', label: 'Request staff access' })
  }

  links.push({ href: '#account', label: 'Account & inbox' })
  return links
}
