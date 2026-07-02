const DEVICE_TYPE_LABELS = {
  desktop: 'حاسوب',
  mobile: 'جوال',
  tablet: 'جهاز لوحي',
}

export function normalizeAuthSession(row) {
  if (!row) return null
  return {
    id: row.id,
    deviceName: row.device_name ?? row.deviceName ?? null,
    deviceType: row.device_type ?? row.deviceType ?? null,
    userAgent: row.user_agent ?? row.userAgent ?? null,
    ipAddress: row.ip_address ?? row.ipAddress ?? null,
    lastSeenAt: row.last_seen_at ?? row.lastSeenAt ?? null,
    createdAt: row.created_at ?? row.createdAt ?? null,
    isCurrent: Boolean(row.is_current ?? row.isCurrent),
  }
}

export function deviceTypeLabel(deviceType) {
  if (!deviceType) return 'جهاز'
  return DEVICE_TYPE_LABELS[deviceType] || deviceType
}

export function deviceTypeIcon(deviceType) {
  if (deviceType === 'mobile') return 'mdi-cellphone'
  if (deviceType === 'tablet') return 'mdi-tablet'
  return 'mdi-monitor'
}

/** Short browser label from stored device_name or user-agent string. */
export function browserLabel(session) {
  if (session?.deviceName) return session.deviceName
  const ua = session?.userAgent
  if (!ua) return 'متصفح غير معروف'
  return summarizeUserAgent(ua)
}

export function summarizeUserAgent(ua) {
  if (!ua) return '—'
  const lower = ua.toLowerCase()
  let browser = 'متصفح'
  if (lower.includes('edg/')) browser = 'Edge'
  else if (lower.includes('chrome/')) browser = 'Chrome'
  else if (lower.includes('firefox/')) browser = 'Firefox'
  else if (lower.includes('safari/') && !lower.includes('chrome')) browser = 'Safari'

  let os = ''
  if (lower.includes('windows')) os = 'Windows'
  else if (lower.includes('android')) os = 'Android'
  else if (lower.includes('iphone') || lower.includes('ipad')) os = 'iOS'
  else if (lower.includes('mac os')) os = 'macOS'
  else if (lower.includes('linux')) os = 'Linux'

  return os ? `${browser} · ${os}` : browser
}

export function formatUserAgentDetail(ua) {
  if (!ua) return '—'
  if (ua.length <= 120) return ua
  return `${ua.slice(0, 117)}…`
}

export function formatLastSeen(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '—'

  const now = Date.now()
  const diffMs = now - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)

  if (diffMin < 1) return 'الآن'
  if (diffMin < 60) return `منذ ${diffMin} د`
  const diffHours = Math.floor(diffMin / 60)
  if (diffHours < 24) return `منذ ${diffHours} س`
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `منذ ${diffDays} ي`

  return date.toLocaleString('ar-SY', {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}
