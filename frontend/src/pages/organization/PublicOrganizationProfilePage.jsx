import { useEffect, useState } from 'react'
import SiteNav from '../../components/SiteNav'
import { getPublicOrganizationProfile } from '../../api/discovery'
import { publicOrganizationDescription, publicOrganizationName, publicOrganizationValue } from '../../lib/publicDisplay'
import '../DirectoryPages.css'
import './PublicOrganizationProfilePage.css'

function readProfileRef() {
  const query = window.location.hash.split('?')[1] || ''
  const params = new URLSearchParams(query)
  return { id: params.get('id') || '', type: params.get('type') || 'daycare' }
}

export default function PublicOrganizationProfilePage() {
  const [reference] = useState(readProfileRef)
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    getPublicOrganizationProfile(reference.id).then((data) => { if (!cancelled) setProfile(data) })
      .catch((err) => { if (!cancelled) setError(err instanceof Error ? err.message : 'This public listing could not be loaded.') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [reference])

  const title = publicOrganizationName(profile?.organization_name) || 'Care organization'
  const typeLabel = profile?.organization_type === 'elderly_care' ? 'Elderly care home' : 'Daycare center'
  const location = profile?.location || ''
  const mapUrl = profile?.latitude != null && profile?.longitude != null
    ? `https://www.google.com/maps/search/?api=1&query=${profile.latitude},${profile.longitude}`
    : location ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(location)}` : ''

  return <><SiteNav/><main className="directory-page organization-profile-page">
    <div className="directory-breadcrumb"><a href={reference.type === 'daycare' ? '#daycare-directory' : '#elderly-care-directory'}>← Back to {reference.type === 'daycare' ? 'daycare centers' : 'care homes'}</a></div>
    {loading && <div className="directory-state" role="status">Loading public organization details…</div>}
    {!loading && error && <div className="directory-state error" role="alert"><strong>Listing unavailable</strong><p>{error}</p><a className="organization-profile-back" href={reference.type === 'daycare' ? '#daycare-directory' : '#elderly-care-directory'}>Return to directory</a></div>}
    {!loading && profile && <>
      <header className="organization-profile-hero">
        <div className="organization-profile-art" aria-label="Organization photo not provided"><span>{title.charAt(0).toUpperCase()}</span><small>PHOTOS NOT PROVIDED</small></div>
        <div className="organization-profile-heading"><span className="directory-kicker">PUBLIC ORGANIZATION PROFILE</span><p className="organization-profile-type">{typeLabel}</p><h1>{title}</h1><p>{location || 'Location not provided'}</p><div className="organization-profile-actions">{profile.contact && <a className="organization-profile-primary" href={'tel:' + profile.contact.replace(/[^\d+]/g, '')}>Contact organization</a>}{mapUrl && <a className="organization-profile-secondary" href={mapUrl} target="_blank" rel="noreferrer">Open location in map ↗</a>}</div></div>
      </header>
      <section className="organization-profile-content"><div><span className="directory-kicker">ABOUT</span><h2>Care and services</h2><p>{publicOrganizationDescription(profile.description, profile.organization_type)}</p></div><div className="organization-profile-facts">
        <div><small>AGE RANGE</small><strong>{profile.age_range || 'Contact the center'}</strong></div>
        <div><small>CAPACITY</small><strong>{profile.capacity ?? 'Contact the center'}</strong></div>
        <div><small>OPENING HOURS</small><strong>{profile.opening_hours || 'Contact the center'}</strong></div>
        <div><small>FACILITIES & SERVICES</small><strong>{publicOrganizationValue(profile.facilities)}</strong></div>
        <div><small>PUBLISHED FEES</small><strong>{publicOrganizationValue(profile.fees)}</strong></div>
        <div><small>PUBLIC CONTACT</small><strong>{profile.contact || 'Contact details not published'}</strong></div>
      </div></section>
      <p className="organization-profile-privacy">This page shows information the organization shared for public discovery. It does not include child, resident, staff, licensing document, or family records.</p>
    </>}
  </main></>
}
