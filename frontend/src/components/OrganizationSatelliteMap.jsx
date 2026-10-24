import { useMemo, useState } from 'react'
import './OrganizationSatelliteMap.css'
import './OrganizationSatelliteMapLocation.css'

const project = (longitude, latitude, zoom) => {
  const size = 256 * (2 ** zoom)
  const rad = Math.max(-85.0511, Math.min(85.0511, latitude)) * Math.PI / 180
  return { x: ((longitude + 180) / 360) * size, y: (0.5 - Math.log((1 + Math.sin(rad)) / (1 - Math.sin(rad))) / (4 * Math.PI)) * size }
}

export default function OrganizationSatelliteMap({ organizations = [], selectedId, onSelect, value, onPick, centerLocation, startZoom = 7 }) {
  const centerKey = centerLocation ? `${centerLocation.latitude}:${centerLocation.longitude}:${startZoom}` : ''
  const [zoomState, setZoomState] = useState({ centerKey, value: startZoom })
  const zoom = zoomState.centerKey === centerKey ? zoomState.value : startZoom
  const changeZoom = (update) => setZoomState((current) => ({
    centerKey,
    value: update(current.centerKey === centerKey ? current.value : startZoom),
  }))
  const width = 560
  const height = 390
  const scale = 0.8
  const located = organizations.filter((org) => org.latitude != null && org.longitude != null && Number.isFinite(Number(org.latitude)) && Number.isFinite(Number(org.longitude)) && Number(org.latitude) >= -90 && Number(org.latitude) <= 90 && Number(org.longitude) >= -180 && Number(org.longitude) <= 180)
  const selected = located.find((org) => org.organization_id === selectedId)
  const hasValue = value?.latitude != null && value?.longitude != null
  const [lon, lat] = hasValue ? [Number(value.longitude), Number(value.latitude)] : centerLocation ? [Number(centerLocation.longitude), Number(centerLocation.latitude)] : selected ? [Number(selected.longitude), Number(selected.latitude)] : [90.35, 23.72]
  const center = project(lon, lat, zoom)
  const tiles = useMemo(() => {
    const result = []
    const minX = Math.floor((center.x - width / (2 * scale)) / 256)
    const maxX = Math.floor((center.x + width / (2 * scale)) / 256)
    const minY = Math.floor((center.y - height / (2 * scale)) / 256)
    const maxY = Math.floor((center.y + height / (2 * scale)) / 256)
    for (let x = minX; x <= maxX; x += 1) for (let y = minY; y <= maxY; y += 1) result.push({ key: `${zoom}/${x}/${y}`, url: `https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/${zoom}/${y}/${x}`, left: `${(((x * 256 - center.x) * scale + width / 2) / width) * 100}%`, top: `${(((y * 256 - center.y) * scale + height / 2) / height) * 100}%` })
    return result
  }, [center.x, center.y, zoom])

  function pickLocation(event) {
    if (!onPick || event.target.closest('button, a')) return
    const rect = event.currentTarget.getBoundingClientRect()
    const x = ((event.clientX - rect.left) / rect.width) * width
    const y = ((event.clientY - rect.top) / rect.height) * height
    const worldX = center.x + (x - width / 2) / scale
    const worldY = center.y + (y - height / 2) / scale
    const size = 256 * (2 ** zoom)
    const longitude = worldX / size * 360 - 180
    const latitude = Math.atan(Math.sinh(Math.PI * (1 - 2 * worldY / size))) * 180 / Math.PI
    onPick({ latitude: Number(latitude.toFixed(6)), longitude: Number(longitude.toFixed(6)) })
  }

  return <div className={'org-satellite-map' + (onPick ? ' is-picker' : '')} role="group" aria-label={onPick ? 'Select exact organization location on satellite map' : 'Satellite map with submitted organization locations'} onClick={pickLocation}>
    <div className="org-satellite-tiles" aria-hidden="true">{tiles.map((tile) => <img key={tile.key} src={tile.url} alt="" style={{ left: tile.left, top: tile.top }} />)}</div>
    <div className="org-satellite-pins">{centerLocation && <span className="org-satellite-user-pin" aria-label="Your approximate location, shown only in this browser" title="Your approximate location" />}{located.map((org) => {
      const point = project(Number(org.longitude), Number(org.latitude), zoom)
      const left = (point.x - center.x) * scale + width / 2
      const top = (point.y - center.y) * scale + height / 2
      if (left < -20 || left > width + 20 || top < -20 || top > height + 20) return null
      return <button type="button" key={org.organization_id} className={'org-satellite-pin' + (org.organization_id === selectedId ? ' selected' : '')} style={{ left: `${left / width * 100}%`, top: `${top / height * 100}%` }} aria-label={`Locate ${org.organization_name}`} aria-pressed={org.organization_id === selectedId} title={org.organization_name} onClick={() => { onSelect(org.organization_id); changeZoom((value) => Math.max(value, 16)) }}><span /></button>
    })}{onPick && hasValue && (() => { const point = project(Number(value.longitude), Number(value.latitude), zoom); const left = (point.x - center.x) * scale + width / 2; const top = (point.y - center.y) * scale + height / 2; return <span className="org-satellite-picker-pin" style={{ left: `${left / width * 100}%`, top: `${top / height * 100}%` }} aria-label="Selected organization location" /> })()}</div>
    <div className="org-satellite-controls"><button type="button" aria-label="Zoom in" onClick={() => changeZoom((value) => Math.min(18, value + 1))}>+</button><button type="button" aria-label="Zoom out" onClick={() => changeZoom((value) => Math.max(5, value - 1))}>−</button></div>
    <span className="org-satellite-label">{onPick ? 'Click the map to set a location · zoom in for precision' : 'Satellite view · select a pin to zoom to the submitted location'}</span>
    <a className="org-satellite-attribution" href="https://support.esri.com/en-us/knowledge-base/what-is-the-correct-way-to-cite-an-arcgis-online-basema-000012040" target="_blank" rel="noreferrer">Esri · Maxar imagery</a>
  </div>
}
