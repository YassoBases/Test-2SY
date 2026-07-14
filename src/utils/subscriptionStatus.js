export const SUBSCRIPTION_STATUS_LABELS = {
  pending: 'غير مشترك',
  active: 'نشط',
  expiring_soon: 'ينتهي قريباً',
  expired: 'منتهٍ',
}

export function subscriptionStatusLabel(status) {
  return SUBSCRIPTION_STATUS_LABELS[status] || status || '—'
}

export function subscriptionStatusColor(status) {
  if (status === 'active') return 'success'
  if (status === 'expiring_soon') return 'warning'
  if (status === 'expired') return 'error'
  return 'default'
}

export function formatSubscriptionDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleDateString('ar-SY', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return '—'
  }
}

export function relationshipLabelAr(label) {
  const map = {
    parent: 'ولي أمر',
    father: 'أب',
    mother: 'أم',
    guardian: 'وصي',
  }
  return map[label] || label || 'ولي أمر'
}
