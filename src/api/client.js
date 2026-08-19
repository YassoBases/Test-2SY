import axios from 'axios'
import { getSession, clearSession } from '../utils/session.js'
import { t, readStoredLocale } from '../i18n/index.js'

const AUTH_PATHS = ['/auth/login', '/auth/register']

function isAuthRequest(url = '') {
  return AUTH_PATHS.some((p) => url.includes(p))
}

/** Dev uses Vite proxy (/api) unless VITE_API_DIRECT=true (avoids CORS). */
import { isParentDebugEnabled, parentDebug } from '../utils/parentDebug.js'

export function getApiBaseUrl() {
  const envUrl = (import.meta.env.VITE_API_URL || '').trim().replace(/\/$/, '')
  if (import.meta.env.DEV && import.meta.env.VITE_API_DIRECT !== 'true') {
    return '/api'
  }
  if (!envUrl) return '/api'
  if (envUrl.endsWith('/api')) return envUrl
  return `${envUrl}/api`
}

export const api = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
  timeout: 120000,
})

api.interceptors.request.use((config) => {
  if (isAuthRequest(config.url)) {
    return config
  }
  const session = getSession()
  if (session?.accessToken) {
    config.headers.Authorization = `Bearer ${session.accessToken}`
  }
  config.headers['Accept-Language'] = readStoredLocale() || 'ar'
  if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  if (isParentDebugEnabled() && String(config.url || '').includes('/parent/')) {
    config.metadata = { parentDebugStart: Date.now(), url: config.url, method: config.method }
    parentDebug('api', 'request-start', {
      method: config.method,
      url: config.url,
      params: config.params,
    })
  }
  return config
})

api.interceptors.response.use(
  (res) => {
    const meta = res.config?.metadata
    if (meta?.parentDebugStart) {
      parentDebug('api', 'request-success', {
        method: meta.method,
        url: meta.url,
        status: res.status,
        durationMs: Date.now() - meta.parentDebugStart,
      })
    }
    return res
  },
  (err) => {
    const meta = err.config?.metadata
    if (meta?.parentDebugStart) {
      parentDebug('api', 'request-failure', {
        method: meta.method,
        url: meta.url,
        status: err.response?.status,
        durationMs: Date.now() - meta.parentDebugStart,
        body: typeof err.response?.data === 'string' ? err.response.data.slice(0, 200) : err.response?.data?.detail,
      })
    }
    const url = err.config?.url || ''
    if (err.response?.status === 401 && !isAuthRequest(url)) {
      clearSession()
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  },
)

export function isTimeoutError(err) {
  return err?.code === 'ECONNABORTED' || err?.code === 'ETIMEDOUT' || /timeout/i.test(err?.message || '')
}

export function getErrorMessage(err, fallback) {
  const genericFallback = t('errors.generic')
  const resolvedFallback = fallback ?? genericFallback

  if (!err.response) {
    if (isTimeoutError(err)) {
      if (fallback != null && fallback !== genericFallback) {
        return `${fallback}${t('errors.timeoutSuffix')}`
      }
      return t('errors.timeoutProcessing')
    }
    if (err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
      return t('errors.networkFastApi')
    }
    if (err?.message) return err.message
    return resolvedFallback
  }

  const data = err.response?.data
  const detail = data?.detail ?? data?.message

  if (typeof detail === 'string' && detail.trim()) {
    if (detail === 'Internal Server Error') {
      return t('errors.internalServerError')
    }
    return detail
  }

  if (typeof detail === 'object' && detail !== null && !Array.isArray(detail)) {
    if (typeof detail.message === 'string' && detail.message.trim()) return detail.message
    if (typeof detail.msg === 'string' && detail.msg.trim()) return detail.msg
  }

  if (Array.isArray(detail) && detail.length) {
    const parts = detail.map((item) => formatValidationIssue(item)).filter(Boolean)
    if (parts.length) return parts.join(' — ')
  }

  if (typeof data === 'string' && data.trim()) return data

  const status = err.response?.status
  if (status === 422) return t('errors.validation422')
  if (status === 400) return t('errors.badRequest400')
  if (status === 403) return t('errors.forbidden')
  if (status === 404) return t('errors.notFound')
  if (status >= 500) return t('errors.serverError500')

  return resolvedFallback
}

const EXPORT_LABELS = { csv: 'CSV', xlsx: 'Excel', pdf: 'PDF' }

/** Export failures must never reuse the report-load connection error copy. */
export function getExportErrorMessage(err, format = 'pdf') {
  const label = EXPORT_LABELS[format] || format.toUpperCase()
  const fallback = t('errors.exportFailed', { format: label })

  if (!err.response) {
    if (isTimeoutError(err)) {
      return t('errors.exportTimeout', { format: label })
    }
    if (err.code === 'ERR_FAILED' || err.code === 'ERR_NETWORK' || err.message === 'Network Error') {
      return t('errors.exportDownloadFailed', { format: label })
    }
    if (err?.message) return `${fallback} (${err.message})`
    return fallback
  }

  if (err.response.status === 503) {
    return getErrorMessage(err, fallback)
  }

  return getErrorMessage(err, fallback)
}

function formatValidationIssue(item) {
  if (typeof item === 'string') return item
  if (!item || typeof item !== 'object') return ''

  const loc = Array.isArray(item.loc) ? item.loc.filter((p) => p !== 'body') : []
  const field = loc.length ? String(loc[loc.length - 1]) : ''
  const msg = String(item.msg || '')

  const fieldLabel = field ? t(`validation.fields.${field}`, field) : field

  if (field === 'due_at' && /datetime|date|future|past|valid/i.test(msg)) {
    return t('validation.quiz.dueAtFuture')
  }
  if (field === 'title' && /string|required|valid/i.test(msg)) {
    return t('validation.quiz.titleRequired')
  }
  if (field === 'duration_minutes') {
    return t('validation.quiz.durationInvalid')
  }
  if (field === 'passing_score_percent') {
    return t('validation.quiz.passingScoreInvalid')
  }

  if (fieldLabel && msg) return `${fieldLabel}: ${msg}`
  return msg || fieldLabel
}
