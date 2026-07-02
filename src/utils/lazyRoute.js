/** One-shot auto-reload when a lazy route chunk fails to load (dev stale deps / 504). */
export const CHUNK_RELOAD_KEY = 'eduspark:chunk-reload'

export function isChunkLoadError(error) {
  const msg = String(error?.message || error || '')
  return (
    msg.includes('Failed to fetch dynamically imported module') ||
    msg.includes('Outdated Optimize Dep') ||
    msg.includes('504') ||
    error?.code === 'ERR_OUTDATED_OPTIMIZED_DEP'
  )
}

export function lazyRoute(importer) {
  return () =>
    importer().catch((error) => {
      if (!isChunkLoadError(error)) throw error
      if (!sessionStorage.getItem(CHUNK_RELOAD_KEY)) {
        sessionStorage.setItem(CHUNK_RELOAD_KEY, '1')
        window.location.reload()
        return new Promise(() => {})
      }
      sessionStorage.removeItem(CHUNK_RELOAD_KEY)
      throw error
    })
}
