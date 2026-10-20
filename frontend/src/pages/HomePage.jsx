import { useEffect, useRef, useState } from 'react'
import './Landing.css'

const go = (hash) => { window.location.hash = hash }
const scrollToId = (id) => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })

const TICKER = [
  ['Daycare', 'Nila arrived at 8:42'],
  ['Orphanage', '12 school bags pledged today'],
  ['Elderly care', 'Evening check-in completed'],
]

function DaycareScene() {
  const [arrived, setArrived] = useState({ Nila: false, Rafi: false, Tania: false })
  const [view, setView] = useState('staff')
  const toggle = (name) => setArrived((s) => ({ ...s, [name]: !s[name] }))
  return (
    <div className="lp-scene" aria-label="Sample daycare attendance">
      <div className="lp-seg" role="tablist">
        {['staff', 'parent'].map((v) => (
          <button key={v} role="tab" aria-selected={view === v} className={view === v ? 'on' : ''} onClick={() => setView(v)}>
            {v === 'staff' ? 'Staff screen' : 'Parent screen'}
          </button>
        ))}
      </div>
      {view === 'staff' ? (
        <ul className="lp-rows">
          {Object.keys(arrived).map((n) => (
            <li key={n}><span>{n}</span>
              <button className={arrived[n] ? 'chip on' : 'chip'} aria-pressed={arrived[n]} onClick={() => toggle(n)}>
                {arrived[n] ? 'Arrived' : 'Mark arrived'}
              </button></li>
          ))}
        </ul>
      ) : (
        <div className="lp-status">
          <strong>Nila</strong>
          <span className={arrived.Nila ? 'lp-pill on' : 'lp-pill'}>{arrived.Nila ? 'Arrived at daycare' : 'Not arrived yet'}</span>
          <small>Switch to the staff screen and mark Nila to see this change.</small>
        </div>
      )}
      <p className="lp-sample">Sample data</p>
    </div>
  )
}

function OrphanageScene() {
  const [needs, setNeeds] = useState([['School bags', 0], ['Blankets', 0], ['Rice (5 kg)', 0]])
  const change = (i, d) => setNeeds((list) => list.map((n, j) => (j === i ? [n[0], Math.max(0, n[1] + d)] : n)))
  const total = needs.reduce((a, n) => a + n[1], 0)
  return (
    <div className="lp-scene" aria-label="Sample pledge builder">
      <ul className="lp-rows">
        {needs.map(([name, qty], i) => (
          <li key={name}><span>{name}</span>
            <span className="lp-step">
              <button aria-label={'Fewer ' + name} onClick={() => change(i, -1)}>−</button>
              <b>{qty}</b>
              <button aria-label={'More ' + name} onClick={() => change(i, 1)}>+</button>
            </span></li>
        ))}
      </ul>
      <div className="lp-slip">{total ? 'Your pledge: ' + needs.filter((n) => n[1]).map((n) => n[1] + ' × ' + n[0]).join(', ') : 'Choose what you can give.'}</div>
      <p className="lp-sample">Sample needs list</p>
    </div>
  )
}

const DAYS = [['Sat', 'Walked in the garden after lunch.'], ['Sun', 'Check-in completed. Blood pressure noted by the nurse.'], ['Mon', 'Video call with family at 6 pm.'], ['Tue', 'Check-in completed.'], ['Wed', 'Caregiver visit booked for Thursday.'], ['Thu', 'Caregiver visit completed.'], ['Fri', 'Prayer and a quiet afternoon.']]

function ElderlyScene() {
  const [day, setDay] = useState(2)
  return (
    <div className="lp-scene" aria-label="Sample check-in week">
      <div className="lp-week">
        {DAYS.map(([d], i) => (
          <button key={d} className={i === day ? 'on' : ''} aria-pressed={i === day} onClick={() => setDay(i)}>{d}</button>
        ))}
      </div>
      <p className="lp-note" aria-live="polite">{DAYS[day][1]}</p>
      <p className="lp-sample">Sample check-ins</p>
    </div>
  )
}

const CHAPTERS = [
  { id: 'daycare', title: 'Know your child arrived.', text: 'Parents search daycares, enroll a child and follow attendance. Staff mark arrivals from their own screen, so what a parent sees comes from the person at the door.', scene: <DaycareScene />, cta: ['Explore daycares', '#daycare'] },
  { id: 'orphanage', title: 'Give what is actually needed.', text: 'Orphanages post campaigns and a list of in-kind needs. Donors pledge items or give through bKash, then read the impact updates the organization publishes.', scene: <OrphanageScene />, cta: ['See how support works', '#orphanage'] },
  { id: 'elderly', title: 'Stay close to someone far away.', text: 'Find a care home or an independent caregiver, book care, and follow check-ins as the family representative.', scene: <ElderlyScene />, cta: ['Find elderly care', '#elderly-care'] },
]

