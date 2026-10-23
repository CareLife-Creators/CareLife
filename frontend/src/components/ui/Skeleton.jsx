/**
 * Loading skeletons. Variants: text | card | avatar | button.
 * Use `lines` to stack several text bars (e.g. <Skeleton lines={3}/>).
 */
function Skeleton({ variant = 'text', lines = 1, className = '', style }) {
  if (variant === 'text' && lines > 1) {
    return (
      <div className={className} style={style} aria-hidden="true">
        {Array.from({ length: lines }, (_, i) => (
          <div key={i} className="cl-skeleton cl-skeleton--text" style={{ width: i === lines - 1 ? '62%' : '100%' }} />
        ))}
      </div>
    )
  }
  const cls = variant === 'text' ? 'cl-skeleton--text' : `cl-skeleton--${variant}`
  return <div className={`cl-skeleton ${cls} ${className}`.trim()} style={style} aria-hidden="true" />
}

export default Skeleton