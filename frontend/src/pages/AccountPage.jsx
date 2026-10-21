import { useEffect, useState } from 'react'
import SiteNav from '../components/SiteNav'
import {
  getMyProfile, updateMyProfile, getMyNotifications, markNotificationRead,
  getMyConversations, startConversation, getConversationMessages, sendConversationMessage,
} from '../api/workspace'
import './Workspace.css'

const prettyDate = (value) => {
  const date = new Date(value)
  return value && !Number.isNaN(date.getTime()) ? date.toLocaleString() : 'Time not provided'
}

export default function AccountPage() {
  const [tab, setTab] = useState('profile')
  const [profile, setProfile] = useState(null)
  const [profileForm, setProfileForm] = useState({ full_name: '', phone: '' })
  const [notifications, setNotifications] = useState([])
  const [conversations, setConversations] = useState([])
  const [selectedConversation, setSelectedConversation] = useState('')
  const [messages, setMessages] = useState([])
  const [recipientId, setRecipientId] = useState('')
  const [draft, setDraft] = useState('')
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  async function loadInbox() {
    const [notificationResult, conversationResult] = await Promise.allSettled([getMyNotifications(), getMyConversations()])
    if (notificationResult.status === 'fulfilled') setNotifications(Array.isArray(notificationResult.value) ? notificationResult.value : [])
    if (conversationResult.status === 'fulfilled') {
      const list = Array.isArray(conversationResult.value) ? conversationResult.value : []
      setConversations(list)
      if (!selectedConversation && list[0]?.id) setSelectedConversation(list[0].id)
    }
    if (notificationResult.status === 'rejected' && conversationResult.status === 'rejected') {
      setError('Inbox data could not be loaded. Check your session and try again.')
    }
  }

  async function loadPage() {
    setLoading(true)
    setError('')
    try {
      const current = await getMyProfile()
      setProfile(current)
      setProfileForm({ full_name: current.full_name || '', phone: current.phone || '' })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load your CareLife profile.')
    }
    await loadInbox()
    setLoading(false)
  }

  useEffect(() => { void loadPage() }, [])

  useEffect(() => {
    if (!selectedConversation) {
      setMessages([])
      return
    }
    let cancelled = false
    getConversationMessages(selectedConversation)
      .then((data) => { if (!cancelled) setMessages(Array.isArray(data) ? data : []) })
      .catch((err) => { if (!cancelled) setError(err instanceof Error ? err.message : 'Could not load messages.') })
    return () => { cancelled = true }
  }, [selectedConversation])

  async function saveProfile(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    setMessage('')
    try {
      const updated = await updateMyProfile({ full_name: profileForm.full_name.trim() || null, phone: profileForm.phone.trim() || null })
      setProfile(updated)
      setProfileForm({ full_name: updated.full_name || '', phone: updated.phone || '' })
      setMessage('Profile details saved.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Profile changes were not saved.')
    } finally {
      setBusy(false)
    }
  }

  async function markRead(notification) {
    try {
      const updated = await markNotificationRead(notification.id)
      setNotifications((current) => current.map((item) => item.id === updated.id ? updated : item))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Notification could not be marked as read.')
    }
  }

  async function openConversation(id) {
    setSelectedConversation(id)
    setTab('messages')
  }

  async function createConversation(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      const created = await startConversation(recipientId.trim())
      setRecipientId('')
      const refreshed = await getMyConversations()
      setConversations(Array.isArray(refreshed) ? refreshed : [])
      setSelectedConversation(created.id)
      setTab('messages')
      setMessage('Conversation opened.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not start this conversation.')
    } finally {
      setBusy(false)
    }
  }

  async function sendMessage(event) {
    event.preventDefault()
    if (!draft.trim() || !selectedConversation) return
    setBusy(true)
    setError('')
    try {
      const created = await sendConversationMessage(selectedConversation, draft.trim())
      setMessages((current) => [...current, created])
      setDraft('')
      const refreshed = await getMyConversations()
      setConversations(Array.isArray(refreshed) ? refreshed : [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Message could not be sent.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <SiteNav />
      <main className="cw-page">
        <header className="cw-hero">
          <span className="cw-kicker">YOUR ACCOUNT</span>
          <h1>Account & inbox</h1>
          <p>Update your contact details, read CareLife notifications, and message people you have a reason to coordinate with.</p>
          <div className="cw-hero-meta">{profile?.email && <span>{profile.email}</span>}{profile?.role && <span>{profile.role.replaceAll('_', ' ')}</span>}</div>
        </header>
        <nav className="cw-tabs" aria-label="Account sections">
          {[['profile', 'Profile'], ['notifications', 'Notifications'], ['messages', 'Messages']].map(([id, label]) => <button key={id} type="button" className={tab === id ? 'active' : ''} aria-pressed={tab === id} onClick={() => setTab(id)}>{label}{id === 'notifications' && notifications.some((n) => !n.is_read) ? <i>{notifications.filter((n) => !n.is_read).length}</i> : null}</button>)}
        </nav>
        {error && <div className="cw-alert error" role="alert">{error}</div>}
        {message && <div className="cw-alert success" role="status">{message}</div>}
        {loading ? <div className="cw-state">Loading your account…</div> : <>
          {tab === 'profile' && <section className="cw-panel">
            <div className="cw-panel-heading"><div><p className="cw-kicker">PERSONAL DETAILS</p><h2>Your profile</h2></div><span className="cw-status">{profile?.role || 'Member'}</span></div>
            <form className="cw-form" onSubmit={saveProfile}>
              <label>Email address<input type="email" value={profile?.email || ''} disabled /></label>
              <label>Full name<input value={profileForm.full_name} maxLength={200} onChange={(event) => setProfileForm((s) => ({ ...s, full_name: event.target.value }))} required /></label>
              <label>Phone number<input type="tel" value={profileForm.phone} maxLength={30} placeholder="+8801XXXXXXXXX" onChange={(event) => setProfileForm((s) => ({ ...s, phone: event.target.value }))} /></label>
              <div className="cw-form-actions"><button className="cw-button primary" disabled={busy}>{busy ? 'Saving…' : 'Save profile'}</button></div>
            </form>
          </section>}
          {tab === 'notifications' && <section className="cw-panel">
            <div className="cw-panel-heading"><div><p className="cw-kicker">UPDATES FOR YOU</p><h2>Notifications</h2></div><button type="button" className="cw-button" onClick={() => void loadInbox()}>Refresh</button></div>
            {!notifications.length ? <div className="cw-empty"><strong>No notifications yet</strong><p>CareLife will show account, booking and review updates here when they are sent to your account.</p></div> :
              <div className="cw-record-list">{notifications.map((item) => <article className={'cw-record ' + (item.is_read ? '' : 'unread')} key={item.id}>
                <div className="cw-record-main"><div className="cw-record-title-row"><h3>{item.title}</h3><span className={'cw-pill ' + (item.is_read ? 'neutral' : 'mint')}>{item.is_read ? 'Read' : 'New'}</span></div><p>{item.message}</p><small>{prettyDate(item.created_at)} · {item.notification_type.replaceAll('_', ' ')}</small></div>
                {!item.is_read && <button type="button" className="cw-button" onClick={() => void markRead(item)}>Mark read</button>}
              </article>)}</div>}
          </section>}
          {tab === 'messages' && <section className="cw-panel">
            <div className="cw-panel-heading"><div><p className="cw-kicker">PRIVATE CONVERSATIONS</p><h2>Messages</h2></div></div>
            <form className="cw-inline-form" onSubmit={createConversation}><label>Start a conversation with a CareLife user ID<input value={recipientId} onChange={(event) => setRecipientId(event.target.value)} placeholder="Paste the user ID shared with you" required /></label><button className="cw-button primary" disabled={busy}>Start chat</button></form>
            <div className="cw-messaging-layout">
              <aside className="cw-conversation-list" aria-label="Your conversations">
                {!conversations.length ? <p className="cw-muted">No conversations yet.</p> : conversations.map((conversation) => <button type="button" key={conversation.id} className={selectedConversation === conversation.id ? 'selected' : ''} onClick={() => void openConversation(conversation.id)}><strong>Conversation</strong><small>{conversation.id}</small><small>{conversation.last_message_at ? prettyDate(conversation.last_message_at) : 'No messages yet'}</small></button>)}
              </aside>
              <div className="cw-chat">
                {!selectedConversation ? <div className="cw-empty"><strong>Select a conversation</strong><p>Choose a conversation or start one with a user ID.</p></div> : <>
                  <div className="cw-chat-heading"><strong>Conversation</strong><small>{selectedConversation}</small></div>
                  <div className="cw-message-list">{messages.map((item) => <article key={item.id} className="cw-message"><p>{item.body}</p><small>{prettyDate(item.created_at)}</small></article>)}</div>
                  <form className="cw-send-form" onSubmit={sendMessage}><label className="visually-hidden" htmlFor="cw-message-body">Message</label><textarea id="cw-message-body" rows={2} maxLength={5000} value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Write a message…" required /><button className="cw-button primary" disabled={busy || !draft.trim()}>{busy ? 'Sending…' : 'Send'}</button></form>
                </>}
              </div>
            </div>
          </section>}
        </>}
      </main>
    </>
  )
}
