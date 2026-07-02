import { ref } from 'vue'
import { fetchGamificationProfileApi } from '../api/gamification.js'
import { getErrorMessage } from '../api/client.js'

export function useGamification() {
  const profile = ref(null)
  const loading = ref(false)
  const error = ref('')

  async function load() {
    loading.value = true
    error.value = ''
    try {
      profile.value = await fetchGamificationProfileApi()
    } catch (err) {
      error.value = getErrorMessage(err, 'تعذر تحميل الإنجازات')
      profile.value = null
    } finally {
      loading.value = false
    }
  }

  return { profile, loading, error, load }
}
