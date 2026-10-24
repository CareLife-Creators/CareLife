import { useEffect, useMemo, useState } from 'react'
import { getDaycareDirectory } from '../../api/daycareDirectory'
import OrganizationSatelliteMap from '../../components/OrganizationSatelliteMap'
import './DaycareDirectoryPage.css'
import './DaycareDirectoryLinks.css'
import '../DirectoryLocation.css'
import SiteNav from '../../components/SiteNav'
import { publicOrganizationDescription, publicOrganizationName } from '../../lib/publicDisplay'
import { requestApproximateLocation, withDistance } from '../../lib/geo'

function DaycareDirectoryPage() {
  const [search, setSearch] = useState('')
  const [location, setLocation] = useState('')

  const [organizations, setOrganizations] = useState([])
  const [loading, setLoading] = useState(true)

  const [error, setError] = useState('')
  const [origin, setOrigin] = useState(null)
  const [locationMessage, setLocationMessage] = useState('')
  const [locationBusy, setLocationBusy] = useState(false)
  const [selectedOrganizationId, setSelectedOrganizationId] = useState('')
  const nearbyOrganizations = useMemo(() => withDistance(organizations, origin), [organizations, origin])

  async function findNearby() {
    setLocationBusy(true)
    setLocationMessage('')
    try {
      const current = await requestApproximateLocation()
      setOrigin(current)
      setLocationMessage('Nearby centers are sorted by straight-line distance. Your location stays in this browser and is not saved to CareLife.')
    } catch (err) {
      setLocationMessage(err instanceof Error ? err.message : 'Location is unavailable. Search by city or area instead.')
    } finally {
      setLocationBusy(false)
    }
  }

  async function loadDirectory(
    currentSearch = search,
    currentLocation = location
  ) {
    setLoading(true)
    setError('')

    try {
      const data = await getDaycareDirectory({
        search: currentSearch,
        location: currentLocation,
      })

      setOrganizations(data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to load daycare directory'
      )

      setOrganizations([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let cancelled = false
    getDaycareDirectory({ search: '', location: '' })
      .then((data) => {
        if (cancelled) return
        setOrganizations(Array.isArray(data) ? data : [])
        setError('')
      })
      .catch((err) => {
        if (cancelled) return
        setError(err instanceof Error ? err.message : 'Unable to load daycare directory')
        setOrganizations([])
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => { cancelled = true }
  }, [])

  function handleSubmit(event) {
    event.preventDefault()

    loadDirectory(search, location)
  }

  function handleClear() {
    setSearch('')
    setLocation('')
    loadDirectory('', '')
  }

  return (
    <>
    <SiteNav />
    <main className="daycare-directory">
      <div className="daycare-directory-container">

        <header className="daycare-directory-header">
          <div>
            <p className="daycare-directory-eyebrow">
              CARELIFE DAYCARE DIRECTORY
            </p>

            <h1>
              Find a daycare center
            </h1>

            <p>
              Search daycare centers by name,
              location, or public organization information.
            </p>
          </div>
        </header>


        <section className="daycare-search-card">
          <form onSubmit={handleSubmit}>

            <div className="daycare-search-fields">

              <div className="daycare-field">
                <label htmlFor="daycare-search">
                  Search
                </label>

                <input
                  id="daycare-search"
                  type="text"
                  value={search}
                  onChange={(event) =>
                    setSearch(event.target.value)
                  }
                  placeholder="Daycare name or keyword"
                />
              </div>


              <div className="daycare-field">
                <label htmlFor="daycare-location">
                  Location
                </label>

                <input
                  id="daycare-location"
                  type="text"
                  value={location}
                  onChange={(event) =>
                    setLocation(event.target.value)
                  }
                  placeholder="City or area"
                />
              </div>


              <button
                type="submit"
                className="daycare-search-button"
              >
                Search
              </button>


              <button
                type="button"
                className="daycare-clear-button"
                onClick={handleClear}
              >
                Clear
              </button>

            </div>

          </form>
          <div className="directory-nearby-tools">
            <button type="button" onClick={findNearby} disabled={locationBusy}>{locationBusy ? 'Finding your location…' : origin ? 'Refresh nearby centers' : 'Use my location for nearby centers'}</button>
            {origin && <button type="button" className="directory-location-clear" onClick={() => { setOrigin(null); setLocationMessage('') }}>Clear location</button>}
            {locationMessage && <p role="status">{locationMessage}</p>}
          </div>
        </section>


        {error && (
          <div className="daycare-directory-message error">
            {error}
          </div>
        )}



        {loading ? (
          <div className="daycare-directory-empty">
            Loading daycare centers...
          </div>
        ) : error ? null : organizations.length === 0 ? (
          <div className="daycare-directory-empty">

            <h2>
              No daycare centers found
            </h2>

            <p>
              Try another search term or location.
            </p>

          </div>
        ) : (
          <section className="daycare-results">

            <div className="daycare-results-heading">

              <div>
                <span>
                  DAYCARE RESULTS
                </span>

                <h2>
                  {organizations.length} daycare
                  {organizations.length === 1
                    ? ''
                    : 's'} found
                </h2>
              </div>

            </div>


            <div className="daycare-results-grid">

                {nearbyOrganizations.map(
                (organization) => (
                  <article
                    className="daycare-card"
                    key={organization.organization_id}
                  >

                    <div className="daycare-card-top">

                      <div>

                        <span className="daycare-type">
                          {organization.organization_type}
                        </span>

                        <h3>
                          {
                            publicOrganizationName(organization.organization_name)
                          }
                        </h3>

                      </div>


                    </div>


                    <div className="daycare-card-details">

                      <div>
                        <span>
                          Location
                        </span>

                        <strong>
                          {organization.location ||
                            'Not provided'}
                        </strong>
                      </div>


                      <div>
                        <span>
                          Contact
                        </span>

                        <strong>
                          {organization.contact ||
                            'Not provided'}
                        </strong>
                      </div>

                    </div>


                    <p className="daycare-description">
                      {publicOrganizationDescription(organization.description, 'daycare')}
                    </p>

                    <div className="daycare-nearby-meta">
                      {organization.distance_km != null ? <strong>{organization.distance_km < 10 ? organization.distance_km.toFixed(1) : Math.round(organization.distance_km)} km away</strong> : <span>{origin ? 'Location not published for distance search' : 'Distance available when you share your location'}</span>}
                      {organization.latitude != null && organization.longitude != null && <a href={`https://www.google.com/maps/dir/?api=1&destination=${organization.latitude},${organization.longitude}`} target="_blank" rel="noreferrer">Directions ↗</a>}
                    </div>


                    <a
                      className="daycare-details-button"
                      href={`#organization-profile?type=daycare&id=${encodeURIComponent(organization.organization_id)}`}
                    >
                      View Public Details
                    </a>

                  </article>
                )
              )}

            </div>

            {nearbyOrganizations.some((organization) => organization.latitude != null && organization.longitude != null) && <section className="daycare-nearby-map" aria-label="Map of listed daycare centers"><div><strong>{origin ? 'Centers near your location' : 'Daycare locations'}</strong><span>Only verified public listing coordinates are shown. No children or family locations are displayed.</span></div><OrganizationSatelliteMap organizations={nearbyOrganizations.filter((organization) => organization.latitude != null && organization.longitude != null).map((organization) => ({ ...organization, organization_name: organization.organization_name }))} selectedId={selectedOrganizationId} onSelect={setSelectedOrganizationId} centerLocation={origin} startZoom={origin ? 10 : 7} /></section>}

          </section>
        )}


      </div>
    </main>
    </>
  )
}

export default DaycareDirectoryPage
