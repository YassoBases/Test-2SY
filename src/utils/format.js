export function formatFileSize(bytes) {
  if (!bytes && bytes !== 0) return '—'
  if (bytes < 1024) return `${bytes} بايت`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} ك.ب`
  return `${(bytes / (1024 * 1024)).toFixed(1)} م.ب`
}

export function estimatePdfPages(file) {
  if (!file) return 1
  return Math.max(1, Math.round(file.size / 50000))
}

export function formatTimeArabic(date = new Date()) {
  return date.toLocaleTimeString('ar-SY', { hour: '2-digit', minute: '2-digit' })
}

/** Format amount in Syrian Pounds (ل.س). */
export function formatSyrianPrice(amount) {
  const n = Number(amount) || 0
  return `${new Intl.NumberFormat('ar-SY').format(n)} ل.س`
}

/** Build display line: مادة — معلم — سعر */
export function formatCourseLine(item) {
  const subject = item.subject_name || item.title
  const teacher = item.teacher_name || ''
  const price = formatSyrianPrice(item.price)
  return `${subject} — ${teacher} — ${price}`
}
