/** Password strength for UI indicator (Weak / Medium / Strong). */

export function scorePassword(password) {
  const value = String(password || '')
  if (!value) return { score: 0, labelKey: '', color: 'grey' }

  let score = 0
  if (value.length >= 6) score += 1
  if (value.length >= 10) score += 1
  if (/[a-z]/.test(value) && /[A-Z]/.test(value)) score += 1
  if (/\d/.test(value)) score += 1
  if (/[^A-Za-z0-9]/.test(value)) score += 1

  if (score <= 2) return { score, labelKey: 'auth.passwordStrength.weak', color: 'error' }
  if (score <= 3) return { score, labelKey: 'auth.passwordStrength.medium', color: 'warning' }
  return { score, labelKey: 'auth.passwordStrength.strong', color: 'success' }
}

export function strengthPercent(password) {
  const { score } = scorePassword(password)
  return Math.min(100, Math.round((score / 5) * 100))
}
