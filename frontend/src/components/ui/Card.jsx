/**
 * CareLife surface card. `hover` lifts on hover, `glass` frosts the backdrop,
 * `pad` adds inner padding. Extra className/styles pass through.
 */
function Card({ hover = false, glass = false, pad = false, children, className = '', ...rest }) {
  const classes = [
    'cl-card',
    hover ? 'cl-card--hover' : '',
    glass ? 'cl-card--glass' : '',
    pad ? 'cl-card--pad' : '',
    className,
  ].filter(Boolean).join(' ')

  return (
    <div className={classes} {...rest}>
      {children}
    </div>
  )
}

export default Card