import { ref } from 'vue'
import { generateWritingLesson } from '../api/language.js'
import { getErrorMessage } from '../api/client.js'

/**
 * W6 lesson generation — POST /writing/generate only; no frontend educational logic.
 */
export function useWritingLesson() {
  const lesson = ref(null)
  const phase = ref('idle')
  const error = ref('')

  async function generate({ goal = null } = {}) {
    phase.value = 'generating'
    error.value = ''
    try {
      lesson.value = await generateWritingLesson({ goal })
      phase.value = 'ready'
      return lesson.value
    } catch (err) {
      phase.value = 'error'
      error.value = getErrorMessage(err, 'Could not generate writing lesson')
      throw err
    }
  }

  function reset() {
    lesson.value = null
    phase.value = 'idle'
    error.value = ''
  }

  return {
    lesson,
    phase,
    error,
    generate,
    reset,
  }
}
