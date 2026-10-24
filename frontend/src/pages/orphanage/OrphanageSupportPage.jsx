import { useCallback, useEffect, useState } from 'react'
import SiteNav from '../../components/SiteNav'
import { useSession } from '../../lib/session'
import { canUseDonorFeatures } from '../../lib/roles'
import { publicActivityText, publicContentLabel, publicOrganizationDescription, publicOrganizationName } from '../../lib/publicDisplay'
import { API_BASE_URL } from '../../api/client'
import { createInKindPledge, getDonationCampaigns, getDonationNeeds, getPublicImpactUpdates, getPublicOrphanageProfile } from '../../api/discovery'
import { startBkashPayment, getMyDonationPayments, verifyDonationPayment, getMyInKindPledges } from '../../api/workspace'
import '../DirectoryPages.css'
import '../Workspace.css'

const money = (value, currency = 'BDT') => {
  try { return new Intl.NumberFormat('en-BD', { style: 'currency', currency, maximumFractionDigits: 2 }).format(Number(value) || 0) }
  catch { return currency + ' ' + (Number(value) || 0).toFixed(2) }
}
const date = (value) => {
  const parsed = new Date(value)
  return value && !Number.isNaN(parsed.getTime()) ? parsed.toLocaleDateString() : ''
}
const dateTime = (value) => {
  const parsed = new Date(value)
  return value && !Number.isNaN(parsed.getTime()) ? parsed.toLocaleString() : ''
}
const statusClass = (value) => ['paid', 'success', 'completed'].includes(String(value || '').toLowerCase()) ? 'mint' : ['failed', 'cancelled', 'rejected'].includes(String(value || '').toLowerCase()) ? 'danger' : 'warning'

