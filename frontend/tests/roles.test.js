import assert from 'node:assert/strict'
import test from 'node:test'
import { canAccessRoute, canUseDonorFeatures, isProtectedRoute, ROLE } from '../src/lib/roles.js'

const publicRoutes = [
  '#daycare-directory',
  '#elderly-care-directory',
  '#caregivers',
  '#orphanage-support',
]

test('public discovery and support routes are available while signed out', () => {
  for (const route of publicRoutes) {
    assert.equal(isProtectedRoute(route), false, `${route} should not redirect signed-out visitors`)
    assert.equal(canAccessRoute(route, ''), true, `${route} should render without a signed-in role`)
  }
})

test('private records, bookings, messaging, and account routes still require sign-in', () => {
  const privateRoutes = [
    '#my-children',
    '#family-checkins',
    '#care-bookings',
    '#messages',
    '#dashboard',
    '#account',
    '#organization-profile',
  ]

  for (const route of privateRoutes) {
    assert.equal(isProtectedRoute(route), true, `${route} should remain protected`)
  }
})

test('organization and admin workspaces retain their role checks', () => {
  assert.equal(canAccessRoute('#organization-workspace', ROLE.DAYCARE_STAFF), true)
  assert.equal(canAccessRoute('#organization-workspace', ROLE.PARENT_GUARDIAN), false)
  assert.equal(canAccessRoute('#admin-operations', ROLE.ADMIN), true)
  assert.equal(canAccessRoute('#admin-operations', ROLE.DONOR_SUPPORTER), false)
})

test('pledges and payment history require a signed-in donor account', () => {
  assert.equal(canUseDonorFeatures(ROLE.DONOR_SUPPORTER, true), true)
  assert.equal(canUseDonorFeatures(ROLE.DONOR_SUPPORTER, false), false)
  assert.equal(canUseDonorFeatures(ROLE.PARENT_GUARDIAN, true), false)
  assert.equal(canUseDonorFeatures('', false), false)
})
