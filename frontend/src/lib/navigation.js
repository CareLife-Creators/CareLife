// Centralize hash navigation so React components do not mutate location directly.
export function navigateToHash(hash) {
  if (typeof window === 'undefined') return
  const value = String(hash || '')
  const target = value.startsWith('#') ? value : `#${value}`
  if (window.location.hash !== target) window.location.hash = target
}
