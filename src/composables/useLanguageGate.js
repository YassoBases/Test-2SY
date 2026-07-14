import { useRouter } from 'vue-router'
import { getErrorMessage } from '../api/client.js'

export function useLanguageGate() {
  const router = useRouter()

  function handleLanguageApiError(e, access) {
    const detail = e?.response?.data?.detail
    const redirect =
      (typeof detail === 'object' && detail?.redirect) ||
      access?.redirect ||
      null
    if (redirect) {
      router.push(redirect)
      return true
    }
    return false
  }

  return { handleLanguageApiError, getErrorMessage }
}

function buildSubmitAnswers(answerMap) {
  const answers = {}
  for (const [qid, idx] of Object.entries(answerMap || {})) {
    if (idx === undefined || idx === null || idx === '') continue
    answers[qid] = { selected_index: Number(idx) }
  }
  return answers
}

export { buildSubmitAnswers }
