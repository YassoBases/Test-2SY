/** Detect platform and build embed URLs for external lesson videos. */

export function parseYouTubeId(url) {
  try {
    const parsed = new URL(url)
    const host = parsed.hostname.replace(/^www\./, '')
    if (host === 'youtu.be') {
      const id = parsed.pathname.replace(/^\//, '').split('/')[0]
      return id || null
    }
    if (host.includes('youtube.com')) {
      if (parsed.pathname.startsWith('/embed/')) {
        return parsed.pathname.split('/')[2] || null
      }
      if (parsed.pathname.startsWith('/shorts/')) {
        return parsed.pathname.split('/')[2] || null
      }
      return parsed.searchParams.get('v') || null
    }
  } catch {
    return null
  }
  return null
}

export function parseVimeoId(url) {
  try {
    const parsed = new URL(url)
    const host = parsed.hostname.replace(/^www\./, '')
    if (!host.includes('vimeo.com')) return null
    const parts = parsed.pathname.split('/').filter(Boolean)
    const id = parts.find((p) => /^\d+$/.test(p))
    return id || null
  } catch {
    return null
  }
  return null
}

export function parseGoogleDriveId(url) {
  try {
    const parsed = new URL(url)
    const host = parsed.hostname.replace(/^www\./, '')
    if (!host.includes('drive.google.com')) return null
    const match = parsed.pathname.match(/\/file\/d\/([^/]+)/)
    return match?.[1] || null
  } catch {
    return null
  }
  return null
}

export function isDirectVideoUrl(url) {
  try {
    const parsed = new URL(url)
    const path = parsed.pathname.toLowerCase()
    return /\.(mp4|webm|mov|m4v|ogv)(\?|$)/i.test(path)
  } catch {
    return false
  }
}

export function detectVideoPlatform(url) {
  const trimmed = String(url || '').trim()
  if (!trimmed) return { id: 'unknown', label: '', icon: 'mdi-link-variant' }
  if (parseYouTubeId(trimmed)) {
    return { id: 'youtube', label: 'YouTube', icon: 'mdi-youtube' }
  }
  if (parseVimeoId(trimmed)) {
    return { id: 'vimeo', label: 'Vimeo', icon: 'mdi-vimeo' }
  }
  if (parseGoogleDriveId(trimmed)) {
    return { id: 'drive', label: 'Google Drive', icon: 'mdi-google-drive' }
  }
  if (isDirectVideoUrl(trimmed)) {
    return { id: 'mp4', label: 'MP4 مباشر', icon: 'mdi-file-video-outline' }
  }
  return { id: 'link', label: 'رابط فيديو', icon: 'mdi-link-variant' }
}

/**
 * @returns {{ type: string, embedUrl: string, platform: string, icon: string } | null}
 */
export function resolveVideoEmbed(url) {
  const trimmed = String(url || '').trim()
  if (!trimmed) return null

  const ytId = parseYouTubeId(trimmed)
  if (ytId) {
    return {
      type: 'youtube',
      embedUrl: `https://www.youtube.com/embed/${ytId}?rel=0&modestbranding=1`,
      platform: 'YouTube',
      icon: 'mdi-youtube',
    }
  }

  const vimeoId = parseVimeoId(trimmed)
  if (vimeoId) {
    return {
      type: 'vimeo',
      embedUrl: `https://player.vimeo.com/video/${vimeoId}`,
      platform: 'Vimeo',
      icon: 'mdi-vimeo',
    }
  }

  const driveId = parseGoogleDriveId(trimmed)
  if (driveId) {
    return {
      type: 'drive',
      embedUrl: `https://drive.google.com/file/d/${driveId}/preview`,
      platform: 'Google Drive',
      icon: 'mdi-google-drive',
    }
  }

  return null
}

export function formatMediaDuration(seconds) {
  const total = Math.max(0, Math.floor(Number(seconds) || 0))
  if (!total) return ''
  const h = Math.floor(total / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = total % 60
  const mm = String(m).padStart(2, '0')
  const ss = String(s).padStart(2, '0')
  if (h > 0) return `${String(h).padStart(2, '0')}:${mm}:${ss}`
  return `${mm}:${ss}`
}
