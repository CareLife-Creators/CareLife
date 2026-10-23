import { useEffect, useMemo, useRef, useState } from 'react'
import CareLifeLogo from '../components/CareLifeLogo'
import { bangladeshMapPoint, createBangladeshDots } from '../data/bangladeshMap'
import './Landing.css'

const go = (hash) => { window.location.hash = hash }
const scrollToId = (id) => document.getElementById(id)?.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' })

function DaycareScene() {
  const [arrived, setArrived] = useState({ Nila: false, Rafi: false, Tania: false })
  const [view, setView] = useState('daycare')
  const toggle = (name) => setArrived((state) => ({ ...state, [name]: !state[name] }))
  return <div className="lp-scene" aria-label="Daycare attendance preview">
    <div className="lp-scene-head"><span className="lp-demo-mark">01</span><div><strong>Today at Little Steps</strong><small>Preview · sample data</small></div></div>
    <div className="lp-seg" aria-label="Choose a preview"><button type="button" aria-pressed={view === 'daycare'} className={view === 'daycare' ? 'on' : ''} onClick={() => setView('daycare')}>Daycare view</button><button type="button" aria-pressed={view === 'parent'} className={view === 'parent' ? 'on' : ''} onClick={() => setView('parent')}>Parent view</button></div>
    {view === 'daycare' ? <ul className="lp-rows">{Object.keys(arrived).map((name) => <li key={name}><span><i className="lp-avatar" aria-hidden="true">{name[0]}</i>{name}</span><button type="button" className={arrived[name] ? 'chip on' : 'chip'} aria-pressed={arrived[name]} onClick={() => toggle(name)}>{arrived[name] ? 'Arrived · 8:42' : 'Mark arrived'}</button></li>)}</ul> : <div className="lp-status" aria-live="polite"><div className="lp-parent-note"><i className="lp-avatar lp-avatar-large" aria-hidden="true">N</i><div><small>Nila’s update</small><strong>{arrived.Nila ? 'She’s arrived.' : 'No arrival update yet.'}</strong><span>{arrived.Nila ? 'Little Steps · Today, 8:42 am' : 'Her latest update will appear here.'}</span></div></div>{!arrived.Nila && <button className="lp-inline-action" type="button" onClick={() => setView('daycare')}>See the daycare preview <span aria-hidden="true">→</span></button>}</div>}
  </div>
}

function OrphanageScene() {
  const [needs, setNeeds] = useState([['School bags', 0], ['Warm blankets', 0], ['Rice · 5 kg', 0]])
  const change = (index, delta) => setNeeds((list) => list.map((item, i) => i === index ? [item[0], Math.max(0, item[1] + delta)] : item))
  const total = needs.reduce((amount, item) => amount + item[1], 0)
  return <div className="lp-scene" aria-label="Orphanage needs and pledge preview"><div className="lp-scene-head"><span className="lp-demo-mark">02</span><div><strong>Needs this month</strong><small>Preview · sample data</small></div></div><ul className="lp-rows">{needs.map(([name, quantity], index) => <li key={name}><span>{name}</span><span className="lp-step"><button type="button" aria-label={'Fewer ' + name} onClick={() => change(index, -1)}>−</button><b aria-live="polite">{quantity}</b><button type="button" aria-label={'Add ' + name} onClick={() => change(index, 1)}>+</button></span></li>)}</ul><div className={total ? 'lp-slip has-items' : 'lp-slip'} aria-live="polite"><span className="lp-slip-icon" aria-hidden="true">♡</span><div><strong>{total ? 'Your pledge' : 'Build a small pledge'}</strong><span>{total ? needs.filter((item) => item[1]).map((item) => item[1] + ' × ' + item[0]).join(' · ') : 'Choose a few items from the list.'}</span></div><span className="lp-slip-count">{total}</span></div></div>
}

