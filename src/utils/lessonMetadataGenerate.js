/**
 * Client-side lesson metadata suggestions from video source.
 * Uses public link previews (YouTube/Vimeo/etc.) — refined by Gemini after upload/processing.
 */

import { detectVideoPlatform } from './videoEmbed.js'

function cleanFilename(name) {
  const base = String(name || '')
    .replace(/\.[^.]+$/, '')
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
  return base || ''
}

function youtubeTitleFallback(url) {
  try {
    const parsed = new URL(url)
    if (!parsed.hostname.includes('youtube.com') && !parsed.hostname.includes('youtu.be')) {
      return ''
    }
    const path = parsed.pathname.replace(/^\//, '')
    if (path.startsWith('watch') && parsed.searchParams.get('v')) {
      return 'درس فيديو من YouTube'
    }
    if (parsed.hostname.includes('youtu.be') && path) {
      return 'درس فيديو من YouTube'
    }
  } catch {
    return ''
  }
  return ''
}

export async function fetchVideoLinkPreview(url) {
  const trimmed = String(url || '').trim()
  if (!trimmed) throw new Error('أدخل رابط الفيديو أولاً')

  const response = await fetch(
    `https://noembed.com/embed?url=${encodeURIComponent(trimmed)}`,
    { headers: { Accept: 'application/json' } },
  )
  if (!response.ok) {
    const fallback = youtubeTitleFallback(trimmed) || cleanFilename(trimmed.split('/').pop())
    if (fallback) {
      const platform = detectVideoPlatform(trimmed)
      return {
        title: fallback,
        provider: platform.label,
        thumbnail: '',
        duration: 0,
        platform: platform.label,
        platformIcon: platform.icon,
      }
    }
    throw new Error('تعذر قراءة الرابط — تحقق من صحته')
  }

  const data = await response.json()
  if (data.error) {
    const fallback = youtubeTitleFallback(trimmed)
    if (fallback) {
      const platform = detectVideoPlatform(trimmed)
      return {
        title: fallback,
        provider: platform.label,
        thumbnail: '',
        duration: 0,
        platform: platform.label,
        platformIcon: platform.icon,
      }
    }
    throw new Error(data.error)
  }

  const platform = detectVideoPlatform(trimmed)

  return {
    title: String(data.title || '').trim(),
    author: data.author_name || '',
    provider: data.provider_name || platform.label,
    thumbnail: String(data.thumbnail_url || '').trim(),
    duration: Number(data.duration) > 0 ? Number(data.duration) : 0,
    platform: platform.label,
    platformIcon: platform.icon,
  }
}

export function suggestTitleFromFile(file) {
  if (!file?.name) return ''
  const cleaned = cleanFilename(file.name)
  if (!cleaned) return 'درس جديد'
  return cleaned.charAt(0).toUpperCase() + cleaned.slice(1)
}

export function suggestDescriptionFromTitle(title) {
  const t = String(title || '').trim()
  if (!t) return ''
  return `درس يشرح «${t}» — مع ملخص ذكي وأسئلة تفاعلية بعد المعالجة التلقائية.`
}

export async function generateLessonMetadata({ videoFile, videoUrl, pdfFile, target = 'both' }) {
  let title = ''
  let description = ''

  if (videoUrl?.trim()) {
    const preview = await fetchVideoLinkPreview(videoUrl)
    title = preview.title || youtubeTitleFallback(videoUrl) || ''
  } else if (videoFile) {
    title = suggestTitleFromFile(videoFile)
  } else if (pdfFile) {
    title = suggestTitleFromFile(pdfFile)
  }

  if (!title) {
    throw new Error('ارفع فيديو أو ألصق رابطاً لتوليد العنوان')
  }

  description = suggestDescriptionFromTitle(title)

  if (target === 'title') return { title, description: '' }
  if (target === 'description') return { title: '', description }
  return { title, description }
}
