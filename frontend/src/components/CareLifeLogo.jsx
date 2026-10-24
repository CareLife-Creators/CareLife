// The CareLife mark: one C made of three arcs, one for each module
// (lavender: elderly care, peach: orphanage, mint: daycare).
const SEGMENTS = [[50, 131, '#8f7be8'], [139, 220, '#f59a6b'], [228, 309, '#2bb596']]

function point(angle) {
  const rad = (angle * Math.PI) / 180
  return [(50 + 32 * Math.cos(rad)).toFixed(2), (50 + 32 * Math.sin(rad)).toFixed(2)]
}

function CareLifeLogo({ size = 32, title = 'CareLife' }) {
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" role="img" aria-label={title} focusable="false">
      {SEGMENTS.map(([from, to, color]) => {
        const [x0, y0] = point(from)
        const [x1, y1] = point(to)
        return (
          <path key={from} d={`M ${x0} ${y0} A 32 32 0 0 1 ${x1} ${y1}`} fill="none" stroke={color} strokeWidth="15" strokeLinecap="round" />
        )
      })}
    </svg>
  )
}

export default CareLifeLogo