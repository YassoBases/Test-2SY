import { computed, unref } from 'vue'

export const LESSON_SESSION_STEPS = [
  { id: 'learn', label: 'تعلّم', icon: 'mdi-book-open-page-variant' },
  { id: 'ask', label: 'اسأل المعلّم', icon: 'mdi-message-text' },
  { id: 'quiz', label: 'اختبر نفسك', icon: 'mdi-clipboard-check' },
  { id: 'complete', label: 'أنهِ الدرس', icon: 'mdi-flag-checkered' },
]

function tabToStepId(tab) {
  if (tab === 'learn') return 'learn'
  if (tab === 'chat') return 'ask'
  if (tab === 'quiz') return 'quiz'
  if (tab === 'video' || tab === 'file') return 'learn'
  return 'learn'
}

/**
 * Session orientation for UI-4.2 — derives step state and header CTA from existing lesson data.
 */
export function useLessonSession({
  lesson,
  lessonProgress,
  activeTab,
  studentQuestionCount,
  quizComplete,
  mistakeReview,
  progressNextStep,
  progressPercent,
  progressActionDisabled,
  verifying,
  nextLesson,
}) {
  const learnComplete = computed(() => {
    const r = unref(lessonProgress)?.requirements
    const l = unref(lesson)
    if (r) {
      const videoOk = !r.requires_video || r.video_met
      const pdfOk = !r.requires_pdf || r.pdf_met
      return videoOk && pdfOk
    }
    if (!l?.has_video && !l?.has_pdf) return true
    return false
  })

  const askComplete = computed(() => {
    const l = unref(lesson)
    if (!l?.has_ai_chat) return learnComplete.value
    return unref(studentQuestionCount) >= 1
  })

  const quizStepComplete = computed(() => {
    const r = unref(lessonProgress)?.requirements
    if (r?.quiz_met) return true
    return unref(quizComplete) && unref(mistakeReview).length === 0
  })

  const completeStepDone = computed(() => Boolean(unref(lessonProgress)?.is_completed))

  const currentStepId = computed(() => {
    const progress = unref(lessonProgress)
    if (progress?.is_completed) return 'complete'
    if (progress?.can_verify) return 'complete'

    const tabStep = tabToStepId(unref(activeTab))
    if (tabStep === 'ask' || tabStep === 'quiz') return tabStep
    if (tabStep === 'learn' && !learnComplete.value) return 'learn'

    if (!learnComplete.value) return 'learn'
    if (!askComplete.value) return 'ask'
    if (!quizStepComplete.value) return 'quiz'
    return 'complete'
  })

  const sessionSteps = computed(() =>
    LESSON_SESSION_STEPS.map((step) => {
      const completed =
        step.id === 'learn'
          ? learnComplete.value
          : step.id === 'ask'
            ? askComplete.value
            : step.id === 'quiz'
              ? quizStepComplete.value
              : completeStepDone.value

      const current = currentStepId.value === step.id
      let status = 'upcoming'
      if (completed) status = 'completed'
      else if (current) status = 'current'

      return { ...step, status, completed, current }
    }),
  )

  const sessionProgressPercent = computed(() => {
    const progress = unref(lessonProgress)
    if (progress?.completion_percent != null) {
      return Math.min(100, Math.round(progress.completion_percent))
    }
    if (progress?.completion_percentage != null) {
      return Math.min(100, Math.round(progress.completion_percentage))
    }

    let score = 0
    if (learnComplete.value) score += 25
    if (askComplete.value) score += 25
    if (quizStepComplete.value) score += 25
    if (completeStepDone.value) score += 25

    const fallback = unref(progressPercent) ?? 0
    return Math.min(100, Math.max(score, fallback))
  })

  const headerNextAction = computed(() => {
    const progress = unref(lessonProgress)
    const l = unref(lesson)
    const next = unref(nextLesson)

    if (progress?.is_completed) {
      if (next) {
        return {
          label: 'الخطوة التالية',
          text: 'انتقل إلى الدرس التالي',
          action: 'nextLesson',
          cta: 'التالي',
          icon: 'mdi-chevron-left',
          disabled: false,
          loading: false,
        }
      }
      return {
        label: 'الخطوة التالية',
        text: 'عد إلى قائمة الدروس',
        action: 'backToCourse',
        cta: 'عودة',
        icon: 'mdi-arrow-right',
        disabled: false,
        loading: false,
      }
    }

    if (progress?.can_verify) {
      return {
        label: 'الخطوة التالية',
        text: 'أنهِ الدرس',
        action: 'verify',
        cta: 'إكمال',
        icon: 'mdi-flag-checkered',
        disabled: Boolean(unref(verifying)),
        loading: Boolean(unref(verifying)),
      }
    }

    if (!learnComplete.value) {
      const r = progress?.requirements
      if (l?.has_video && !r?.video_met) {
        return {
          label: 'الخطوة التالية',
          text: 'شاهد الفيديو',
          action: 'scrollVideo',
          cta: 'ابدأ',
          icon: 'mdi-play-circle',
          disabled: false,
          loading: false,
        }
      }
      if (l?.has_pdf && !r?.pdf_met) {
        return {
          label: 'الخطوة التالية',
          text: 'اقرأ الدرس',
          action: 'scrollPdf',
          cta: 'اقرأ',
          icon: 'mdi-file-pdf-box',
          disabled: false,
          loading: false,
        }
      }
      return {
        label: 'الخطوة التالية',
        text: 'تعرّف على محتوى الدرس',
        action: 'scrollStart',
        cta: 'ابدأ',
        icon: 'mdi-book-open-page-variant',
        disabled: false,
        loading: false,
      }
    }

    if (l?.has_ai_chat && unref(studentQuestionCount) < 1) {
      return {
        label: 'الخطوة التالية',
        text: 'اسأل المعلّم سؤالاً عن الدرس',
        action: 'goChat',
        cta: 'اسأل',
        icon: 'mdi-message-text',
        disabled: false,
        loading: false,
      }
    }

    if (!unref(quizComplete)) {
      return {
        label: 'الخطوة التالية',
        text: 'أكمل الاختبار',
        action: 'goQuiz',
        cta: 'اختبر',
        icon: 'mdi-clipboard-check',
        disabled: false,
        loading: false,
      }
    }

    const step = unref(progressNextStep)
    if (step?.action === 'askKeywords') {
      return {
        label: 'الخطوة التالية',
        text: 'اسأل المعلّم سؤالاً عن الدرس',
        action: 'askKeywords',
        cta: step.cta || 'اسأل',
        icon: step.icon || 'mdi-message-text',
        disabled: Boolean(unref(progressActionDisabled)),
        loading: false,
      }
    }

    if (step?.action === 'regenerateQuiz') {
      return {
        label: 'الخطوة التالية',
        text: unref(mistakeReview).length ? 'راجع الأخطاء ثم اختبر مجدداً' : step.text,
        action: 'regenerateQuiz',
        cta: step.cta || 'اختبار',
        icon: step.icon || 'mdi-clipboard-check',
        disabled: Boolean(unref(progressActionDisabled)),
        loading: false,
      }
    }

    return {
      label: 'الخطوة التالية',
      text: step?.text || 'تابع جلسة التعلم',
      action: step?.action || 'goQuiz',
      cta: step?.cta || '',
      icon: step?.icon || 'mdi-arrow-left-circle',
      disabled: !step?.action || Boolean(unref(progressActionDisabled)),
      loading: false,
    }
  })

  return {
    sessionSteps,
    currentStepId,
    sessionProgressPercent,
    headerNextAction,
    learnComplete,
    askComplete,
    quizStepComplete,
  }
}