const DAYS = [['Sat', 'A slow morning and a walk in the garden.'], ['Sun', 'A call with family after lunch.'], ['Mon', 'Nurse check-in · feeling well today.'], ['Tue', 'Tea with a neighbour in the courtyard.'], ['Wed', 'A visit from family at 6 pm.'], ['Thu', 'Care visit completed this afternoon.'], ['Fri', 'Prayer, music and a quiet afternoon.']]
function ElderlyScene() {
  const [day, setDay] = useState(2)
  return <div className="lp-scene" aria-label="Elderly care weekly check-in preview"><div className="lp-scene-head"><span className="lp-demo-mark">03</span><div><strong>This week with Amma</strong><small>Preview · sample data</small></div></div><div className="lp-week" aria-label="Choose a day">{DAYS.map(([label], index) => <button type="button" key={label} className={index === day ? 'on' : ''} aria-pressed={index === day} onClick={() => setDay(index)}>{label}</button>)}</div><div className="lp-note-card" aria-live="polite"><span className="lp-note-icon" aria-hidden="true">✳</span><div><small>{DAYS[day][0]} · Family note</small><p>{DAYS[day][1]}</p></div></div></div>
}

const PLACES = [
  { id: 'dhaka', city: 'Dhaka', area: 'Uttara', module: 'Daycare', type: 'daycare', color: '#42c5a0', title: 'Little Steps Daycare', detail: 'A sample daycare preview in Uttara.', point: bangladeshMapPoint(90.4125, 23.8103) },
  { id: 'rajshahi', city: 'Rajshahi', area: 'Rajshahi city', module: 'Orphanage', type: 'orphanage', color: '#ff956d', title: 'Shapla Children’s Home', detail: 'A sample needs list from Rajshahi.', point: bangladeshMapPoint(88.6042, 24.3745) },
  { id: 'chattogram', city: 'Chattogram', area: 'Chattogram city', module: 'Elderly care', type: 'elderly', color: '#a99bff', title: 'Shanti Care Home', detail: 'A sample family check-in from Chattogram.', point: bangladeshMapPoint(91.7832, 22.3569) },
]
const FILTERS = [{ id: 'all', label: 'All previews' }, { id: 'daycare', label: 'Daycare' }, { id: 'orphanage', label: 'Orphanage' }, { id: 'elderly', label: 'Elderly care' }]

function BangladeshMap() {
  const [filter, setFilter] = useState('all')
  const [selected, setSelected] = useState(PLACES[0])
  const dots = useMemo(createBangladeshDots, [])
  const visible = PLACES.filter((place) => filter === 'all' || place.type === filter)
  const chooseFilter = (id) => { setFilter(id); if (id !== 'all') setSelected(PLACES.find((place) => place.type === id)) }
  return <section className="lp-map-section" id="bangladesh" aria-labelledby="lp-map-title">
    <div className="lp-map-copy"><span className="lp-kicker">Care, close to home</span><h2 id="lp-map-title">A little closer,<br />wherever you are.</h2><p>Explore a few sample places across Bangladesh. Each pin is just a preview.</p><div className="lp-filters" aria-label="Filter map previews">{FILTERS.map((item) => <button type="button" key={item.id} aria-pressed={filter === item.id} className={filter === item.id ? 'active' : ''} onClick={() => chooseFilter(item.id)}>{item.label}</button>)}</div>
      <article className="lp-place-card" aria-live="polite" key={selected.id}><div className="lp-place-top"><span className={'lp-place-dot ' + selected.type} /><span>{selected.module} · Preview</span><span className="lp-place-area">{selected.area}</span></div><h3>{selected.title}</h3><p>{selected.detail}</p></article>
      <p className="lp-map-source">Bangladesh outline: Natural Earth · Public domain</p>
    </div>
    <div className="lp-map-visual"><div className="lp-map-meta"><span>Bangladesh</span><span>Sample places <i aria-hidden="true" /></span></div><div className="lp-map-canvas"><svg viewBox="0 0 400 360" role="img" aria-label="Dotted outline map of Bangladesh with three sample location pins"><defs><radialGradient id="lp-map-glow"><stop stopColor="#3cc1a0" stopOpacity=".14" /><stop offset="1" stopColor="#3cc1a0" stopOpacity="0" /></radialGradient></defs><circle cx="202" cy="180" r="172" fill="url(#lp-map-glow)" />{dots.map(([x, y], index) => <circle key={index} cx={x} cy={y} r="1.55" className="lp-map-dot" />)}</svg>
      {visible.map((place) => <button type="button" key={place.id} className={'lp-map-pin ' + place.type + (selected.id === place.id ? ' selected' : '')} style={{ left: `${place.point[0] / 4}%`, top: `${place.point[1] / 3.6}%`, '--pin': place.color }} aria-label={`${place.module} preview in ${place.city}`} aria-pressed={selected.id === place.id} onClick={() => setSelected(place)}><span /></button>)}
      <span className="lp-map-label lp-map-label-dhaka" aria-hidden="true">Dhaka</span><span className="lp-map-label lp-map-label-sylhet" aria-hidden="true">Sylhet</span><span className="lp-map-label lp-map-label-bay" aria-hidden="true">Bay of Bengal</span></div><p className="lp-map-footnote">Pins show sample locations, not real organizations.</p></div>
  </section>
}

