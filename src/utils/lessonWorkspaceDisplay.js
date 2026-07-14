import { formatLastSeen } from './sessionDisplay.js'

const STATUS_META = {
  processed: { label: 'جاهز', tone: 'ready' },
  draft: { label: 'مسودة', tone: 'draft' },
  processing: { label: 'جاري المعالجة', tone: 'processing' },
  error: { label: 'يوجد خطأ', tone: 'error' },
}

const TYPE_META = {
  video: { label: 'فيديو', icon: 'mdi-play-circle-outline' },
  pdf: { label: 'PDF', icon: 'mdi-file-pdf-box' },
  homework: { label: 'واجب', icon: 'mdi-clipboard-text-outline' },
  ai: { label: 'AI', icon: 'mdi-brain' },
  composite: { label: 'متكامل', icon: 'mdi-layers-outline' },
  audio: { label: 'صوت', icon: 'mdi-headphones' },
}

export function lessonStatusMeta(status) {
  return STATUS_META[status] || { label: status || '—', tone: 'draft' }
}

export function lessonTypeMeta(contentType, fallbackLabel = '') {
  const key = String(contentType || '').toLowerCase()
  const meta = TYPE_META[key]
  if (meta) return meta
  return {
    label: fallbackLabel || key || 'درس',
    icon: 'mdi-book-open-page-variant-outline',
  }
}

export function formatLessonRelativeDate(iso) {
  if (!iso) return null
  return formatLastSeen(iso)
}

export function formatLessonMetaDate(iso) {
  if (!iso) return null
  try {
    const date = new Date(iso)
    if (Number.isNaN(date.getTime())) return null
    return date.toLocaleDateString('ar-SY', { day: 'numeric', month: 'long' })
  } catch {
    return null
  }
}

export function canReprocessLesson(lesson) {
  return ['error', 'draft', 'processing'].includes(lesson?.status)
    && (lesson?.content_type === 'pdf' || lesson?.content_type === 'ai')
}

/** Derive completed count from API percent + known active subscriber total. */
export function lessonCompletionFromPercent(percent, totalStudents) {
  const total = Math.max(0, Number(totalStudents) || 0)
  const pct = Math.min(100, Math.max(0, Number(percent) || 0))
  if (!total) return { total: 0, completed: 0, percent: pct }
  const completed = Math.round((pct / 100) * total)
  return { total, completed, percent: pct }
}
