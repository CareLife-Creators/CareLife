// Bangladesh country outline from Natural Earth Admin 0 1:110m GeoJSON (public domain).
export const BANGLADESH_BORDER = [[92.672721,22.041239],[92.652257,21.324048],[92.303234,21.475485],[92.368554,20.670883],[92.082886,21.192195],[92.025215,21.70157],[91.834891,22.182936],[91.417087,22.765019],[90.496006,22.805017],[90.586957,22.392794],[90.272971,21.836368],[89.847467,22.039146],[89.70205,21.857116],[89.418863,21.966179],[89.031961,22.055708],[88.876312,22.879146],[88.52977,23.631142],[88.69994,24.233715],[88.084422,24.501657],[88.306373,24.866079],[88.931554,25.238692],[88.209789,25.768066],[88.563049,26.446526],[89.355094,26.014407],[89.832481,25.965082],[89.920693,25.26975],[90.872211,25.132601],[91.799596,25.147432],[92.376202,24.976693],[91.915093,24.130414],[91.46773,24.072639],[91.158963,23.503527],[91.706475,22.985264],[91.869928,23.624346],[92.146035,23.627499],[92.672721,22.041239]]

export const BANGLADESH_BOUNDS = {
  minLon: 88.084422,
  maxLon: 92.672721,
  minLat: 20.670883,
  maxLat: 26.446526,
}

export function bangladeshMapPoint(lon, lat) {
  const { minLon, maxLon, minLat, maxLat } = BANGLADESH_BOUNDS
  return [90 + ((lon - minLon) / (maxLon - minLon)) * 220, 22 + ((maxLat - lat) / (maxLat - minLat)) * 276]
}

export function createBangladeshDots() {
  const points = []
  const { minLon, maxLon, minLat, maxLat } = BANGLADESH_BOUNDS
  for (let lat = minLat + 0.055; lat < maxLat; lat += 0.105) {
    for (let lon = minLon + 0.055; lon < maxLon; lon += 0.105) {
      let inside = false
      for (let i = 0, j = BANGLADESH_BORDER.length - 1; i < BANGLADESH_BORDER.length; j = i++) {
        const [xi, yi] = BANGLADESH_BORDER[i]
        const [xj, yj] = BANGLADESH_BORDER[j]
        if (((yi > lat) !== (yj > lat)) && lon < ((xj - xi) * (lat - yi)) / (yj - yi) + xi) inside = !inside
      }
      if (inside) points.push(bangladeshMapPoint(lon, lat))
    }
  }
  return points
}

// Division capitals are useful area filters. The organization marker is the area,
// not an exact building address; public listings currently contain text locations.
export const BANGLADESH_DIVISIONS = [
  { id: 'dhaka', name: 'Dhaka', aliases: ['dhaka'], coordinates: [90.4125, 23.8103] },
  { id: 'chattogram', name: 'Chattogram', aliases: ['chattogram', 'chittagong'], coordinates: [91.7832, 22.3569] },
  { id: 'rajshahi', name: 'Rajshahi', aliases: ['rajshahi'], coordinates: [88.6042, 24.3745] },
  { id: 'khulna', name: 'Khulna', aliases: ['khulna'], coordinates: [89.5403, 22.8456] },
  { id: 'barishal', name: 'Barishal', aliases: ['barishal', 'barisal'], coordinates: [90.3535, 22.701] },
  { id: 'sylhet', name: 'Sylhet', aliases: ['sylhet'], coordinates: [91.8687, 24.8949] },
  { id: 'rangpur', name: 'Rangpur', aliases: ['rangpur'], coordinates: [89.2752, 25.7439] },
  { id: 'mymensingh', name: 'Mymensingh', aliases: ['mymensingh'], coordinates: [90.4203, 24.7471] },
]