const CHAPTERS = [
  { id: 'daycare', type: 'daycare', index: '01', title: 'See the moment your child arrives.', text: 'Find a daycare, keep up with daily attendance and see important updates from your child’s day.', scene: <DaycareScene />, action: 'Explore daycare', href: '#daycare' },
  { id: 'orphanage', type: 'orphanage', index: '02', title: 'Give what is needed most.', text: 'See what a children’s home needs, pledge useful items and follow the difference your support makes.', scene: <OrphanageScene />, action: 'Explore orphanage support', href: '#orphanage' },
  { id: 'elderly-care', type: 'elderly', index: '03', title: 'Stay close, even from far away.', text: 'Find a care home or caregiver, arrange care and keep family close through thoughtful check-ins.', scene: <ElderlyScene />, action: 'Explore elderly care', href: '#elderly-care' },
]

function HomePage() {
  const [chapter, setChapter] = useState(-1)
  const story = useRef(null); const path = useRef(null); const dot = useRef(null); const stops = useRef(null); const svg = useRef(null)
  useEffect(() => {
    const element = story.current; const storyPath = path.current; const storyDot = dot.current; const storySvg = svg.current
    const storyStops = stops.current
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    let length = 0; let frame = 0
    function build() {
      const height = element.offsetHeight; const x = window.innerWidth < 820 ? 10 : 32
      let pathData = `M ${x} 0`
      for (let y = 0; y < height; y += 180) pathData += ` Q ${x + (y / 180 % 2 ? 9 : -9)} ${y + 90} ${x} ${y + 180}`
      storySvg.setAttribute('height', height); storyPath.setAttribute('d', pathData); length = storyPath.getTotalLength(); storyPath.style.strokeDasharray = length; update()
      const namespace = 'http://www.w3.org/2000/svg'
      const colors = { daycare: 'daycare', orphanage: 'orphanage', elderly: 'elderly' }
      const markers = [...element.querySelectorAll('[data-chapter]')].map((section) => {
        const point = storyPath.getPointAtLength(length * Math.min(1, (section.offsetTop + 34) / height))
        return { point, type: colors[section.dataset.type] }
      })
      storyStops.replaceChildren(...markers.map(({ point, type }) => {
        const group = document.createElementNS(namespace, 'g')
        group.setAttribute('class', `lp-thread-stop lp-thread-stop-${type}`)
        group.setAttribute('transform', `translate(${point.x} ${point.y})`)
        const halo = document.createElementNS(namespace, 'circle')
        halo.setAttribute('class', 'lp-thread-stop-halo'); halo.setAttribute('r', '10')
        const core = document.createElementNS(namespace, 'circle')
        core.setAttribute('class', 'lp-thread-stop-core'); core.setAttribute('r', '3.5')
        group.append(halo, core)
        return group
      }))
    }
    function place(elementToMove, point) {
      elementToMove.setAttribute('cx', point.x)
      elementToMove.setAttribute('cy', point.y)
    }
    function update() {
      frame = 0
      if (reducedMotion) {
        storyPath.style.strokeDashoffset = 0
        const point = storyPath.getPointAtLength(0)
        place(storyDot, point)
        return
      }
      const bounds = element.getBoundingClientRect(); const progress = Math.min(1, Math.max(0, (window.innerHeight * 0.52 - bounds.top) / bounds.height))
      const distance = length * progress; const point = storyPath.getPointAtLength(distance)
      storyPath.style.strokeDashoffset = length * (1 - progress)
      place(storyDot, point)
    }
    const onScroll = () => { if (!frame) frame = requestAnimationFrame(update) }
    const observer = new IntersectionObserver((entries) => { const active = entries.filter((entry) => entry.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0]; if (active) setChapter(CHAPTERS.findIndex((item) => item.id === active.target.id)) }, { rootMargin: '-20% 0px -35% 0px', threshold: [0, 0.15, 0.4, 0.7] })
    element.querySelectorAll('[data-chapter]').forEach((item) => observer.observe(item)); build(); window.addEventListener('scroll', onScroll, { passive: true }); window.addEventListener('resize', build)
    const resizeObserver = new ResizeObserver(build); resizeObserver.observe(element)
    return () => { window.removeEventListener('scroll', onScroll); window.removeEventListener('resize', build); resizeObserver.disconnect(); observer.disconnect(); cancelAnimationFrame(frame) }
  }, [])
  return <div className="lp" data-ch={chapter}>
    <header className="lp-nav"><a className="lp-brand" href="#home" aria-label="CareLife home"><CareLifeLogo size={34} />CareLife</a><nav aria-label="Page sections"><button type="button" onClick={() => scrollToId('daycare')}>Daycare</button><button type="button" onClick={() => scrollToId('orphanage')}>Orphanage</button><button type="button" onClick={() => scrollToId('elderly-care')}>Elderly care</button><button type="button" onClick={() => scrollToId('bangladesh')}>Our map</button></nav><div className="lp-nav-end"><button type="button" onClick={() => go('#login')}>Sign in</button><button type="button" className="lp-cta" onClick={() => go('#signup')}>Create an account</button></div></header>
    <main>
      <section className="lp-hero"><div className="lp-hero-copy"><span className="lp-kicker">Care, made closer</span><h1>Care you can count on.</h1><p className="lp-intro">Find care for your family, support a children’s home or stay close to an older loved one—all with CareLife.</p><div className="lp-actions"><button type="button" className="lp-cta" onClick={() => go('#signup')}>Create an account <span aria-hidden="true">→</span></button><button type="button" className="lp-ghost" onClick={() => go('#login')}>Sign in</button></div></div><div className="lp-hero-art" aria-hidden="true"><div className="lp-orbit lp-orbit-one" /><div className="lp-orbit lp-orbit-two" /><div className="lp-hero-sun">Care<br />lives<br />here<span>♡</span></div><span className="lp-art-label lp-art-one">Little moments</span><span className="lp-art-label lp-art-two">Closer together</span><span className="lp-art-star">✳</span></div><button className="lp-scroll-cue" type="button" onClick={() => scrollToId('daycare')}><span>One place for the people who matter</span><i aria-hidden="true">↓</i></button></section>
      <div className="lp-story" ref={story}><svg className="lp-thread" ref={svg} width="72" aria-hidden="true"><defs><linearGradient id="lp-thread-gradient" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#17806a" /><stop offset="50%" stopColor="#d9562a" /><stop offset="100%" stopColor="#5846b4" /></linearGradient></defs><path ref={path} d="" /><g ref={stops} className="lp-thread-stops" /><circle ref={dot} className="lp-thread-dot" r="7" cx="32" cy="0" /></svg>{CHAPTERS.map((item) => <section className="lp-chapter" id={item.id} data-chapter key={item.id} data-type={item.type}><div className="lp-chapter-copy"><span className="lp-chapter-number">{item.index} <i /></span><span className="lp-kicker">{item.type === 'daycare' ? 'Daycare' : item.type === 'orphanage' ? 'Orphanage support' : 'Elderly care'}</span><h2>{item.title}</h2><p>{item.text}</p><a className={`lp-explore-link ${item.type}`} href={item.href}>{item.action}<span aria-hidden="true">→</span></a></div>{item.scene}</section>)}</div>
      <BangladeshMap />
      <section className="lp-end"><span className="lp-kicker">For every kind of care</span><h2>Start with the people<br />who matter to you.</h2><p>CareLife brings everyday care and thoughtful support a little closer.</p><div className="lp-actions"><button type="button" className="lp-cta" onClick={() => go('#signup')}>Create an account <span aria-hidden="true">→</span></button><button type="button" className="lp-ghost" onClick={() => go('#login')}>Sign in</button></div><a className="lp-org-link" href="#for-organizations">Do you run a care organization? Learn how to join CareLife <span aria-hidden="true">→</span></a></section>
    </main><footer className="lp-footer"><a className="lp-brand" href="#home" aria-label="CareLife home"><CareLifeLogo size={28} />CareLife</a><a className="lp-footer-org-link" href="#for-organizations">For organizations</a><span>Care, made closer.</span><small>© 2026 CareLife</small></footer>
  </div>
}
export default HomePage
