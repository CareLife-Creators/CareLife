/**
 * Friendly empty state. `icon` accepts any inline SVG/ReactNode.
 * Provide `action` (e.g. a <Button/>) when there is a useful next step.
 */
function EmptyState({ icon = null, title, description = '', action = null }) {
  return (
    <div className="cl-empty" role="status">
      {icon ? <div className="cl-empty-icon" aria-hidden="true">{icon}</div> : null}
      <h3>{title}</h3>
      {description ? <p>{description}</p> : null}
      {action}
    </div>
  )
}

export default EmptyState