/**
 * Consistent page header for every authenticated/app page.
 * <PageHeader title="Enrollments" description="Review and manage enrollment requests."
 *   actions={<Button size="sm">Export</Button>} />
 */
function PageHeader({ title, description, actions = null, children }) {
  return (
    <div className="cl-page-header">
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'flex-end', justifyContent: 'space-between', gap: '1rem' }}>
        <div>
          <h1>{title}</h1>
          {description ? <p>{description}</p> : null}
        </div>
        {actions ? <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>{actions}</div> : null}
      </div>
      {children}
    </div>
  )
}

export default PageHeader