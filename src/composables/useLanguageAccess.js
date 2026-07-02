import { ref } from 'vue'
import { fetchLanguageAccess } from '../api/language.js'
import { getErrorMessage } from '../api/client.js'

const accessCache = ref(null)
const loading = ref(false)
const error = ref('')

export function useLanguageAccess() {
  async function loadAccess(force = false) {
    if (accessCache.value && !force) return accessCache.value
    loading.value = true
    error.value = ''
    try {
      accessCache.value = await fetchLanguageAccess()
      return accessCache.value
    } catch (e) {
      error.value = getErrorMessage(e, 'Unable to load language subscription status')
      throw e
    } finally {
      loading.value = false
    }
  }

  function clearLanguageAccessCache() {
    accessCache.value = null
  }

  return {
    access: accessCache,
    loading,
    error,
    loadAccess,
    clearLanguageAccessCache,
  }
}
