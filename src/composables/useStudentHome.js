import { computed, ref } from 'vue'
import { fetchStudentDashboard, fetchStudentCourse } from '../api/studentCourses.js'
import { fetchLanguageAccess, fetchDailyPlan } from '../api/language.js'
import { getErrorMessage } from '../api/client.js'
import { ROUTES } from '../constants/app.js'
import { isApiMode } from '../utils/session.js'

function pickContinueCourse(courses) {
  const unlocked = (courses || []).filter((c) => c.unlocked)
  if (!unlocked.length) return null
  const inProgress = unlocked
    .filter((c) => c.progress_percent > 0 && c.progress_percent < 100)
    .sort((a, b) => b.progress_percent - a.progress_percent)
  if (inProgress.length) return inProgress[0]
  const notStarted = unlocked.filter((c) => !c.progress_percent)
  if (notStarted.length) return notStarted[0]
  return unlocked[0]
}

function pickNextLesson(lessons) {
  if (!lessons?.length) return null
  const open = lessons.find((l) => !l.completed && (l.completion_percent || 0) < 100)
  return open || lessons[0]
}

export function useStudentHome() {
  const loading = ref(isApiMode())
  const loadError = ref('')
  const dashboard = ref({
    courses: [],
    unlocked_count: 0,
    locked_count: 0,
    grade: null,
    gamification: null,
    lesson_completion: null,
  })
  const continueLesson = ref(null)
  const languageAccess = ref(null)
  const languageDailyPlan = ref(null)

  const gamification = computed(() => dashboard.value.gamification)
  const courses = computed(() => dashboard.value.courses || [])
  const lessonStats = computed(() => dashboard.value.lesson_completion)

  const continueCourse = computed(() => pickContinueCourse(courses.value))

  const journeyNodes = computed(() =>
    [...courses.value]
      .sort((a, b) => Number(b.unlocked) - Number(a.unlocked) || b.progress_percent - a.progress_percent)
      .map((course) => {
        let status = 'locked'
        if (course.unlocked) {
          if (course.progress_percent >= 100) status = 'done'
          else if (course.progress_percent > 0) status = 'active'
          else status = 'ready'
        }
        return { ...course, status }
      }),
  )

  const dailyFocus = computed(() => {
    const g = gamification.value
    const stats = lessonStats.value
    const lang = languageDailyPlan.value
    if (lang?.goal) {
      return {
        mission: 'أكمل خطة اللغات اليومية',
        target: `${lang.goal} أنشطة`,
        progress: lang.goal ? Math.round((100 * (lang.completed_today || 0)) / lang.goal) : 0,
        detail: `${lang.completed_today || 0} من ${lang.goal} مكتمل`,
      }
    }
    if (stats?.in_progress_lessons) {
      return {
        mission: 'أنهِ الدروس التي بدأتها',
        target: `${stats.in_progress_lessons} دروس قيد التقدّم`,
        progress: stats.completed_lessons
          ? Math.min(
              100,
              Math.round(
                (stats.completed_lessons /
                  Math.max(1, stats.completed_lessons + stats.in_progress_lessons)) *
                  100,
              ),
            )
          : 0,
        detail: `${stats.completed_lessons || 0} مكتمل · ${stats.in_progress_lessons} متبقٍ`,
      }
    }
    if (stats?.pending_lessons) {
      return {
        mission: 'ابدأ درساً جديداً اليوم',
        target: `هدف: درس واحد على الأقل`,
        progress: g?.current_streak ? Math.min(100, g.current_streak * 10) : 0,
        detail: `${stats.pending_lessons} دروس لم تبدأ بعد`,
      }
    }
    return {
      mission: 'استكشف موادك وابدأ رحلتك',
      target: 'هدف اليوم: 20 دقيقة تعلّم',
      progress: g?.progress_percent || 0,
      detail: g?.streak_display || 'ابدأ الآن',
    }
  })

  const recentBadge = computed(() => {
    const badges = gamification.value?.badges || []
    return badges.find((b) => b.unlocked) || gamification.value?.achievements?.[0] || null
  })

  const nextBadge = computed(() => {
    const badges = gamification.value?.badges || []
    return badges.find((b) => !b.unlocked) || null
  })

  const nextMission = computed(() => {
    const course = continueCourse.value
    const lesson = continueLesson.value

    if (!course) {
      const hasLocked = courses.value.some((c) => !c.unlocked)
      return {
        kind: 'empty',
        headline: hasLocked ? 'افتح مادتك الأولى' : 'ابدأ رحلتك التعليمية',
        lessonTitle: hasLocked
          ? 'اشترك في مادة لفتح الدروس مع معلمك'
          : 'لا توجد مواد متاحة لصفك حالياً',
        courseName: null,
        teacherName: null,
        teacherImageUrl: null,
        progress: 0,
        lessonCount: 0,
        completedLessons: 0,
        ctaLabel: hasLocked ? 'الاشتراكات' : 'تحديد الصف',
        to: hasLocked ? ROUTES.STUDENT_SUBSCRIPTIONS : ROUTES.ONBOARDING_GRADE,
      }
    }

    const teacherImageUrl = course.teacher_image_url || course.teacherImageUrl || course.avatar_url
    const base = {
      courseName: course.subject_name,
      teacherName: course.teacher_name,
      teacherImageUrl,
      progress: course.progress_percent || 0,
      lessonCount: course.lesson_count || 0,
      completedLessons: course.completed_lesson_count || 0,
      courseId: course.id,
    }

    if (lesson) {
      const lessonStarted = (lesson.completion_percent || 0) > 0 && !lesson.completed
      return {
        ...base,
        kind: 'lesson',
        headline: lessonStarted ? 'تابع آخر درس وصلت إليه' : 'مهمتك التالية',
        lessonTitle: lesson.title,
        ctaLabel: lessonStarted ? 'متابعة الدرس' : 'ابدأ الدرس',
        to: ROUTES.STUDENT_LESSON(lesson.id),
      }
    }

    return {
      ...base,
      kind: 'course',
      headline: course.progress_percent > 0 ? 'أكمل تقدّمك في المادة' : 'ابدأ أول درس',
      lessonTitle: course.title || `دروس ${course.subject_name}`,
      ctaLabel: 'افتح الدروس',
      to: ROUTES.STUDENT_COURSE(course.id),
    }
  })

  const continueItems = computed(() => {
    const items = []
    if (continueCourse.value && continueLesson.value) {
      items.push({
        key: 'lesson',
        icon: 'mdi-book-open-page-variant',
        label: 'آخر درس',
        title: continueLesson.value.title,
        meta: continueCourse.value.subject_name,
        to: ROUTES.STUDENT_LESSON(continueLesson.value.id),
      })
    } else if (continueCourse.value) {
      items.push({
        key: 'lesson',
        icon: 'mdi-book-open-page-variant',
        label: 'مادة نشطة',
        title: continueCourse.value.title || continueCourse.value.subject_name,
        meta: `${continueCourse.value.progress_percent || 0}% مكتمل`,
        to: ROUTES.STUDENT_COURSE(continueCourse.value.id),
      })
    }
    if (languageAccess.value?.subscribed && languageAccess.value?.placement_completed) {
      items.push({
        key: 'language',
        icon: 'mdi-translate',
        label: 'اللغات',
        title: 'ممارسة اللغة اليوم',
        meta: languageDailyPlan.value
          ? `${languageDailyPlan.value.completed_today || 0}/${languageDailyPlan.value.goal || 0} اليوم`
          : 'تابع مسارك',
        to: ROUTES.STUDENT_LANGUAGES_LESSONS,
      })
    }
    if (continueCourse.value?.unlocked) {
      items.push({
        key: 'quiz',
        icon: 'mdi-clipboard-text-outline',
        label: 'كويز',
        title: `كويزات ${continueCourse.value.subject_name}`,
        meta: 'اختبر فهمك',
        to: ROUTES.STUDENT_COURSE_QUIZZES(continueCourse.value.id),
      })
    }
    if (languageAccess.value?.subscribed) {
      items.push({
        key: 'scenario',
        icon: 'mdi-drama-masks',
        label: 'سيناريو',
        title: 'محادثة تطبيقية',
        meta: 'تمرين واقعي',
        to: ROUTES.STUDENT_LANGUAGES_SCENARIOS,
      })
    }
    return items
  })

  async function load() {
    if (!isApiMode()) {
      loading.value = false
      return
    }
    loading.value = true
    loadError.value = ''
    continueLesson.value = null
    languageAccess.value = null
    languageDailyPlan.value = null
    try {
      dashboard.value = await fetchStudentDashboard()
      const candidate = pickContinueCourse(dashboard.value.courses)
      const tasks = []
      if (candidate?.id) {
        tasks.push(
          fetchStudentCourse(candidate.id)
            .then((detail) => {
              continueLesson.value = pickNextLesson(detail.lessons)
            })
            .catch(() => {
              continueLesson.value = null
            }),
        )
      }
      tasks.push(
        fetchLanguageAccess()
          .then(async (access) => {
            languageAccess.value = access
            if (access?.subscribed && access?.placement_completed) {
              try {
                languageDailyPlan.value = await fetchDailyPlan()
              } catch {
                languageDailyPlan.value = null
              }
            }
          })
          .catch(() => {
            languageAccess.value = null
          }),
      )
      await Promise.all(tasks)
    } catch (err) {
      loadError.value = getErrorMessage(err, 'تعذر تحميل رحلتك')
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    loadError,
    dashboard,
    gamification,
    courses,
    lessonStats,
    continueCourse,
    continueLesson,
    continueItems,
    journeyNodes,
    dailyFocus,
    recentBadge,
    nextBadge,
    nextMission,
    languageAccess,
    languageDailyPlan,
    load,
  }
}
