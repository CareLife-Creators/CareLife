import { useEffect, useRef, useState } from 'react'
import { markLoaderSeen } from '../lib/loader'
import './PageLoader.css'

const W = 360
const H = 360
const CX = 180
const CY = 150
const R = 92
const RAD = Math.PI / 180
const COLORS = ['#b9a9ff', '#ffb38f', '#6fe3c0']
const SEGMENTS = [[50, 131], [139, 220], [228, 309]]
const BANGLADESH = [23.7 * RAD, 90.4 * RAD]
const SPEED = 1.5
const END = 6.6

const dots = []
for (let lat = -80; lat <= 80; lat += 9) {
  const count = Math.max(1, Math.round(40 * Math.cos(lat * RAD)))
  for (let i = 0; i < count; i += 1) dots.push([lat * RAD, (i / count) * 2 * Math.PI - Math.PI])
}

const ease = (t) => 1 - Math.pow(1 - Math.min(1, Math.max(0, t)), 3)
const span = (t, a, b) => Math.min(1, Math.max(0, (t - a) / (b - a)))

function draw(g, t) {
  g.clearRect(0, 0, W, H)
  const glow = g.createRadialGradient(CX, CY, 10, CX, CY, 170)
  glow.addColorStop(0, 'rgba(47,170,140,.35)')
  glow.addColorStop(1, 'rgba(11,59,51,0)')
  g.fillStyle = glow
  g.fillRect(0, 0, W, H)

  const globeAlpha = 1 - ease(span(t, 3.2, 4.4))
  const scale = 1 - 0.35 * ease(span(t, 3.2, 4.4))
  if (globeAlpha > 0) {
    const lon0 = -2.1 + (BANGLADESH[1] + 2.1) * ease(span(t, 0, 2.4))
    const lat0 = BANGLADESH[0]
    for (const [lat, lon] of dots) {
      const d = lon - lon0
      const z = Math.sin(lat0) * Math.sin(lat) + Math.cos(lat0) * Math.cos(lat) * Math.cos(d)
      if (z <= 0) continue
      const x = Math.cos(lat) * Math.sin(d)
      const y = Math.cos(lat0) * Math.sin(lat) - Math.sin(lat0) * Math.cos(lat) * Math.cos(d)
      g.globalAlpha = globeAlpha * (0.25 + 0.6 * z)
      g.fillStyle = '#8be9cf'
      g.beginPath()
      g.arc(CX + x * R * scale, CY - y * R * scale, 1.6, 0, 7)
      g.fill()
    }
    g.globalAlpha = globeAlpha * 0.5
    g.strokeStyle = '#6fe3c0'
    g.lineWidth = 1.5
    g.beginPath()
    g.arc(CX, CY, R * scale, 0, 7)
    g.stroke()
    g.globalAlpha = 1
  }

  const appear = ease(span(t, 2.3, 3.1))
  const travel = ease(span(t, 3.2, 4.4))
  const fade = 1 - ease(span(t, 4.2, 4.8))
  if (appear > 0 && fade > 0) {
    SEGMENTS.forEach(([from, to], i) => {
      const a = ((from + to) / 2) * RAD
      const ox = Math.cos(i * 2.09 + 1) * 14
      const oy = Math.sin(i * 2.09 + 1) * 14
      const x = CX + ox + (Math.cos(a) * 62 - ox) * travel
      const y = CY + oy + (Math.sin(a) * 62 - oy) * travel
      g.globalAlpha = appear * fade
      g.fillStyle = COLORS[i]
      g.shadowColor = COLORS[i]
      g.shadowBlur = 16
      g.beginPath()
      g.arc(x, y, 5 + 3 * appear, 0, 7)
      g.fill()
      g.shadowBlur = 0
      g.globalAlpha = 1
    })
  }

  const drawn = ease(span(t, 3.6, 4.9))
  if (drawn > 0) {
    g.lineWidth = 13
    g.lineCap = 'round'
    SEGMENTS.forEach(([from, to], i) => {
      g.strokeStyle = COLORS[i]
      g.shadowColor = COLORS[i]
      g.shadowBlur = 14
      g.beginPath()
      g.arc(CX, CY, 62, from * RAD, (from + (to - from) * drawn) * RAD)
      g.stroke()
      g.shadowBlur = 0
    })
  }

  const label = ease(span(t, 4.8, 5.8))
  if (label > 0) {
    g.globalAlpha = label
    g.fillStyle = '#eafff7'
    g.font = '800 34px "Bricolage Grotesque", system-ui, sans-serif'
    g.textAlign = 'center'
    g.fillText('CareLife', CX, CY + R + 40 - 6 * (1 - label))
    g.globalAlpha = 1
  }
}

function PageLoader({ onDone }) {
  const canvas = useRef(null)
  const finishRef = useRef(() => {})
  const [leaving, setLeaving] = useState(false)

  useEffect(() => {
    const cv = canvas.current
    const dpr = window.devicePixelRatio || 1
    cv.width = W * dpr
    cv.height = H * dpr
    const g = cv.getContext('2d')
    g.scale(dpr, dpr)

    let raf = 0
    let timer = 0
    let finished = false
    const start = performance.now()

    finishRef.current = () => {
      if (finished) return
      finished = true
      cancelAnimationFrame(raf)
      markLoaderSeen()
      setLeaving(true)
      timer = window.setTimeout(onDone, 500)
    }

    function loop(now) {
      const t = ((now - start) / 1000) * SPEED
      draw(g, Math.min(t, END))
      if (t >= END) finishRef.current()
      else raf = requestAnimationFrame(loop)
    }
    raf = requestAnimationFrame(loop)

    return () => {
      finished = true
      cancelAnimationFrame(raf)
      window.clearTimeout(timer)
    }
  }, [onDone])

  return (
    <div className={leaving ? 'cl-loader leaving' : 'cl-loader'} role="status" aria-label="Loading CareLife">
      <canvas ref={canvas} aria-hidden="true" />
      <button type="button" className="cl-loader-skip" onClick={() => finishRef.current()}>Skip</button>
    </div>
  )
}

export default PageLoader