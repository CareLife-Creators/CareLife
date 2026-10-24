/**
 * CareLife status badge. Tone maps to the platform's semantic colors.
 * tones: success | warning | danger | info | neutral | verified
 */
function Badge({ tone = 'neutral', children, className = '', ...rest }) {
  return (
    <span className={`cl-badge cl-badge--${tone} ${className}`.trim()} {...rest}>
      {children}
    </span>
  )
}

export default Badge