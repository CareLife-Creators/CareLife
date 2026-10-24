import { useCallback, useEffect, useRef, useState } from 'react'
import SiteNav from '../components/SiteNav'
import {
  getMyProfile, updateMyProfile, getMyNotifications, markNotificationRead,
  getMyConversations, startConversation, getConversationMessages, sendConversationMessage,
  uploadMyProfilePhoto, removeMyProfilePhoto,
} from '../api/workspace'
import { API_BASE_URL } from '../api/client'
import { getToken } from '../lib/session'
import { getCaregiverDirectory } from '../api/discovery'
import './Workspace.css'

const prettyDate = (value) => {
  const date = new Date(value)
  return value && !Number.isNaN(date.getTime()) ? date.toLocaleString() : 'Time not provided'
}

export default function AccountPage({ initialTab = 'profile' }) {
  const [tab, setTab] = useState(() => {
    try {
      const requested = window.sessionStorage.getItem('carelife_account_tab')
      if (requested) { window.sessionStorage.removeItem('carelife_account_tab'); return requested }
    } catch { /* Use the route's default section when storage is unavailable. */ }
    return initialTab
  })
  const [profile, setProfile] = useState(null)
  const [profileForm, setProfileForm] = useState({ full_name: '', phone: '' })
  const [notifications, setNotifications] = useState([])
  const [conversations, setConversations] = useState([])
  const [selectedConversation, setSelectedConversation] = useState('')
  const [messages, setMessages] = useState([])
  const [contacts, setContacts] = useState([])
  const [contactSearch, setContactSearch] = useState('')
  const [contactSearchOpen, setContactSearchOpen] = useState(false)
  const [contactsLoaded, setContactsLoaded] = useState(false)
  const [contactsLoading, setContactsLoading] = useState(false)
  const [draft, setDraft] = useState('')
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [photoUrl, setPhotoUrl] = useState('')
  const [photoBusy, setPhotoBusy] = useState(false)
  const photoInput = useRef(null)
  const initialTabRef = useRef(initialTab)

  useEffect(() => {
    if (initialTabRef.current !== initialTab) {
      initialTabRef.current = initialTab
      setTab(initialTab)
    }
  }, [initialTab])

  useEffect(() => {
    if (!profile?.user_id) return undefined
    let cancelled = false
    let objectUrl = ''
    fetch(API_BASE_URL + '/users/me/profile/photo', {
      headers: getToken() ? { Authorization: 'Bearer ' + getToken() } : {},
      credentials: 'include',
    }).then((response) => {
      if (!response.ok) throw new Error('No profile photo')
      return response.blob()
    }).then((blob) => {
      if (cancelled) return
      objectUrl = URL.createObjectURL(blob)
      setPhotoUrl(objectUrl)
    }).catch(() => { if (!cancelled) setPhotoUrl('') })
    return () => { cancelled = true; if (objectUrl) URL.revokeObjectURL(objectUrl) }
  }, [profile?.user_id, profile?.profile_photo_url, photoBusy])

  async function uploadPhoto(event) {
    const file = event.target.files?.[0]
    if (!file) return
    if (file.size > 5 * 1024 * 1024) {
      setError('Choose a profile photo under 5 MB.')
      event.target.value = ''
      return
    }
    setPhotoBusy(true)
    setError('')
    setMessage('')
    try {
      await uploadMyProfilePhoto(file)
      window.dispatchEvent(new Event('carelife:profile-photo-updated'))
      setMessage('Profile photo updated.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Profile photo could not be uploaded.')
    } finally {
      setPhotoBusy(false)
      event.target.value = ''
    }
  }

  async function removePhoto() {
    setPhotoBusy(true)
    setError('')
    setMessage('')
    try {
      await removeMyProfilePhoto()
      setPhotoUrl('')
      window.dispatchEvent(new Event('carelife:profile-photo-updated'))
      setMessage('Profile photo removed.')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Profile photo could not be removed.')
    } finally {
      setPhotoBusy(false)
    }
  }

  const initials = (profile?.full_name || profile?.email || 'CL').trim().split(/[\s@._-]+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join('').toUpperCase()
  const activeConversation = conversations.find((item) => item.id === selectedConversation)
  const conversationInitials = (activeConversation?.other_user_name || 'CareLife member').trim().split(/[\s@._-]+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join('').toUpperCase()
  const matchingContacts = contacts.filter((contact) => {
    const query = contactSearch.trim().toLowerCase()
    return !query || [contact.full_name, contact.service_type, contact.location].some((value) => String(value || '').toLowerCase().includes(query))
  }).slice(0, 5)

  const loadInbox = useCallback(async () => {
    const [notificationResult, conversationResult] = await Promise.allSettled([getMyNotifications(), getMyConversations()])
    if (notificationResult.status === 'fulfilled') setNotifications(Array.isArray(notificationResult.value) ? notificationResult.value : [])
    if (conversationResult.status === 'fulfilled') {
      const list = Array.isArray(conversationResult.value) ? conversationResult.value : []
      setConversations(list)
      setSelectedConversation((current) => current || list[0]?.id || '')
    }
    if (notificationResult.status === 'rejected' && conversationResult.status === 'rejected') {
      setError('Inbox data could not be loaded. Check your session and try again.')
    }
  }, [])

  async function toggleContactSearch() {
    if (contactSearchOpen) {
      setContactSearchOpen(false)
      return
    }
    setContactSearchOpen(true)
    if (contactsLoaded || contactsLoading) return
    setContactsLoading(true)
    setError('')
    try {
      const directory = await getCaregiverDirectory()
      setContacts(Array.isArray(directory) ? directory : [])
      setContactsLoaded(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Care professionals could not be loaded.')
    } finally {
      setContactsLoading(false)
    }
  }

  const loadPage = useCallback(async () => {
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
  }, [loadInbox])

  // eslint-disable-next-line react-hooks/set-state-in-effect -- The initial request loads the profile and inbox into local UI state.
  useEffect(() => { void loadPage() }, [loadPage])

  useEffect(() => {
    if (!selectedConversation) return
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
      window.dispatchEvent(new Event('carelife:notifications-updated'))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Notification could not be marked as read.')
    }
  }

  async function openConversation(id) {
    setSelectedConversation(id)
    setTab('messages')
  }

  async function createConversation(contact) {
    setBusy(true)
    setError('')
    try {
      const created = await startConversation(contact.caregiver_id)
      const refreshed = await getMyConversations()
      setConversations(Array.isArray(refreshed) ? refreshed : [])
      setSelectedConversation(created.id)
      setTab('messages')
      setMessage('Conversation opened with ' + (contact.full_name || 'this caregiver') + '.')
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
        <header className={'cw-hero cw-account-hero ' + (tab === 'messages' ? 'messages' : '')}>
          <span className="cw-kicker">{tab === 'messages' ? 'YOUR CARELIFE INBOX' : tab === 'notifications' ? 'UPDATES FOR YOU' : 'YOUR ACCOUNT'}</span>
          <h1>{tab === 'messages' ? 'Messages' : tab === 'notifications' ? 'Notifications' : 'Your profile'}</h1>
          <p>{tab === 'messages' ? 'Keep conversations with care professionals together, right where you need them.' : tab === 'notifications' ? 'See updates about your care requests and account.' : 'Keep your contact details and profile photo up to date.'}</p>
          {tab === 'profile' && <div className="cw-hero-meta">{profile?.email && <span>{profile.email}</span>}{profile?.role && <span>{profile.role.replaceAll('_', ' ')}</span>}</div>}
        </header>
        <nav className="cw-tabs cw-account-links" aria-label="Account sections">
          <a className={tab === 'profile' ? 'active' : ''} aria-current={tab === 'profile' ? 'page' : undefined} href="#account">Profile</a>
          <a className={tab === 'notifications' ? 'active' : ''} aria-current={tab === 'notifications' ? 'page' : undefined} href="#notifications">Notifications</a>
          <a className={tab === 'messages' ? 'active' : ''} aria-current={tab === 'messages' ? 'page' : undefined} href="#messages">Messages</a>
        </nav>
        {error && <div className="cw-alert error" role="alert">{error}</div>}
        {message && <div className="cw-alert success" role="status">{message}</div>}
        {loading ? <div className="cw-state">Loading your account…</div> : <>
          {tab === 'profile' && <>
          <section className="cw-profile-card">
            <div className="cw-profile-person">
              <div className="cw-profile-avatar" aria-label={profile?.full_name ? profile.full_name + ' profile photo' : 'Profile photo'}>
                {photoUrl ? <span className="cw-profile-photo-crop"><img src={photoUrl} alt="Your profile" /></span> : <span>{initials}</span>}
              </div>
              <div className="cw-profile-summary"><p className="cw-kicker">YOUR CARELIFE PROFILE</p><h2>{profile?.full_name || 'Add your name'}</h2><p className="cw-profile-email">{profile?.email}</p><div className="cw-profile-badges"><span>{String(profile?.role || 'Member').replaceAll('_', ' ')}</span><span>CareLife member</span></div><div className="cw-profile-photo-actions"><button type="button" className="cw-profile-change" onClick={() => photoInput.current?.click()} disabled={photoBusy}>{photoBusy ? 'Saving photo…' : photoUrl ? 'Change photo' : 'Add a photo'}</button>{photoUrl && <button type="button" className="cw-profile-remove" disabled={photoBusy} onClick={removePhoto}>Remove</button>}</div></div>
            </div>
            <input ref={photoInput} className="cw-profile-file-input" type="file" accept="image/jpeg,image/png,image/webp" onChange={uploadPhoto} aria-label="Choose a profile photo" />
          </section>
          <section className="cw-panel" id="personal-details">
            <div className="cw-panel-heading"><div><p className="cw-kicker">PERSONAL DETAILS</p><h2>Your profile</h2></div><span className="cw-status cw-profile-role-status">{String(profile?.role || 'Member').replaceAll('_', ' ')}</span></div>
            <form className="cw-form" onSubmit={saveProfile}>
              <label>Email address<input type="email" value={profile?.email || ''} disabled /></label>
              <label>Full name<input value={profileForm.full_name} maxLength={200} onChange={(event) => setProfileForm((s) => ({ ...s, full_name: event.target.value }))} required /></label>
              <label>Phone number<input type="tel" value={profileForm.phone} maxLength={30} placeholder="+8801XXXXXXXXX" onChange={(event) => setProfileForm((s) => ({ ...s, phone: event.target.value }))} /></label>
              <div className="cw-form-actions"><button className="cw-button primary" disabled={busy}>{busy ? 'Saving…' : 'Save profile'}</button></div>
            </form>
          </section></>}
          {tab === 'notifications' && <section className="cw-panel">
            <div className="cw-panel-heading"><div><p className="cw-kicker">UPDATES FOR YOU</p><h2>Notifications</h2></div><button type="button" className="cw-button" onClick={() => void loadInbox()}>Refresh</button></div>
            {!notifications.length ? <div className="cw-empty"><strong>No notifications yet</strong><p>CareLife will show account, booking and review updates here when they are sent to your account.</p></div> :
              <div className="cw-record-list">{notifications.map((item) => <article className={'cw-record ' + (item.is_read ? '' : 'unread')} key={item.id}>
                <div className="cw-record-main"><div className="cw-record-title-row"><h3>{item.title}</h3><span className={'cw-pill ' + (item.is_read ? 'neutral' : 'mint')}>{item.is_read ? 'Read' : 'New'}</span></div><p>{item.message}</p><small>{prettyDate(item.created_at)} · {item.notification_type.replaceAll('_', ' ')}</small></div>
                {!item.is_read && <button type="button" className="cw-button" onClick={() => void markRead(item)}>Mark read</button>}
              </article>)}</div>}
          </section>}
          {tab === 'messages' && <section className="cw-panel cw-messages-panel">
            <div className="cw-panel-heading"><div><p className="cw-kicker">PRIVATE CARE CONVERSATIONS</p><h2>Your inbox</h2><p className="cw-panel-subtitle">{profile?.role === 'independent_caregiver' ? 'Reply to families here, or find another care professional to coordinate with.' : 'Find a care professional to begin. Replies and care updates stay in this inbox.'}</p></div><button type="button" className="cw-button primary" onClick={() => void toggleContactSearch()}>{contactSearchOpen ? 'Close directory' : 'Find a care professional'}</button></div>
            {contactSearchOpen && <div className="cw-contact-finder"><div className="cw-contact-finder-heading"><strong>Choose a care professional</strong><p>Search by name, service, or location. Select Message to open a private conversation.</p></div><label>Search the caregiver directory<input type="search" value={contactSearch} onChange={(event) => setContactSearch(event.target.value)} placeholder="Name, service, or location" /></label>
              {contactsLoading ? <p className="cw-contact-empty" role="status">Loading care professionals…</p> : <div className="cw-contact-results">{matchingContacts.map((contact) => <article className="cw-contact-result" key={contact.caregiver_id}><span className="cw-contact-avatar">{(contact.full_name || 'C').trim().charAt(0).toUpperCase()}</span><span className="cw-contact-info"><strong>{contact.full_name || 'CareLife caregiver'}</strong><small>{String(contact.service_type || 'Care service').replaceAll('_', ' ')} · {contact.location || 'Location not listed'}</small></span><button type="button" className="cw-button soft" disabled={busy} onClick={() => void createConversation(contact)}>{busy ? 'Opening…' : 'Message'}</button></article>)}
                {!matchingContacts.length && <div className="cw-contact-empty">{contacts.length ? 'No care professionals match that search.' : <>No approved care professionals are listed yet. Check again in the <a href="#caregivers">caregiver directory</a>.</>}</div>}</div>}
            </div>}
            <div className="cw-messaging-layout">
              <aside className="cw-conversation-list" aria-label="Your conversations">
                <div className="cw-list-heading-row"><strong className="cw-list-heading">Conversations</strong><span>{conversations.length}</span></div>
                {!conversations.length ? <div className="cw-conversation-empty"><span className="cw-empty-message-icon" aria-hidden="true">✉</span><strong>No conversations yet</strong><p>When you start or receive a message, it will appear here.</p><button type="button" className="cw-button soft" onClick={() => void toggleContactSearch()}>Find a care professional</button></div> : conversations.map((conversation) => {
                  const otherName = conversation.other_user_name || 'CareLife member'
                  const otherInitials = otherName.trim().split(/[\s@._-]+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join('').toUpperCase()
                  return <button type="button" key={conversation.id} className={selectedConversation === conversation.id ? 'selected' : ''} aria-current={selectedConversation === conversation.id ? 'true' : undefined} onClick={() => void openConversation(conversation.id)}>
                    <span className="cw-conversation-avatar" aria-hidden="true">{otherInitials}</span><span className="cw-conversation-copy"><strong>{otherName}</strong><small>{String(conversation.other_user_role || 'CareLife member').replaceAll('_', ' ')}</small><small>{conversation.last_message_at ? prettyDate(conversation.last_message_at) : 'Conversation started'}</small></span>
                  </button>
                })}
              </aside>
              <div className="cw-chat">
                {!selectedConversation ? <div className="cw-chat-welcome"><span className="cw-chat-welcome-icon" aria-hidden="true">✉</span><strong>{conversations.length ? 'Select a conversation' : 'Start a care conversation'}</strong><p>{conversations.length ? 'Choose a person in your conversation list to read messages and reply.' : 'Find a care professional, open a conversation, then send your first message. Their reply will appear here.'}</p>{!conversations.length && <button type="button" className="cw-button primary" onClick={() => void toggleContactSearch()}>Browse care professionals</button>}</div> : <>
                  <div className="cw-chat-heading"><span className="cw-chat-partner-avatar" aria-hidden="true">{conversationInitials}</span><span className="cw-chat-partner-copy"><strong>{activeConversation?.other_user_name || 'CareLife member'}</strong><small>{String(activeConversation?.other_user_role || 'Private conversation').replaceAll('_', ' ')}</small></span><span className="cw-private-label">Private conversation</span></div>
                  <div className="cw-message-list">{messages.map((item) => {
                    const isMine = item.sender_user_id === profile?.user_id
                    return <article key={item.id} className={'cw-message ' + (isMine ? 'mine' : '')}>
                      <span className="cw-message-avatar" aria-hidden="true">{isMine && photoUrl ? <img src={photoUrl} alt="" /> : isMine ? initials : conversationInitials}</span>
                      <div className="cw-message-content"><p>{item.body}</p><small>{isMine ? 'You' : activeConversation?.other_user_name || 'CareLife member'} · {prettyDate(item.created_at)}</small></div>
                    </article>
                  })}</div>
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
