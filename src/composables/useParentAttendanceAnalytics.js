import { ref } from 'vue'
import { fetchParentAttendanceAnalytics } from '../api/activity.js'
import { getErrorMessage } from '../api/client.js'
import { resolveParentStudentId } from '../utils/parentStorage.js'
import { isApiMode } from '../utils/session.js'

export function useParentAttendanceAnalytics(selectedStudentId) {
  const loading = ref(false)
  const loadError = ref('')
  const weekOffset = ref(0)
  const monthOffset = ref(0)
  const analytics = ref(null)
  let loadSeq = 0

  async function load() {
    const studentId = resolveParentStudentId(selectedStudentId)
    if (studentId == null) {
      loadSeq += 1
      analytics.value = null
      loadError.value = ''
      loading.value = false
      return
    }
    if (!isApiMode()) {
      loadError.value = 'تحليلات الحضور تتطلب الاتصال بالخادم'
      return
    }

    const seq = ++loadSeq
    loading.value = true
    loadError.value = ''
    try {
      analytics.value = await fetchParentAttendanceAnalytics(studentId, {
        weekOffset: weekOffset.value,
        monthOffset: monthOffset.value,
      })
      if (seq !== loadSeq) return
    } catch (err) {
      if (seq !== loadSeq) return
      loadError.value = getErrorMessage(err, 'تعذر تحميل تحليلات وقت الدراسة')
      analytics.value = null
    } finally {
      if (seq === loadSeq) loading.value = false
    }
  }

  function setWeekOffset(offset) {
    weekOffset.value = offset
    load()
  }

  function setMonthOffset(offset) {
    monthOffset.value = offset
    load()
  }

  function resetOffsetsAndLoad() {
    weekOffset.value = 0
    monthOffset.value = 0
    return load()
  }

  return {
    loading,
    loadError,
    error: loadError,
    analytics,
    weekOffset,
    monthOffset,
    setWeekOffset,
    setMonthOffset,
    reload: load,
    resetOffsetsAndLoad,
  }
}
