import { ref } from 'vue'
import { fetchLessonProgress, updateLessonProgress } from '../api/studentCourses.js'
import { getErrorMessage } from '../api/client.js'

export function buildFallbackProgress(lessonId, lesson = {}) {
  const requiresVideo = Boolean(lesson.has_video)
  const requiresPdf = Boolean(lesson.has_pdf)
  const requiresQuiz = Boolean(lesson.has_generated_quiz)
  return {
    lesson_id: Number(lessonId),
    lesson_title: lesson.title || null,
    course_id: lesson.courseId ?? lesson.course_id ?? null,
    video_progress_percent: 0,
    pdf_progress_percent: 0,
    pdf_opened: false,
    quiz_submitted: false,
    quiz_score_percent: 0,
    is_completed: false,
    completed_at: null,
    completion_type: null,
    completion_percentage: 0,
    completion_percent: 0,
    requirements: {
      requires_video: requiresVideo,
      requires_pdf: requiresPdf,
      requires_quiz: requiresQuiz,
      video_threshold: 90,
      pdf_threshold: 100,
      quiz_score_threshold: 100,
      video_met: false,
      pdf_met: false,
      quiz_submitted_met: false,
      quiz_score_met: false,
      quiz_met: false,
    },
    checklist: [],
    can_verify: false,
    lesson_type: requiresVideo && requiresPdf ? 'mixed' : requiresPdf ? 'pdf' : requiresVideo ? 'video' : 'other',
    newly_completed: false,
  }
}

export function useLessonProgress(lessonIdRef, lessonRef = null) {
  const progress = ref(null)
  const loading = ref(false)
  const loadError = ref('')
  let videoTimer = null
  let pdfTimer = null

  async function load() {
    const id = lessonIdRef?.value ?? lessonIdRef
    if (!id) return
    loading.value = true
    loadError.value = ''
    try {
      progress.value = await fetchLessonProgress(id)
    } catch (err) {
      const lesson = lessonRef?.value ?? lessonRef
      loadError.value = getErrorMessage(err, 'تعذر تحميل تقدّم الدرس')
      progress.value = buildFallbackProgress(id, lesson || {})
    } finally {
      loading.value = false
    }
  }

  async function pushUpdate(payload) {
    const id = lessonIdRef?.value ?? lessonIdRef
    if (!id || progress.value?.is_completed) return
    try {
      const data = await updateLessonProgress(id, payload)
      progress.value = data
      loadError.value = ''
      return data
    } catch {
      return null
    }
  }

  function onVideoTimeUpdate(videoEl) {
    if (!videoEl?.duration || videoEl.duration <= 0) return
    const pct = (videoEl.currentTime / videoEl.duration) * 100
    clearTimeout(videoTimer)
    videoTimer = setTimeout(() => {
      pushUpdate({ video_percent: Math.min(100, pct) })
    }, 4000)
  }

  function onPdfProgress({ pdf_percent, pdf_opened }) {
    clearTimeout(pdfTimer)
    pdfTimer = setTimeout(() => {
      pushUpdate({ pdf_percent, pdf_opened: pdf_opened ?? true })
    }, 800)
  }

  function onPdfOpened() {
    pushUpdate({ pdf_opened: true, pdf_percent: progress.value?.pdf_progress_percent || 0 })
  }

  return {
    progress,
    loading,
    loadError,
    load,
    pushUpdate,
    onVideoTimeUpdate,
    onPdfProgress,
    onPdfOpened,
  }
}
