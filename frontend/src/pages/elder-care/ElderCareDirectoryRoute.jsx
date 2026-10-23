import { useEffect, useState } from 'react'
import SiteNav from '../../components/SiteNav'
import { publicOrganizationDescription, publicOrganizationName } from '../../lib/publicDisplay'
import { getElderCareDirectory } from '../../api/discovery'
import '../DirectoryPages.css'
import './ElderCareDirectoryRoute.css'

export default function ElderCareDirectoryRoute() {
  const [filters, setFilters] = useState({ search: '', location: '', facility: '' })
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function load(values = filters) {
    setLoading(true); setError('')
    try { const data = await getElderCareDirectory(values); setItems(Array.isArray(data) ? data : []) }
    catch (err) { setError(err instanceof Error ? err.message : 'Unable to load care homes.'); setItems([]) }
    finally { setLoading(false) }
  }
  useEffect(() => { let cancelled = false; getElderCareDirectory().then((data) => { if (!cancelled) setItems(Array.isArray(data) ? data : []) }).catch((err) => { if (!cancelled) { setError(err instanceof Error ? err.message : 'Unable to load care homes.'); setItems([]) } }).finally(() => { if (!cancelled) setLoading(false) }); return () => { cancelled = true } }, [])

  return <><SiteNav/><main className="directory-page elder"><div className="directory-breadcrumb"><a href="#elderly-care">Elderly Care</a> / Directory</div>
    <header className="directory-hero"><span className="directory-kicker">ELDERLY CARE DIRECTORY</span><h1>Find thoughtful care, closer to home.</h1><p>Compare public care-home information, explore each organization’s profile, and contact the provider directly.</p></header>
    <form className="directory-filters" onSubmit={(event) => { event.preventDefault(); void load(filters) }}><label>Search<input value={filters.search} onChange={(event) => setFilters({ ...filters, search: event.target.value })} placeholder="Care-home name or keyword"/></label><label>Location<input value={filters.location} onChange={(event) => setFilters({ ...filters, location: event.target.value })} placeholder="City or area"/></label><label>Facility<input value={filters.facility} onChange={(event) => setFilters({ ...filters, facility: event.target.value })} placeholder="Facility or service"/></label><button>Search homes</button><button type="button" className="filter-clear" onClick={() => { const empty = { search: '', location: '', facility: '' }; setFilters(empty); void load(empty) }}>Clear</button></form>
    <div className="directory-section-title"><h2>Care homes</h2>{!loading && <span>{items.length} listings</span>}</div>
    {loading && <div className="directory-state" role="status">Loading care homes…</div>}{!loading && error && <div className="directory-state error" role="alert"><strong>Care-home listings unavailable</strong><p>{error}</p><button type="button" onClick={() => void load()}>Try again</button></div>}{!loading && !error && !items.length && <div className="directory-state"><strong>No care homes found</strong><p>Try a wider search or clear your filters.</p></div>}
    {!loading && !error && !!items.length && <div className="directory-grid">{items.map((org) => <article className="directory-card" key={org.organization_id}><span className="directory-icon">⌂</span><span className="directory-card-label">Care home</span><h3>{publicOrganizationName(org.organization_name)}</h3><p>{publicOrganizationDescription(org.description, 'elderly_care')}</p><div className="directory-facts"><div><small>LOCATION</small><strong>{org.location || 'Not listed'}</strong></div><div><small>CAPACITY</small><strong>{org.capacity ?? 'Not listed'}</strong></div><div><small>FACILITIES</small><strong>{org.facilities || 'Ask the provider'}</strong></div><div><small>PUBLISHED FEES</small><strong>{org.fees || 'Ask the provider'}</strong></div></div><a className="elder-profile-link" href={`#organization-profile?type=elderly_care&id=${encodeURIComponent(org.organization_id)}`}>View care home profile <span aria-hidden="true">→</span></a></article>)}</div>}
    <aside className="directory-privacy"><strong>Private care stays private.</strong> Listings contain public organization details only. Resident and family records require authorization.</aside>
  </main></>
}
