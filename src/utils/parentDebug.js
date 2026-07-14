/**
 * Temporary parent portal debug logging.
 * Enable in browser console: localStorage.setItem('eduspark_parent_debug', '1')
 * Disable: localStorage.removeItem('eduspark_parent_debug')
 */
const PREFIX = '[parent-debug]'

export function isParentDebugEnabled() {
  try {
    return import.meta.env.DEV || localStorage.getItem('eduspark_parent_debug') === '1'
  } catch {
    return import.meta.env.DEV
  }
}

export function parentDebug(scope, event, detail = undefined) {
  if (!isParentDebugEnabled()) return
  const payload = {
    ts: new Date().toISOString(),
    scope,
    event,
    ...(detail !== undefined ? { detail } : {}),
  }
  console.debug(PREFIX, payload)
  try {
    window.__parentDebugLog = window.__parentDebugLog || []
    window.__parentDebugLog.push(payload)
    if (window.__parentDebugLog.length > 500) {
      window.__parentDebugLog.splice(0, window.__parentDebugLog.length - 500)
    }
  } catch {
    /* ignore */
  }
}

export function logErrorStateChange(scope, refName, from, to, context = undefined) {
  if (from === to) return
  parentDebug(scope, 'error-state-change', { ref: refName, from: from || '', to: to || '', ...context })
}

export function trackErrorRef(scope, refName, errorRef) {
  if (!isParentDebugEnabled()) return () => {}
  let prev = errorRef.value
  return () => {
    const next = errorRef.value
    if (next !== prev) {
      logErrorStateChange(scope, refName, prev, next)
      prev = next
    }
  }
}
