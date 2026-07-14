import { computed, unref } from 'vue'

/**
 * Continue CTA at the end of the unified learn flow (UI-4.3).
 */
export function useLessonLearnContinue({
  lesson,
  lessonProgress,
  learnComplete,
  studentQuestionCount,
}) {
  return computed(() => {
    const l = unref(lesson)
    const progress = unref(lessonProgress)
    const r = progress?.requirements
    const teacher = l?.teacherName || 'المعلّم'

    if (!unref(learnComplete)) {
      if (l?.has_video && !r?.video_met) {
        return {
          eyebrow: 'تابع التعلّم',
          message: `ابدأ بمشاهدة شرح ${teacher} — ثم تابع بقية الدرس`,
          cta: 'تابعي المشاهدة',
          action: 'scrollVideo',
          icon: 'mdi-play-circle',
        }
      }
      if (l?.has_pdf && !r?.pdf_met) {
        return {
          eyebrow: 'تابع التعلّم',
          message: `اقرأي شرح ${teacher} في ملف الدرس`,
          cta: 'تابعي القراءة',
          action: 'scrollPdf',
          icon: 'mdi-file-pdf-box',
        }
      }
      return {
        eyebrow: 'تابع التعلّم',
        message: 'راجعي محتوى الدرس قبل الانتقال للخطوة التالية',
        cta: 'راجع المحتوى',
        action: 'scrollStart',
        icon: 'mdi-book-open-page-variant',
      }
    }

    if (l?.has_ai_chat && unref(studentQuestionCount) < 1) {
      return {
        eyebrow: 'أنهيتِ التعلّم — ماذا بعد؟',
        message: `اسألي ${teacher} عن ما تعلّمته — سؤال واحد يثبت الفهم`,
        cta: 'اسأل المعلّم',
        action: 'goChat',
        icon: 'mdi-message-text',
      }
    }

    return {
      eyebrow: 'أنهيتِ التعلّم — ماذا بعد؟',
      message: 'اختبر فهمك لما تعلّمته في هذا الدرس',
      cta: 'اختبر فهمك',
      action: 'goQuiz',
      icon: 'mdi-clipboard-check',
    }
  })
}
