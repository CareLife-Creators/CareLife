import { useEffect, useState } from 'react'
import {
  getDaycareDirectory,
  getPublicDaycare,
} from '../../api/daycareDirectory'
import './DaycareDirectoryPage.css'

function DaycareDirectoryPage() {
  const [search, setSearch] = useState('')
  const [location, setLocation] = useState('')

  const [organizations, setOrganizations] = useState([])
  const [selectedOrganization, setSelectedOrganization] =
    useState(null)

  const [loading, setLoading] = useState(true)
  const [detailsLoading, setDetailsLoading] =
    useState(false)

  const [error, setError] = useState('')
  const [detailsError, setDetailsError] =
    useState('')

  async function loadDirectory(
    currentSearch = search,
    currentLocation = location
  ) {
    setLoading(true)
    setError('')
    setDetailsError('')
    setSelectedOrganization(null)

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
    loadDirectory('', '')
  }, [])

  async function handleViewDetails(
    organizationId
  ) {
    setDetailsLoading(true)
    setDetailsError('')

    try {
      const data = await getPublicDaycare(
        organizationId
      )

      setSelectedOrganization(data)
    } catch (err) {
      setDetailsError(
        err instanceof Error
          ? err.message
          : 'Unable to load daycare details'
      )

      setSelectedOrganization(null)
    } finally {
      setDetailsLoading(false)
    }
  }

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
    <main className="daycare-directory">
      <div className="daycare-directory-container">

        <header className="daycare-directory-header">
          <div>
            <p className="daycare-directory-eyebrow">
              CARELIFE DAYCARE DIRECTORY
            </p>

            <h1>
              Find a Verified Daycare
            </h1>

            <p>
              Search verified daycare centers by name,
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
        </section>


        {error && (
          <div className="daycare-directory-message error">
            {error}
          </div>
        )}


        {detailsError && (
          <div className="daycare-directory-message error">
            {detailsError}
          </div>
        )}


        {loading ? (
          <div className="daycare-directory-empty">
            Loading verified daycare centers...
          </div>
        ) : organizations.length === 0 ? (
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
                  VERIFIED RESULTS
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

              {organizations.map(
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
                            organization.organization_name
                          }
                        </h3>

                      </div>

                      <span className="daycare-verified">
                        Verified
                      </span>

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
                      {organization.description ||
                        'No public description available.'}
                    </p>


                    <button
                      type="button"
                      className="daycare-details-button"
                      onClick={() =>
                        handleViewDetails(
                          organization.organization_id
                        )
                      }
                    >
                      View Public Details
                    </button>

                  </article>
                )
              )}

            </div>

          </section>
        )}


        {detailsLoading && (
          <div className="daycare-directory-message">
            Loading daycare details...
          </div>
        )}


        {selectedOrganization && (
          <section className="daycare-detail-card">

            <div className="daycare-detail-header">

              <div>
                <span>
                  PUBLIC DAYCARE DETAILS
                </span>

                <h2>
                  {
                    selectedOrganization.organization_name
                  }
                </h2>
              </div>


              <button
                type="button"
                onClick={() =>
                  setSelectedOrganization(null)
                }
              >
                Close
              </button>

            </div>


            <div className="daycare-detail-grid">

              <div>
                <span>
                  Organization Type
                </span>

                <strong>
                  {
                    selectedOrganization.organization_type
                  }
                </strong>
              </div>


              <div>
                <span>
                  Location
                </span>

                <strong>
                  {selectedOrganization.location ||
                    'Not provided'}
                </strong>
              </div>


              <div>
                <span>
                  Contact
                </span>

                <strong>
                  {selectedOrganization.contact ||
                    'Not provided'}
                </strong>
              </div>


              <div className="daycare-detail-description">
                <span>
                  Description
                </span>

                <p>
                  {selectedOrganization.description ||
                    'No public description available.'}
                </p>
              </div>

            </div>

          </section>
        )}

      </div>
    </main>
  )
}

export default DaycareDirectoryPage