function HomePage() {
  const [chapter, setChapter] = useState(-1)
  const [tick, setTick] = useState(0)
  const story = useRef(null)
  const path = useRef(null)
  const dot = useRef(null)
  const svg = useRef(null)

  useEffect(() => {
    const id = setInterval(() => setTick((t) => (t + 1) % TICKER.length), 3200)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    const el = story.current, p = path.current, d = dot.current, s = svg.current
    let len = 0, frame = 0
    function build() {
      const h = el.offsetHeight, x = window.innerWidth < 820 ? 14 : 36
      let dstr = 'M ' + x + ' 0'
      for (let y = 0; y < h; y += 160) dstr += ' Q ' + (x + ((y / 160) % 2 ? 12 : -12)) + ' ' + (y + 80) + ' ' + x + ' ' + (y + 160)
      s.setAttribute('height', h)
      p.setAttribute('d', dstr)
      len = p.getTotalLength()
      p.style.strokeDasharray = len
      update()
    }
    function update() {
      frame = 0
      const r = el.getBoundingClientRect(), vh = window.innerHeight
      const prog = Math.min(1, Math.max(0, (vh * 0.5 - r.top) / r.height))
      p.style.strokeDashoffset = len * (1 - prog)
      const pt = p.getPointAtLength(len * prog)
      d.setAttribute('cx', pt.x); d.setAttribute('cy', pt.y)
      let active = -1
      el.querySelectorAll('[data-chapter]').forEach((c, i) => { if (c.getBoundingClientRect().top < vh * 0.6) active = i })
      setChapter(active)
    }
    const onScroll = () => { if (!frame) frame = requestAnimationFrame(update) }
    build()
    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', build)
    const ro = new ResizeObserver(build)
    ro.observe(el)
    return () => { window.removeEventListener('scroll', onScroll); window.removeEventListener('resize', build); ro.disconnect(); cancelAnimationFrame(frame) }
  }, [])

  return (
    <div className="lp" data-ch={chapter}>
      <header className="lp-nav">
        <a className="lp-brand" href="#home" aria-label="CareLife home"><span aria-hidden="true">C</span>CareLife</a>
        <nav aria-label="Page sections">
          <button onClick={() => scrollToId('daycare')}>Daycare</button>
          <button onClick={() => scrollToId('orphanage')}>Orphanage</button>
          <button onClick={() => scrollToId('elderly')}>Elderly care</button>
        </nav>
        <div className="lp-nav-end"><button onClick={() => go('#login')}>Sign in</button><button className="lp-cta" onClick={() => go('#signup')}>Get started</button></div>
      </header>

      <section className="lp-hero">
        <h1>Care you can check on.</h1>
        <p>Daycares, orphanages and elderly-care homes on one platform. CareLife reviews organizations, and an administrator approves every staff account.</p>
        <div className="lp-actions"><button className="lp-cta" onClick={() => go('#signup')}>Create an account</button><button className="lp-ghost" onClick={() => scrollToId('daycare')}>See how it works</button></div>
        <p className="lp-ticker" aria-live="off"><small>Sample activity</small><span key={tick}><b>{TICKER[tick][0]}</b> {TICKER[tick][1]}</span></p>
      </section>

      <div className="lp-story" ref={story}>
        <svg className="lp-thread" ref={svg} width="80" aria-hidden="true"><path ref={path} d="" /><circle ref={dot} r="7" cx="36" cy="0" /></svg>
        {CHAPTERS.map((c) => (
          <section className="lp-chapter" id={c.id} data-chapter key={c.id}>
            <div><h2>{c.title}</h2><p>{c.text}</p><button className="lp-link" onClick={() => go(c.cta[1])}>{c.cta[0]}</button></div>
            {c.scene}
          </section>
        ))}
      </div>

      <footer className="lp-end">
        <h2>Start with one account.</h2>
        <div className="lp-actions"><button className="lp-cta" onClick={() => go('#signup')}>Get started</button><button className="lp-ghost" onClick={() => go('#login')}>Sign in</button></div>
        <small>© 2026 CareLife</small>
      </footer>
    </div>
  )
}

export default HomePage