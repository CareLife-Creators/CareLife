const EMPTY_TEXT_VALUES = new Set(['null', 'undefined', 'none', 'n/a', 'na'])

function cleanPublicText(value, maxLength = 1200) {
  if (typeof value !== 'string' && typeof value !== 'number') return ''
  if (typeof value === 'number' && !Number.isFinite(value)) return ''

  const text = Array.from(String(value))
    .filter((character) => {
      const code = character.charCodeAt(0)
      return !(
        (code >= 0 && code <= 8) ||
        code === 11 ||
        code === 12 ||
        (code >= 14 && code <= 31) ||
        code === 127
      )
    })
    .join('')
    .replace(/\s+/g, ' ')
    .trim()

  if (!text || EMPTY_TEXT_VALUES.has(text.toLowerCase())) return ''
  return text.slice(0, maxLength)
}

// Public-facing copy stays as plain strings; React safely escapes it at render time.
export function publicOrganizationName(value) {
  return cleanPublicText(value, 160)
}

export function publicOrganizationDescription(value) {
  return cleanPublicText(value, 1600)
}

export function publicOrganizationValue(value, fallback = 'Not provided') {
  return cleanPublicText(value, 500) || fallback
}

export function publicActivityText(value) {
  return cleanPublicText(value, 2000)
}

export function publicContentLabel(value) {
  return cleanPublicText(value, 180)
}
