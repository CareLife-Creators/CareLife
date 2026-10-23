import { useEffect, useState } from 'react'
import { getDaycareDirectory } from '../../api/daycareDirectory'
import './DaycareDirectoryPage.css'
import './DaycareDirectoryLinks.css'
import SiteNav from '../../components/SiteNav'
import { publicOrganizationDescription, publicOrganizationName } from '../../lib/publicDisplay'

function DaycareDirectoryPage() {
  const [search, setSearch] = useState('')
  const [location, setLocation] = useState('')

  const [organizations, setOrganizations] = useState([])
  const [loading, setLoading] = useState(true)

  const [error, setError] = useState('')

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

          </section>
        )}


      </div>
    </main>
    </>
  )
}

export default DaycareDirectoryPage
