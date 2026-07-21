import { computed, ref } from 'vue'
import { fetchGrammarStatus } from '../api/grammar.js'

const enabled = ref(null)
const loading = ref(false)
let loadPromise = null

export function useGrammarModule() {
  async function refresh() {
    if (loadPromise) return loadPromise
    loading.value = true
    loadPromise = fetchGrammarStatus()
      .then((data) => {
        enabled.value = !!data?.enabled
      })
      .catch(() => {
        enabled.value = false
      })
      .finally(() => {
        loading.value = false
        loadPromise = null
      })
    return loadPromise
  }

  const isEnabled = computed(() => enabled.value === true)
  const isReady = computed(() => enabled.value !== null)

  return { enabled, isEnabled, isReady, loading, refresh }
}
