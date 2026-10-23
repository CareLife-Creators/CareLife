import { useState } from 'react'

const project = (longitude, latitude, zoom) => {
  const size = 256 * (2 ** zoom)
  const latitudeRadians = Math.max(-85.0511, Math.min(85.0511, latitude)) * Math.PI / 180
  return {
    x: ((longitude + 180) / 360) * size,
    y: (0.5 - Math.log((1 + Math.sin(latitudeRadians)) / (1 - Math.sin(latitudeRadians))) / (4 * Math.PI)) * size,
  }
}

export default function BangladeshSatelliteMap({ areas, selectedArea, onSelectArea, label = 'Bangladesh satellite map' }) {
  const [zoom, setZoom] = useState(7)
  const width = 440
  const height = 500
  const tileScale = 0.82
  const activeArea = areas.find((area) => area.id === selectedArea)
  const [centerLongitude, centerLatitude] = activeArea?.coordinates || [90.35, 23.72]
  const center = project(centerLongitude, centerLatitude, zoom)
  const minX = Math.floor((center.x - width / (2 * tileScale)) / 256)
  const maxX = Math.floor((center.x + width / (2 * tileScale)) / 256)
  const minY = Math.floor((center.y - height / (2 * tileScale)) / 256)
  const maxY = Math.floor((center.y + height / (2 * tileScale)) / 256)
  const tiles = []

  for (let x = minX; x <= maxX; x += 1) {
    for (let y = minY; y <= maxY; y += 1) {
      tiles.push({
        key: `${zoom}/${x}/${y}`,
        src: `https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/${zoom}/${y}/${x}`,
        left: `${(((x * 256 - center.x) * tileScale + width / 2) / width) * 100}%`,
        top: `${(((y * 256 - center.y) * tileScale + height / 2) / height) * 100}%`,
      })
    }
  }

  return <div className="family-map-canvas" role="group" aria-label={label}>
    <div className="family-map-tiles" aria-hidden="true">{tiles.map((tile) => <img key={tile.key} src={tile.src} alt="" draggable="false" style={{ left: tile.left, top: tile.top }} />)}</div>
    <div className="family-map-markers">{areas.map((area) => {
      const [longitude, latitude] = area.coordinates
      const point = project(longitude, latitude, zoom)
      const left = (point.x - center.x) * tileScale + width / 2
      const top = (point.y - center.y) * tileScale + height / 2
      return <button type="button" key={area.id} className={'family-map-pin' + (selectedArea === area.id ? ' selected' : '') + (area.count ? ' has-listings' : '')} style={{ left: `${(left / width) * 100}%`, top: `${(top / height) * 100}%` }} aria-label={`${area.name}, ${area.count} organizations`} aria-pressed={selectedArea === area.id} onClick={() => onSelectArea((current) => current === area.id ? 'all' : area.id)}><span>{area.count}</span></button>
    })}</div>
    <div className="family-map-controls" role="group" aria-label="Map zoom controls">
      <button type="button" aria-label="Zoom in" onClick={() => setZoom((current) => Math.min(current + 1, 17))} disabled={zoom >= 17}>+</button>
      <button type="button" aria-label="Zoom out" onClick={() => setZoom((current) => Math.max(current - 1, selectedArea === 'all' ? 5 : 8))} disabled={zoom <= (selectedArea === 'all' ? 5 : 8)}>−</button>
    </div>
    <a className="family-map-attribution" href="https://support.esri.com/en-us/knowledge-base/what-is-the-correct-way-to-cite-an-arcgis-online-basema-000012040" target="_blank" rel="noreferrer">Sources: Esri, Maxar, Earthstar Geographics, GIS User Community</a>
  </div>
}
