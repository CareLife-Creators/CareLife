export function distanceKm(from, to) {
  const radians = (degrees) => (degrees * Math.PI) / 180
  const lat1 = Number(from?.latitude)
  const lon1 = Number(from?.longitude)
  const lat2 = Number(to?.latitude)
  const lon2 = Number(to?.longitude)
  if (![lat1, lon1, lat2, lon2].every(Number.isFinite)) return null
  const dLat = radians(lat2 - lat1)
  const dLon = radians(lon2 - lon1)
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(radians(lat1)) * Math.cos(radians(lat2)) * Math.sin(dLon / 2) ** 2
  return 6371 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

export function requestApproximateLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('This browser cannot provide a location. Search by city or area instead.'))
      return
    }
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => resolve({ latitude: coords.latitude, longitude: coords.longitude }),
      (error) => reject(new Error(error.code === error.PERMISSION_DENIED
        ? 'Location permission was declined. You can still search by city or area.'
        : 'Your location is unavailable right now. You can still search by city or area.')),
      { enableHighAccuracy: false, maximumAge: 300000, timeout: 10000 },
    )
  })
}

export function withDistance(items, origin) {
  if (!origin) return items
  return items.map((item) => ({ ...item, distance_km: distanceKm(origin, item) }))
    .sort((a, b) => {
      if (a.distance_km == null) return 1
      if (b.distance_km == null) return -1
      return a.distance_km - b.distance_km
    })
}
