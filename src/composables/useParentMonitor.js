import { ref, onUnmounted } from 'vue'
import { fetchParentDashboardApi } from '../api/parent.js'
import { getErrorMessage } from '../api/client.js'
import { resolveParentStudentId } from '../utils/parentStorage.js'
import { isApiMode } from '../utils/session.js'
import { LESSON_COMPLETED_EVENT } from '../utils/lessonCompletionEvents.js'

export function useParentMonitor(selectedStudentId) {
  const loading = ref(false)
  const loadError = ref('')
  const child = ref(null)
  const activity = ref([])
  const insights = ref([])
  const stats = ref({})
  const quiz = ref({})
  const attendance = ref({})
  const planner = ref({})
  const courseProgress = ref([])
  const subscriptions = ref([])
  const languagePlacement = ref(null)
  const gamification = ref(null)
  const academicIntelligence = ref(null)
  const lessonProgress = ref(null)
  let loadSeq = 0

  async function load() {
    const studentId = resolveParentStudentId(selectedStudentId)
    if (studentId == null) {
      loadSeq += 1
      child.value = null
      activity.value = []
      insights.value = []
      stats.value = {}
      quiz.value = {}
      attendance.value = {}
      planner.value = {}
      gamification.value = null
      courseProgress.value = []
      subscriptions.value = []
      languagePlacement.value = null
      academicIntelligence.value = null
      lessonProgress.value = null
      loadError.value = ''
      loading.value = false
      return
    }

    const seq = ++loadSeq
    loading.value = true
    loadError.value = ''
    try {
      if (!isApiMode()) {
        if (seq !== loadSeq) return
        loadError.value = 'لوحة ولي الأمر تتطلب الاتصال بالخادم'
        return
      }
      const data = await fetchParentDashboardApi(studentId)
      if (seq !== loadSeq) return
      child.value = data.child
      activity.value = data.activity || []
      insights.value = data.insights || []
      stats.value = data.stats || {}
      quiz.value = data.quiz || {}
      attendance.value = data.attendance || {}
      planner.value = data.planner || {}
      courseProgress.value = data.course_progress || []
      subscriptions.value = data.subscriptions || []
      languagePlacement.value = data.language_placement || null
      gamification.value = data.gamification || null
      academicIntelligence.value = data.academic_intelligence || null
      lessonProgress.value = data.lesson_progress || null
    } catch (err) {
      if (seq !== loadSeq) return
      loadError.value = getErrorMessage(err, 'تعذر تحميل لوحة المتابعة')
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

  return {
    loading,
    loadError,
    child,
    activity,
    insights,
    stats,
    quiz,
    attendance,
    planner,
    courseProgress,
    subscriptions,
    languagePlacement,
    gamification,
    academicIntelligence,
    lessonProgress,
    load,
  }
}
