import { useEffect, useMemo, useState } from 'react'
import SiteNav from '../../components/SiteNav'
import OrganizationSatelliteMap from '../../components/OrganizationSatelliteMap'
import { getElderCareDirectory } from '../../api/discovery'
import { requestApproximateLocation, withDistance } from '../../lib/geo'
import '../DirectoryPages.css'
import '../DirectoryLocation.css'

export default function ElderCareDirectoryPage() {
  const [filters, setFilters] = useState({ search: '', location: '', facility: '' })
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [origin, setOrigin] = useState(null)
  const [locationMessage, setLocationMessage] = useState('')
  const [locationBusy, setLocationBusy] = useState(false)
  const [selectedId, setSelectedId] = useState('')
  const nearbyHomes = useMemo(() => withDistance(items, origin), [items, origin])

  async function load(values = filters) {
    setLoading(true)
    setError('')
    try { const data = await getElderCareDirectory(values); setItems(Array.isArray(data) ? data : []) }
    catch (err) { setError(err instanceof Error ? err.message : 'Unable to load directory.'); setItems([]) }
    finally { setLoading(false) }
  }

  useEffect(() => {
    let cancelled = false
    getElderCareDirectory().then((data) => { if (!cancelled) setItems(Array.isArray(data) ? data : []) })
      .catch((err) => { if (!cancelled) { setError(err instanceof Error ? err.message : 'Unable to load directory.'); setItems([]) } })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  async function findNearby() {
    setLocationBusy(true); setLocationMessage('')
    try { setOrigin(await requestApproximateLocation()); setLocationMessage('Care homes are sorted by straight-line distance. Your location stays in this browser and is not saved to CareLife.') }
    catch (err) { setLocationMessage(err instanceof Error ? err.message : 'Location is unavailable. Search by city or area instead.') }
    finally { setLocationBusy(false) }
  }

  function change(key, value) { setFilters((current) => ({ ...current, [key]: value })) }

  return <>
    <SiteNav />
    <main className="directory-page elder">
      <div className="directory-breadcrumb"><a href="#home">CareLife</a> / <a href="#elderly-care">Elderly Care</a> / Directory</div>
      <header className="directory-hero"><span className="directory-kicker">MODULE 03 · ELDERLY CARE</span><h1>Find a care home that fits your family.</h1><p>Compare verified public listings by location, facilities, capacity, opening hours and published fees. Resident details remain private.</p></header>
      <form className="directory-filters" onSubmit={(event) => { event.preventDefault(); void load(filters) }}>
        <label>Search<input value={filters.search} onChange={(event) => change('search', event.target.value)} placeholder="Care-home name or keyword" /></label>
        <label>Location<input value={filters.location} onChange={(event) => change('location', event.target.value)} placeholder="City or area" /></label>
        <label>Facility<input value={filters.facility} onChange={(event) => change('facility', event.target.value)} placeholder="Facility or service" /></label>
        <button>Search homes</button>
        <button type="button" className="filter-clear" onClick={() => { const empty = { search: '', location: '', facility: '' }; setFilters(empty); void load(empty) }}>Clear</button>
      </form>
      <div className="directory-nearby-tools"><button type="button" onClick={findNearby} disabled={locationBusy}>{locationBusy ? 'Finding your location…' : origin ? 'Refresh nearby homes' : 'Use my location for nearby homes'}</button>{origin && <button type="button" className="directory-location-clear" onClick={() => { setOrigin(null); setLocationMessage('') }}>Clear location</button>}{locationMessage && <p role="status">{locationMessage}</p>}</div>
      <div className="directory-section-title"><h2>{origin ? 'Care homes nearest to you' : 'Care homes'}</h2>{!loading && <span>{nearbyHomes.length} listings</span>}</div>
      {loading && <div className="directory-state" role="status">Loading care-home listings…</div>}
      {!loading && error && <div className="directory-state error" role="alert"><strong>Directory unavailable</strong><p>{error}</p><button onClick={() => void load(filters)} type="button">Try again</button></div>}
      {!loading && !error && !nearbyHomes.length && <div className="directory-state"><strong>No matching care homes</strong><p>Try a broader search or clear your filters.</p></div>}
      {!loading && !error && nearbyHomes.length > 0 && <>
        <div className="directory-grid">{nearbyHomes.map((home) => <article className="directory-card" key={home.organization_id}>
          <span className="directory-icon" aria-hidden="true">⌂</span><span className="directory-card-label">Verified public listing</span><h3>{home.organization_name}</h3><p>{home.description || 'No public description provided.'}</p>
          <div className="directory-facts"><div><small>LOCATION</small><strong>{home.location || 'Not listed'}</strong></div><div><small>CAPACITY</small><strong>{home.capacity ?? 'Not listed'}</strong></div><div><small>FACILITIES</small><strong>{home.facilities || 'Contact provider'}</strong></div><div><small>FEES</small><strong>{home.fees || 'Contact provider'}</strong></div></div>
          {home.opening_hours && <p className="directory-meta">Hours: {home.opening_hours}</p>}
          <div className="directory-nearby-meta">{home.distance_km != null ? <strong>{home.distance_km < 10 ? home.distance_km.toFixed(1) : Math.round(home.distance_km)} km away</strong> : <span>{origin ? 'Location not published for distance search' : 'Distance available when you share your location'}</span>}{home.latitude != null && home.longitude != null && <a href={`https://www.google.com/maps/dir/?api=1&destination=${home.latitude},${home.longitude}`} target="_blank" rel="noreferrer">Directions ↗</a>}</div>
          <a className="elder-profile-link" href={`#organization-profile?type=elderly_care&id=${encodeURIComponent(home.organization_id)}`}>View care home profile <span aria-hidden="true">→</span></a>
          {home.contact && <a className="directory-contact" href={'tel:' + home.contact.replace(/[^\d+]/g, '')}>Contact care home ↗</a>}
        </article>)}</div>
        {nearbyHomes.some((home) => home.latitude != null && home.longitude != null) && <section className="directory-nearby-map"><div><strong>{origin ? 'Care homes near your location' : 'Care-home locations'}</strong><span>Only verified public listing coordinates are shown. Resident and family locations are never shown here.</span></div><OrganizationSatelliteMap organizations={nearbyHomes.filter((home) => home.latitude != null && home.longitude != null)} selectedId={selectedId} onSelect={setSelectedId} centerLocation={origin} startZoom={origin ? 10 : 7} /></section>}
      </>}
      <aside className="directory-privacy"><strong>Privacy matters.</strong> Public listings do not expose resident records or family check-in information. Those workflows require care-home authorization.</aside>
    </main>
  </>
}
