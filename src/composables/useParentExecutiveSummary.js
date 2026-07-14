import { ref, onUnmounted } from 'vue'
import { fetchParentExecutiveSummary } from '../api/parent.js'
import { getErrorMessage } from '../api/client.js'
import { resolveParentStudentId } from '../utils/parentStorage.js'
import { isApiMode } from '../utils/session.js'
import { LESSON_COMPLETED_EVENT } from '../utils/lessonCompletionEvents.js'

export function useParentExecutiveSummary(selectedStudentId) {
  const summary = ref(null)
  const loading = ref(false)
  const loadError = ref('')
  let loadSeq = 0

  async function load() {
    const studentId = resolveParentStudentId(selectedStudentId)
    if (studentId == null) {
      loadSeq += 1
      summary.value = null
      loadError.value = ''
      loading.value = false
      return
    }
    if (!isApiMode()) {
      loadError.value = 'الملخص التنفيذي يتطلب الاتصال بالخادم'
      return
    }

    const seq = ++loadSeq
    loading.value = true
    loadError.value = ''
    try {
      summary.value = await fetchParentExecutiveSummary(studentId)
      if (seq !== loadSeq) return
    } catch (err) {
      if (seq !== loadSeq) return
      loadError.value = getErrorMessage(err, 'تعذر تحميل الملخص التنفيذي')
      summary.value = null
    } finally {
      if (seq === loadSeq) loading.value = false
    }
  }

  function onLessonCompleted() {
    load()
  }

  window.addEventListener(LESSON_COMPLETED_EVENT, onLessonCompleted)
  onUnmounted(() => {
    window.removeEventListener(LESSON_COMPLETED_EVENT, onLessonCompleted)
  })

  return { summary, loading, loadError, error: loadError, load }
}
