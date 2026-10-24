import { useEffect, useState } from 'react'
import { API_BASE_URL } from '../api/client'
import { getToken, useSession } from '../lib/session'

export default function useMyProfilePhoto() {
  const { signedIn, email } = useSession()
  const [photoUrl, setPhotoUrl] = useState('')

  useEffect(() => {
    if (!signedIn) {
      return undefined
    }

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
    }).catch(() => {
      if (!cancelled) setPhotoUrl('')
    })

    return () => {
      cancelled = true
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [signedIn, email])

  return photoUrl
}
