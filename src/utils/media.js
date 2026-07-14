import { getApiBaseUrl } from '../api/client.js'

/** Absolute URL for uploaded media (images, voice, PDF). */
export function mediaUrl(path) {
  if (!path) return ''
  const trimmed = String(path).trim()
  if (!trimmed) return ''
  if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) return trimmed

  const normalized = trimmed.startsWith('/') ? trimmed : `/${trimmed}`
  const apiBase = getApiBaseUrl().replace(/\/$/, '')

  // Dev: Vite proxies /uploads → backend; same-origin relative path is most reliable.
  if (typeof window !== 'undefined' && !apiBase.startsWith('http')) {
    return normalized
  }

  if (apiBase.startsWith('http')) {
    const origin = apiBase.replace(/\/api\/?$/, '')
    return `${origin}${normalized}`
  }

  if (typeof window !== 'undefined') {
    return `${window.location.origin}${normalized}`
  }

  return normalized
}
