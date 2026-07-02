/** Pick a locale-specific API field (e.g. label_ar / label_en) with sensible fallbacks. */
export function pickLocalizedField(item, base = 'label', locale = 'ar') {
  if (!item) return ''
  const loc = locale === 'ar' ? 'ar' : 'en'
  const primary = item[`${base}_${loc}`]
  if (primary) return primary
  const fallback = item[`${base}_ar`] ?? item[base]
  return fallback ?? ''
}

export function translateEnum(t, te, keyPrefix, value, apiFallback = '') {
  if (!value) return apiFallback
  const key = `${keyPrefix}.${value}`
  return te(key) ? t(key) : (apiFallback || String(value))
}

export function dateLocaleTag(locale) {
  return locale === 'ar' ? 'ar-SY' : 'en-US'
}