export default function OrphanageSupportPage() {
  const { signedIn, role } = useSession()
  const [tab, setTab] = useState('campaigns')
  const [campaigns, setCampaigns] = useState([])
  const [needs, setNeeds] = useState([])
  const [updates, setUpdates] = useState([])
  const [payments, setPayments] = useState([])
  const [myPledges, setMyPledges] = useState([])
  const [pledgesLoading, setPledgesLoading] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [amounts, setAmounts] = useState({})
  const [pledgeForms, setPledgeForms] = useState({})
  const [busy, setBusy] = useState('')
  const [messages, setMessages] = useState({})
  const [profile, setProfile] = useState(null)

  const isDonor = canUseDonorFeatures(role, signedIn)

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    const requests = [
      getDonationCampaigns(),
      getDonationNeeds(),
      getPublicImpactUpdates(),
    ]
    if (isDonor) requests.push(getMyDonationPayments())
    const result = await Promise.allSettled(requests)
    setCampaigns(result[0].status === 'fulfilled' && Array.isArray(result[0].value) ? result[0].value : [])
    setNeeds(result[1].status === 'fulfilled' && Array.isArray(result[1].value) ? result[1].value : [])
    setUpdates(result[2].status === 'fulfilled' && Array.isArray(result[2].value) ? result[2].value : [])
    if (isDonor) setPayments(result[3]?.status === 'fulfilled' && Array.isArray(result[3].value) ? result[3].value : [])
    if (result.slice(0, 3).every((item) => item.status === 'rejected')) {
      setError('The campaign, need and impact endpoints all failed to load. Confirm the backend is running, then retry.')
    } else if (isDonor && result[3]?.status === 'rejected') {
      setMessages((current) => ({ ...current, payments: result[3].reason instanceof Error ? result[3].reason.message : 'Payment history could not be loaded.' }))
    }
    setLoading(false)
  }, [isDonor])

  useEffect(() => { void load() }, [load])
  useEffect(() => {
    if (tab !== 'pledges' || !isDonor) return
    let cancelled = false
    setPledgesLoading(true)
    setMessages((current) => ({ ...current, pledges: '' }))
    getMyInKindPledges()
      .then((data) => { if (!cancelled) setMyPledges(Array.isArray(data) ? data : []) })
      .catch((err) => { if (!cancelled) setMessages((current) => ({ ...current, pledges: err instanceof Error ? err.message : 'Pledge history could not be loaded.' })) })
      .finally(() => { if (!cancelled) setPledgesLoading(false) })
    return () => { cancelled = true }
  }, [tab, isDonor])


  async function pledge(event, need) {
    event.preventDefault()
    if (!signedIn) { window.location.hash = '#login'; return }
    if (!isDonor) {
      setMessages((current) => ({ ...current, [need.id]: 'Only Donor / Supporter accounts can submit item pledges.' }))
      return
    }
    const form = pledgeForms[need.id] || {}
    if (!form.quantity || Number(form.quantity) <= 0) {
      setMessages((current) => ({ ...current, [need.id]: 'Enter a quantity greater than zero.' }))
      return
    }
    setBusy(need.id)
    setMessages((current) => ({ ...current, [need.id]: '' }))
    try {
      await createInKindPledge(need.id, { quantity: form.quantity, notes: form.notes || '' })
      setMessages((current) => ({ ...current, [need.id]: 'Pledge submitted. The organization can now review it.' }))
      setPledgeForms((current) => ({ ...current, [need.id]: { quantity: '', notes: '' } }))
    } catch (err) {
      setMessages((current) => ({ ...current, [need.id]: err instanceof Error ? err.message : 'Pledge submission failed.' }))
    } finally { setBusy('') }
  }

  async function payCampaign(event, campaign) {
    event.preventDefault()
    if (!signedIn) { window.location.hash = '#login'; return }
    if (!isDonor) {
      setMessages((current) => ({ ...current, [campaign.id]: 'The backend restricts bKash checkout to the Donor / Supporter role. Sign in with that account type to make this payment.' }))
      return
    }
    const amount = Number(amounts[campaign.id])
    if (!Number.isFinite(amount) || amount <= 0) {
      setMessages((current) => ({ ...current, [campaign.id]: 'Enter a donation amount greater than zero.' }))
      return
    }
    setBusy('pay:' + campaign.id)
    setMessages((current) => ({ ...current, [campaign.id]: '' }))
    try {
      const checkout = await startBkashPayment(campaign.id, amount.toFixed(2))
      if (!checkout?.payment_url) throw new Error('The payment service did not return a checkout URL.')
      const paymentUrl = new URL(checkout.payment_url, window.location.origin)
      if (!['http:', 'https:'].includes(paymentUrl.protocol)) throw new Error('The payment service returned an unsupported URL.')
      window.location.assign(paymentUrl.href)
    } catch (err) {
      setMessages((current) => ({ ...current, [campaign.id]: err instanceof Error ? err.message : 'Could not start bKash checkout.' }))
      setBusy('')
    }
  }

  async function verifyPayment(payment) {
    setBusy('verify:' + payment.id)
    setError('')
    setMessages((current) => ({ ...current, payments: '' }))
    try {
      await verifyDonationPayment(payment.id)
      const latest = await getMyDonationPayments()
      setPayments(Array.isArray(latest) ? latest : [])
      setMessages((current) => ({ ...current, payments: 'Payment verification requested. The history below now reflects the latest API response.' }))
    } catch (err) {
      setMessages((current) => ({ ...current, payments: err instanceof Error ? err.message : 'Payment could not be verified.' }))
    } finally { setBusy('') }
  }

  async function showOrganization(organizationId) {
    setMessages((current) => ({ ...current, profile: '' }))
    try { setProfile(await getPublicOrphanageProfile(organizationId)) }
    catch (err) { setMessages((current) => ({ ...current, profile: err instanceof Error ? err.message : 'Organization profile could not be loaded.' })) }
  }

  const activeCampaigns = campaigns.filter((item) => item.is_active !== false)
  const activeNeeds = needs.filter((item) => item.is_active !== false)
  const publicUpdates = updates.filter((item) => !item.status || String(item.status).toLowerCase() === 'published')
  const tabs = [['campaigns', 'Campaigns'], ['needs', 'In-kind needs'], ['impact', 'Impact updates'], ...(isDonor ? [['pledges', 'My item pledges'], ['payments', 'My payments']] : [])]

  return (
    <>
      <SiteNav />
      <main className="directory-page orphanage">
        <div className="directory-breadcrumb"><a href="#home">CareLife</a> / <a href="#orphanage">Orphanage</a> / Support board</div>
        <header className="directory-hero">
          <span className="directory-kicker">MODULE 02 · ORPHANAGE & COMMUNITY SUPPORT</span>
          <h1>Give to a listed need. Follow what happens next.</h1>
          <p>Compare each organization’s reported fundraising target with the amount received, pledge specific items from an active need, and read impact updates that have been published.</p>
        </header>
        <div className="support-tabs" role="tablist" aria-label="Support board sections">
          {tabs.map(([id, label]) => <button key={id} type="button" role="tab" aria-selected={tab === id} className={tab === id ? 'active' : ''} onClick={() => setTab(id)}>{label}</button>)}
        </div>
        {error && <div className="directory-state error" role="alert"><p>{error}</p><button type="button" onClick={() => void load()}>Retry loading support board</button></div>}
        {loading && <div className="directory-state" role="status">Loading campaigns, item needs and published updates…</div>}

        {!loading && !error && tab === 'campaigns' && <>
          <div className="directory-section-title"><h2>Fundraising campaigns</h2><span>{activeCampaigns.length} active</span></div>
          {!activeCampaigns.length && <div className="directory-state">No active fundraising campaigns are published in the directory.</div>}
          <div className="directory-grid">
            {activeCampaigns.map((campaign) => {
              const target = Number(campaign.target_amount) || 0
              const received = Number(campaign.received_amount) || 0
              const progress = target > 0 ? Math.max(0, Math.min(100, Math.round(received / target * 100))) : 0
              return <article className="directory-card" key={campaign.id}>
                <span className="directory-icon">↗</span>
                <span className="directory-card-label">FUNDRAISING CAMPAIGN</span>
                <h3>{publicContentLabel(campaign.title)}</h3>
                <p className="support-org-name">{publicOrganizationName(campaign.organization_name)}</p>
                {campaign.description && <p>{publicOrganizationDescription(campaign.description, 'orphanage')}</p>}
                <div className="campaign-money">
                  <div><small>RECEIVED</small><strong>{money(received, campaign.currency || 'BDT')}</strong></div>
                  <div><small>TARGET</small><strong>{money(target, campaign.currency || 'BDT')}</strong></div>
                </div>
                <div className="campaign-progress"><span style={{ width: progress + '%' }} /></div>
                <small className="directory-id">{progress}% of the target · {date(campaign.updated_at) ? 'Updated ' + date(campaign.updated_at) : ''}</small>
                <button className="directory-inline-action" type="button" onClick={() => void showOrganization(campaign.organization_id)}>View organization details</button>
                <form className="pledge-form" onSubmit={(event) => void payCampaign(event, campaign)}>
                  <label>Donation amount ({campaign.currency || 'BDT'})<input type="number" min="0.01" step="0.01" value={amounts[campaign.id] || ''} onChange={(event) => setAmounts((current) => ({ ...current, [campaign.id]: event.target.value }))} required /></label>
                  {isDonor ? <button type="submit" disabled={busy === 'pay:' + campaign.id}>{busy === 'pay:' + campaign.id ? 'Opening secure checkout…' : 'Continue with bKash'}</button> : <button type="button" onClick={() => { if (!signedIn) window.location.hash = '#login'; else setMessages((current) => ({ ...current, [campaign.id]: 'Only accounts with the Donor / Supporter role can start bKash checkout.' })) }}>{signedIn ? 'bKash checkout requires donor role' : 'Sign in to donate'}</button>}
                  {messages[campaign.id] && <p role="status">{messages[campaign.id]}</p>}
                </form>
              </article>
            })}
          </div>
          <p className="directory-note">Amounts and progress are read from the campaign response. Payment completion is confirmed by the bKash payment workflow, not by submitting this form alone.</p>
        </>}

        {!loading && !error && tab === 'needs' && <>
          <div className="directory-section-title"><h2>Current organization needs</h2><span>{activeNeeds.length} listed</span></div>
          {!activeNeeds.length && <div className="directory-state">No active donation needs are published.</div>}
          <div className="directory-grid">{activeNeeds.map((need) => {
            const inKind = String(need.need_type).toLowerCase() === 'in_kind'
            const form = pledgeForms[need.id] || {}
            return <article className="directory-card" key={need.id}>
              <span className="directory-icon">{inKind ? '＋' : '৳'}</span><span className="directory-card-label">{need.category}</span>
              <h3>{publicContentLabel(need.title)}</h3><p className="support-org-name">{publicOrganizationName(need.organization_name)}</p>
              {need.description && <p>{publicOrganizationDescription(need.description, 'orphanage')}</p>}
              <div className="campaign-money"><div><small>{inKind ? 'TARGET QUANTITY' : 'TARGET AMOUNT'}</small><strong>{inKind ? [need.target_quantity, need.unit].filter(Boolean).join(' ') : money(need.target_amount, 'BDT')}</strong></div><div><small>NEED TYPE</small><strong>{inKind ? 'Items' : 'Money'}</strong></div></div>
              {inKind ? <form className="pledge-form" onSubmit={(event) => void pledge(event, need)}>
                <label>Quantity to pledge<input type="number" min="0.001" step="0.001" value={form.quantity || ''} onChange={(event) => setPledgeForms((current) => ({ ...current, [need.id]: { ...(current[need.id] || {}), quantity: event.target.value } }))} required /></label>
                <label>Message to the organization (optional)<input maxLength="1000" value={form.notes || ''} onChange={(event) => setPledgeForms((current) => ({ ...current, [need.id]: { ...(current[need.id] || {}), notes: event.target.value } }))} /></label>
                <button type="submit" disabled={busy === need.id}>{busy === need.id ? 'Submitting pledge…' : isDonor ? 'Submit in-kind pledge' : signedIn ? 'Donor account required' : 'Sign in to pledge'}</button>
                {!isDonor && <small>{signedIn ? 'Only Donor / Supporter accounts can submit an item pledge.' : 'Sign in with a Donor / Supporter account to submit an item pledge.'}</small>}
                {messages[need.id] && <p role="status">{messages[need.id]}</p>}
              </form> : <p className="directory-note">This is a monetary need. Use the campaign’s bKash checkout when the organization has published a fundraising campaign for it.</p>}
            </article>
          })}</div>
        </>}

        {!loading && !error && tab === 'impact' && <>
          <div className="directory-section-title"><h2>Published impact updates</h2><span>{publicUpdates.length} updates</span></div>
          {!publicUpdates.length && <div className="directory-state">No impact updates have been published for public viewing yet.</div>}
          <div className="impact-list">{publicUpdates.map((update) => <article className="impact-card" key={update.id}>
            <small>{date(update.published_at || update.created_at)} · {publicOrganizationName(update.organization_name)}</small><h3>{publicContentLabel(update.title)}</h3><p>{publicActivityText(update.content) || 'The organization shared a progress update. Contact them for current details.'}</p>
            {update.media?.length > 0 && <div className="cw-impact-media" aria-label={'Media for ' + update.title}>{update.media.map((media) => media.media_type === 'video' ? <video key={media.id} controls preload="metadata" src={API_BASE_URL + media.url} aria-label={'Video for ' + update.title} /> : <a key={media.id} href={API_BASE_URL + media.url} target="_blank" rel="noreferrer"><img src={API_BASE_URL + media.url} alt={'Organization impact photo for ' + update.title} loading="lazy" /></a>)}</div>}
          </article>)}</div>
        </>}

        {!loading && !error && tab === 'payments' && isDonor && <>
          <div className="directory-section-title"><h2>Your bKash payment records</h2><span>{payments.length} records</span></div>
          {messages.payments && <div className="cw-alert" role="status">{messages.payments}</div>}
          {!payments.length && <div className="directory-state">No donation payment records were returned for this account.</div>}
          <div className="cw-record-list">{payments.map((payment) => <article className="cw-record" key={payment.id}>
            <div className="cw-record-main"><div className="cw-record-title-row"><h3>{payment.campaign_title}</h3><span className={'cw-pill ' + statusClass(payment.status)}>{String(payment.status).replaceAll('_', ' ')}</span></div>
              <p>{money(payment.amount, payment.currency)} · Invoice {payment.merchant_invoice_number}</p>
              <small>{dateTime(payment.created_at)}{payment.bkash_transaction_id ? ' · Transaction ' + payment.bkash_transaction_id : ''}</small>
              {payment.failure_reason && <p>{payment.failure_reason}</p>}
            </div>
            {['pending', 'created', 'failed'].includes(String(payment.status).toLowerCase()) && <button type="button" className="cw-button" disabled={busy === 'verify:' + payment.id} onClick={() => void verifyPayment(payment)}>{busy === 'verify:' + payment.id ? 'Verifying…' : 'Verify payment status'}</button>}
          </article>)}</div>
        </>}

        {!loading && !error && tab === 'pledges' && isDonor && <>
          <div className="directory-section-title"><h2>Your in-kind pledges</h2><span>{myPledges.length} records</span></div>
          {messages.pledges && <div className="cw-alert error" role="alert">{messages.pledges}</div>}
          {pledgesLoading && <div className="directory-state" role="status">Loading your pledge history…</div>}
          {!pledgesLoading && !messages.pledges && !myPledges.length && <div className="directory-state">No item pledges have been submitted from this account yet.</div>}
          {!pledgesLoading && <div className="cw-record-list">{myPledges.map((pledge) => <article className="cw-record" key={pledge.id}>
            <div className="cw-record-main"><div className="cw-record-title-row"><h3>{pledge.need_title}</h3><span className={'cw-pill ' + statusClass(pledge.status)}>{String(pledge.status).replaceAll('_', ' ')}</span></div>
              <p>{pledge.quantity} {pledge.unit} · {pledge.organization_name}</p>
              {pledge.notes && <p>{pledge.notes}</p>}
              <small>Submitted {dateTime(pledge.created_at)} · Pledge ID: {pledge.id}</small>
              {pledge.received_at && <small>Received {dateTime(pledge.received_at)}</small>}
              {pledge.allocated_at && <small>Allocated {dateTime(pledge.allocated_at)}</small>}
            </div>
          </article>)}</div>}
          <p className="directory-note">The status shown here is the organization’s returned record: pledged, received, or allocated. Contact the organization if a status needs clarification.</p>
        </>}

        {profile && <section className="organization-public-panel"><button type="button" onClick={() => setProfile(null)}>Close details ×</button><p className="directory-kicker">PUBLIC ORGANIZATION PROFILE</p><h2>{publicOrganizationName(profile.organization_name)}</h2><p>{publicOrganizationDescription(profile.description, 'orphanage')}</p><p>{[profile.location, profile.contact].filter(Boolean).join(' · ')}</p><p>{[profile.capacity != null ? 'Capacity ' + profile.capacity : '', profile.age_range, profile.opening_hours, profile.facilities, profile.fees].filter(Boolean).join(' · ')}</p><span>{String(profile.verification_status || '').replaceAll('_', ' ')}</span></section>}
        {messages.profile && <div className="directory-state error" role="alert">{messages.profile}</div>}
        <aside className="directory-privacy"><strong>Public transparency, private records.</strong> The public board exposes campaign and impact information returned by the backend. Private child details do not belong in public fundraising records.</aside>
      </main>
    </>
  )
}
