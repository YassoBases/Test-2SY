import { createRouter, createWebHistory } from 'vue-router'
import { fetchMe } from '../api/auth.js'
import { fetchLanguageAccess } from '../api/language.js'
import { CHUNK_RELOAD_KEY, isChunkLoadError, lazyRoute } from '../utils/lazyRoute.js'
import { getSession, isApiMode, isParentViewer, setSession } from '../utils/session.js'
import { ROUTES } from '../constants/app.js'
import {
  isPublicEntryRoute,
  mergeUserIntoSession,
  onboardingRouteForSession,
  resolvePostAuthRoute,
} from '../utils/studentFlow.js'

const routes = [
  {
    path: '/',
    name: 'welcome',
    component: lazyRoute(() => import('../views/WelcomeView.vue')),
    meta: { title: 'Welcome', guest: true },
  },
  {
    path: '/login',
    name: 'login',
    component: lazyRoute(() => import('../views/LoginView.vue')),
    meta: { title: 'Sign In', guest: true },
  },
  {
    path: '/register',
    name: 'register',
    component: lazyRoute(() => import('../views/RegisterView.vue')),
    meta: { title: 'Create Account', guest: true },
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: lazyRoute(() => import('../views/ForgotPasswordView.vue')),
    meta: { title: 'Forgot Password', guest: true },
  },
  {
    path: '/reset-password',
    name: 'reset-password',
    component: lazyRoute(() => import('../views/ResetPasswordView.vue')),
    meta: { title: 'Reset Password' },
  },
  {
    path: '/verify-email',
    name: 'verify-email',
    component: lazyRoute(() => import('../views/VerifyEmailView.vue')),
    meta: { title: 'Verify Email' },
  },
  {
    path: '/login/verify-2fa',
    name: 'login-verify-2fa',
    component: lazyRoute(() => import('../views/TwoFactorVerifyView.vue')),
    meta: { title: 'Two-Factor Authentication', guest: true },
  },
  {
    path: '/register/parent',
    redirect: (to) => ({
      path: '/register',
      query: { ...to.query, role: 'parent' },
    }),
  },
  {
    path: '/verify-certificate/:certificateNumber',
    name: 'verify-certificate',
    component: lazyRoute(() => import('../views/VerifyCertificateView.vue')),
    meta: { title: 'Verify Certificate' },
  },
  {
    path: '/student/onboarding',
    component: lazyRoute(() => import('../layouts/OnboardingLayout.vue')),
    meta: { requiresAuth: true, role: 'student', onboardingFlow: true },
    children: [
      { path: '', redirect: { name: 'onboarding-grade' } },
      {
        path: 'grade',
        name: 'onboarding-grade',
        component: lazyRoute(() => import('../views/onboarding/OnboardingGradeView.vue')),
        meta: { title: 'Select Grade', onboardingStep: 'grade' },
      },
      {
        path: 'personalize',
        name: 'onboarding-personalize',
        component: lazyRoute(() => import('../views/onboarding/OnboardingPersonalizeView.vue')),
        meta: { title: 'Personalize' },
      },
      {
        path: 'subjects',
        name: 'onboarding-subjects',
        component: lazyRoute(() => import('../views/onboarding/OnboardingSubjectsView.vue')),
        meta: { title: 'Select Subjects', onboardingStep: 'subjects' },
      },
      {
        path: 'teachers',
        name: 'onboarding-teachers',
        component: lazyRoute(() => import('../views/onboarding/OnboardingTeachersView.vue')),
        meta: { title: 'Select Teachers', onboardingStep: 'teachers' },
      },
    ],
  },
  {
    path: '/student/payment',
    name: 'student-payment',
    component: lazyRoute(() => import('../views/payment/StudentPaymentView.vue')),
    meta: { requiresAuth: true, role: 'student', paymentFlow: true, title: 'Payment' },
  },
  {
    path: '/student/payment/success',
    name: 'student-payment-success',
    component: lazyRoute(() => import('../views/payment/StudentPaymentSuccessView.vue')),
    meta: { requiresAuth: true, role: 'student', paymentFlow: true, title: 'Payment made' },
  },
  {
    path: '/teacher/setup',
    name: 'teacher-setup',
    component: lazyRoute(() => import('../views/teacher/TeacherSetupView.vue')),
    meta: { requiresAuth: true, role: 'teacher', teacherSetup: true, title: 'Teacher preparation' },
  },
  {
    path: '/teacher',
    component: lazyRoute(() => import('../layouts/TeacherLayout.vue')),
    meta: { requiresAuth: true, role: 'teacher' },
    children: [
      { path: '', redirect: { name: 'teacher-dashboard' } },
      {
        path: 'dashboard',
        name: 'teacher-dashboard',
        component: lazyRoute(() => import('../views/TeacherDashboardView.vue')),
        meta: { title: 'Teacher Dashboard' },
      },
      {
        path: 'grades',
        name: 'teacher-grades',
        component: lazyRoute(() => import('../views/teacher/TeacherGradesView.vue')),
        meta: { title: 'Classes' },
      },
      {
        path: 'grades/:courseId',
        name: 'teacher-grade-detail',
        component: lazyRoute(() => import('../views/teacher/TeacherGradeDetailView.vue')),
        props: true,
        meta: { title: 'Class Details' },
      },
      {
        path: 'lessons',
        name: 'teacher-lessons',
        component: lazyRoute(() => import('../views/teacher/TeacherLessonsView.vue')),
        meta: { title: 'Lessons' },
      },
      {
        path: 'courses/:courseId/lessons/:lessonId/preview',
        name: 'teacher-lesson-preview',
        component: lazyRoute(() => import('../views/teacher/TeacherLessonPreviewView.vue')),
        props: true,
        meta: { title: 'Lesson Preview' },
      },
      {
        path: 'courses/:courseId/lessons/:lessonId/edit',
        name: 'teacher-lesson-edit',
        component: lazyRoute(() => import('../views/teacher/TeacherLessonEditView.vue')),
        props: true,
        meta: { title: 'Edit Lesson' },
      },
      {
        path: 'students',
        name: 'teacher-students',
        component: lazyRoute(() => import('../views/teacher/TeacherStudentsView.vue')),
        meta: { title: 'Students' },
      },
      {
        path: 'students/:studentId',
        name: 'teacher-student-profile',
        component: lazyRoute(() => import('../views/teacher/TeacherStudentProfileView.vue')),
        props: true,
        meta: { title: 'Student Profile' },
      },
      {
        path: 'quizzes',
        name: 'teacher-quizzes',
        component: lazyRoute(() => import('../views/teacher/TeacherQuizzesView.vue')),
        meta: { title: 'Quizzes' },
      },
      {
        path: 'quizzes/:courseId/:quizId/edit',
        name: 'teacher-quiz-builder',
        component: lazyRoute(() => import('../views/teacher/TeacherQuizBuilderView.vue')),
        props: true,
        meta: { title: 'Quiz Builder' },
      },
      {
        path: 'quizzes/:courseId/:quizId/results',
        name: 'teacher-quiz-results',
        component: lazyRoute(() => import('../views/teacher/TeacherQuizResultsView.vue')),
        props: true,
        meta: { title: 'Quiz Results' },
      },
      {
        path: 'analytics',
        name: 'teacher-analytics',
        component: lazyRoute(() => import('../views/teacher/TeacherAnalyticsView.vue')),
        meta: { title: 'Analytics' },
      },
      {
        path: 'upload',
        redirect: { name: 'teacher-grades' },
      },
      {
        path: 'messages',
        name: 'teacher-messages',
        component: lazyRoute(() => import('../views/messages/MessagesView.vue')),
        props: { role: 'teacher' },
        meta: { title: 'Messages' },
      },
      {
        path: 'profile',
        name: 'teacher-profile',
        component: lazyRoute(() => import('../views/teacher/TeacherProfileView.vue')),
        meta: { title: 'Profile' },
      },
      {
        path: 'settings',
        name: 'teacher-settings',
        component: lazyRoute(() => import('../views/settings/UserSettingsView.vue')),
        props: { roleLabel: 'Teacher' },
        meta: { title: 'Settings', accountSettings: true },
      },
    ],
  },
  {
    path: '/student',
    component: lazyRoute(() => import('../layouts/StudentLayout.vue')),
    meta: { requiresAuth: true, role: 'student', blockParentViewer: true },
    children: [
      { path: '', redirect: () => ({ name: 'student-dashboard', hash: '#courses' }) },
      {
        path: 'dashboard',
        name: 'student-dashboard',
        component: lazyRoute(() => import('../views/student/StudentDashboardView.vue')),
        meta: { title: 'My Courses' },
        beforeEnter(to) {
          if (!to.hash) {
            return { path: '/student/dashboard', hash: '#courses', replace: true }
          }
          return true
        },
      },
      {
        path: 'course/:id',
        name: 'student-course',
        component: lazyRoute(() => import('../views/student/StudentCourseView.vue')),
        meta: { title: 'Course' },
        props: true,
      },
      {
        path: 'lesson/:id',
        name: 'student-lesson',
        component: lazyRoute(() => import('../views/student/StudentLessonView.vue')),
        meta: { title: 'Learning Session' },
        props: true,
      },
      {
        path: 'messages',
        name: 'student-messages',
        component: lazyRoute(() => import('../views/messages/MessagesView.vue')),
        props: { role: 'student' },
        meta: { title: 'Messages' },
      },
      {
        path: 'profile',
        name: 'student-profile',
        component: lazyRoute(() => import('../views/student/StudentProfileView.vue')),
        meta: { title: 'Profile' },
      },
      {
        path: 'routine',
        name: 'student-routine',
        component: lazyRoute(() => import('../views/student/StudentRoutineView.vue')),
        meta: { title: 'Schedule & Commitment' },
      },
      {
        path: 'planner',
        name: 'student-planner',
        component: lazyRoute(() => import('../views/student/StudentPlannerView.vue')),
        meta: { title: 'Smart Planner' },
      },
      {
        path: 'achievements',
        name: 'student-achievements',
        component: lazyRoute(() => import('../views/student/StudentAchievementsView.vue')),
        meta: { title: 'My Achievements' },
      },
      {
        path: 'manual-quiz/:quizId',
        name: 'student-manual-quiz',
        component: lazyRoute(() => import('../views/student/StudentManualQuizView.vue')),
        props: true,
        meta: { title: 'Quiz' },
      },
      {
        path: 'subscriptions',
        name: 'student-subscriptions',
        component: lazyRoute(() => import('../views/student/StudentSubscriptionsView.vue')),
        meta: { title: 'Subscriptions' },
      },
      {
        path: 'languages',
        name: 'student-languages',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguagesHubView.vue')),
        meta: { title: 'Languages', languageModule: true },
      },
      {
        path: 'languages/subscribe',
        name: 'student-languages-subscribe',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguageSubscribeView.vue')),
        meta: { title: 'Language Subscription', languageModule: true },
      },
      {
        path: 'languages/placement',
        name: 'student-languages-placement',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguagePlacementView.vue')),
        meta: { title: 'Placement Test', languageModule: true },
      },
      {
        path: 'languages/reading',
        name: 'student-languages-reading',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguageReadingView.vue')),
        meta: { title: 'Reading', languageModule: true },
      },
      {
        path: 'languages/listening',
        name: 'student-languages-listening',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguageListeningView.vue')),
        meta: { title: 'Listening', languageModule: true },
      },
      {
        path: 'languages/listening/promotion',
        name: 'student-languages-listening-promotion',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguageListeningPromotionView.vue')),
        meta: { title: 'Listening Promotion', languageModule: true },
      },
      {
        path: 'languages/progress',
        name: 'student-languages-progress',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguageProgressView.vue')),
        meta: { title: 'Progress', languageModule: true },
      },
      {
        path: 'languages/insights',
        name: 'student-languages-insights',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguageInsightsView.vue')),
        meta: { title: 'AI Insights', languageModule: true },
      },
      {
        path: 'languages/curriculum',
        name: 'student-languages-curriculum',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguageCurriculumView.vue')),
        meta: { title: 'Curriculum', languageModule: true },
      },
      {
        path: 'languages/lessons',
        name: 'student-languages-lessons',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguageLessonsView.vue')),
        meta: { title: 'Lessons', languageModule: true },
      },
      {
        path: 'languages/vocabulary',
        name: 'student-languages-vocabulary',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguageVocabularyView.vue')),
        meta: { title: 'Vocabulary', languageModule: true },
      },
      {
        path: 'languages/dictionary',
        name: 'student-languages-dictionary',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguageDictionaryView.vue')),
        meta: { title: 'Dictionary', languageModule: true },
      },
      {
        path: 'languages/writing',
        name: 'student-languages-writing',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguageWritingView.vue')),
        meta: { title: 'Writing', languageModule: true },
      },
      {
        path: 'languages/speaking',
        name: 'student-languages-speaking',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguageSpeakingView.vue')),
        meta: { title: 'Speaking', languageModule: true },
      },
      {
        path: 'languages/certificates',
        name: 'student-languages-certificates',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguageCertificatesView.vue')),
        meta: { title: 'Certificates', languageModule: true },
      },
      {
        path: 'languages/history',
        name: 'student-languages-history',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguageHistoryView.vue')),
        meta: { title: 'History', languageModule: true },
      },
      {
        path: 'languages/exam',
        name: 'student-languages-exam',
        component: lazyRoute(() => import('../views/student/languages/StudentLanguageExamView.vue')),
        meta: { title: 'AI Exam', languageModule: true },
      },
      {
        path: 'settings',
        name: 'student-settings',
        component: lazyRoute(() => import('../views/settings/UserSettingsView.vue')),
        props: { roleLabel: 'Student' },
        meta: { title: 'Settings', accountSettings: true },
      },
    ],
  },
  {
    path: '/parent',
    component: lazyRoute(() => import('../layouts/ParentLayout.vue')),
    meta: { requiresAuth: true, role: 'parent', parentViewer: true },
    children: [
      { path: '', redirect: { name: 'parent-dashboard' } },
      {
        path: 'dashboard',
        name: 'parent-dashboard',
        component: lazyRoute(() => import('../views/parent/ParentDashboardView.vue')),
        meta: { title: 'Overview' },
      },
      {
        path: 'student-performance',
        name: 'parent-performance',
        component: lazyRoute(() => import('../views/parent/ParentPerformanceView.vue')),
        meta: { title: 'Academic Performance' },
      },
      {
        path: 'student-attendance',
        name: 'parent-attendance',
        component: lazyRoute(() => import('../views/parent/ParentAttendanceView.vue')),
        meta: { title: 'Attendance & Study Time' },
      },
      {
        path: 'student-lessons',
        name: 'parent-lessons',
        component: lazyRoute(() => import('../views/parent/ParentLessonsView.vue')),
        meta: { title: 'Lesson Progress' },
      },
      {
        path: 'student-lessons/:lessonId',
        name: 'parent-lesson-detail',
        component: lazyRoute(() => import('../views/parent/ParentLessonDetailView.vue')),
        meta: { title: 'Lesson Details' },
      },
      {
        path: 'student-planner',
        name: 'parent-planner',
        component: lazyRoute(() => import('../views/parent/ParentPlannerView.vue')),
        meta: { title: 'Schedule & Commitment' },
      },
      {
        path: 'student-notifications',
        name: 'parent-notifications',
        component: lazyRoute(() => import('../views/parent/ParentNotificationsView.vue')),
        meta: { title: 'Alerts' },
      },
      {
        path: 'student-insights',
        name: 'parent-insights',
        component: lazyRoute(() => import('../views/parent/ParentInsightsView.vue')),
        meta: { title: 'AI Insights' },
      },
      {
        path: 'student-reports',
        name: 'parent-reports',
        component: lazyRoute(() => import('../views/parent/ParentReportsView.vue')),
        meta: { title: 'Reports & Export' },
      },
      {
        path: 'subjects-teachers',
        name: 'parent-subjects-teachers',
        component: lazyRoute(() => import('../views/parent/ParentSubjectsTeachersView.vue')),
        meta: { title: 'Subjects & Teachers' },
      },
      {
        path: 'link',
        name: 'parent-link',
        component: lazyRoute(() => import('../views/parent/ParentLinkStudentView.vue')),
        meta: { title: 'Link Student' },
      },
      {
        path: 'messages',
        name: 'parent-messages',
        component: lazyRoute(() => import('../views/messages/MessagesView.vue')),
        props: { role: 'parent' },
        meta: { title: 'Messages' },
      },
      {
        path: 'settings',
        name: 'parent-settings',
        component: lazyRoute(() => import('../views/settings/UserSettingsView.vue')),
        props: { roleLabel: 'Parent' },
        meta: { title: 'Settings', accountSettings: true },
      },
    ],
  },
  {
    path: '/admin',
    component: lazyRoute(() => import('../layouts/AdminLayout.vue')),
    meta: { requiresAuth: true, accountSettings: true },
    children: [
      { path: '', redirect: { name: 'admin-settings' } },
      {
        path: 'settings',
        name: 'admin-settings',
        component: lazyRoute(() => import('../views/settings/UserSettingsView.vue')),
        props: { roleLabel: 'Admin' },
        meta: { title: 'Admin Settings', accountSettings: true },
      },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to) {
    if (to.hash) {
      const id = to.hash.replace(/^#/, '')
      const el = id === 'courses' || id === 'journey' ? '#my-subjects' : to.hash
      return { el, behavior: 'smooth', top: 80 }
    }
    return { top: 0, behavior: 'smooth' }
  },
})

router.onError((error) => {
  if (!isChunkLoadError(error)) return
  if (!sessionStorage.getItem(CHUNK_RELOAD_KEY)) {
    sessionStorage.setItem(CHUNK_RELOAD_KEY, '1')
    window.location.reload()
  }
})

function isOnboardingPath(path) {
  return path.startsWith('/student/onboarding')
}

function isPaymentPath(path) {
  return path.startsWith('/student/payment')
}

function isLanguagePath(path) {
  return path.startsWith('/student/languages')
}

function isStudentFlowPath(path) {
  return isOnboardingPath(path) || isPaymentPath(path)
}

const STEP_ORDER = ['grade', 'subjects', 'teachers']

function stepRank(step) {
  const i = STEP_ORDER.indexOf(step || 'grade')
  return i === -1 ? 0 : i
}

async function refreshSessionFlags() {
  if (!isApiMode()) return getSession()
  try {
    const me = await fetchMe()
    const next = mergeUserIntoSession(getSession(), me)
    setSession(next)
    return next
  } catch {
    return getSession()
  }
}

router.beforeEach(async (to) => {
  let session = getSession()
  const isAuth = isApiMode()
    ? !!session?.accessToken
    : !!(session?.accessToken || session?.loggedInAt)

  const fromWelcomeEntry = to.query.entry === 'welcome'

  // Login/register from welcome: always show the form (no skip to onboarding).
  if (to.meta.guest && isAuth && to.name !== 'welcome' && !fromWelcomeEntry) {
    if (isApiMode()) session = await refreshSessionFlags()
    return resolvePostAuthRoute({
      role: session.role,
      viewer_mode: session.viewerMode,
      onboarding_complete: session.onboardingComplete,
      needs_payment: session.needsPayment,
      teacher_setup_complete: session.teacherSetupComplete,
      onboarding_step: session.onboardingStep,
    })
  }

  if ((to.meta.requiresAuth || isStudentFlowPath(to.path)) && !isAuth) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (isStudentFlowPath(to.path) && isAuth && session?.role && session.role !== 'student') {
    return resolvePostAuthRoute({
      role: session.role,
      teacher_setup_complete: session.teacherSetupComplete,
    })
  }

  const needsFreshFlags =
    isAuth &&
    isApiMode() &&
    (to.meta.requiresAuth || to.meta.onboardingFlow || to.meta.paymentFlow || to.meta.teacherSetup)

  if (needsFreshFlags) {
    session = await refreshSessionFlags()
  }

  if (to.meta.parentViewer && !isParentViewer()) {
    return resolvePostAuthRoute({ role: session?.role, viewer_mode: session?.viewerMode })
  }

  if (to.meta.blockParentViewer && isParentViewer()) {
    return { name: 'parent-dashboard' }
  }

  if (to.meta.role && session?.role !== to.meta.role && !isParentViewer()) {
    return resolvePostAuthRoute({
      role: session?.role,
      onboarding_complete: session?.onboardingComplete,
      needs_payment: session?.needsPayment,
      teacher_setup_complete: session?.teacherSetupComplete,
      onboarding_step: session.onboardingStep,
    })
  }

  if (session?.role === 'teacher' && isAuth && !isParentViewer() && !to.meta.accountSettings) {
    if (!session.teacherSetupComplete && !to.meta.teacherSetup) {
      return ROUTES.TEACHER_SETUP
    }
    if (to.meta.teacherSetup && session.teacherSetupComplete) {
      return ROUTES.TEACHER_DASHBOARD
    }
  }

  // Student onboarding/payment enforcement — NEVER on welcome/login/register.
  if (
    session?.role === 'student' &&
    isAuth &&
    !isParentViewer() &&
    !isPublicEntryRoute(to) &&
    !to.meta.accountSettings
  ) {
    const currentStep = session.onboardingStep || 'grade'

    if (to.meta.onboardingStep && stepRank(currentStep) < stepRank(to.meta.onboardingStep)) {
      return onboardingRouteForSession(session)
    }

    if (!session.onboardingComplete && !isOnboardingPath(to.path)) {
      return onboardingRouteForSession(session)
    }
    if (session.onboardingComplete && session.needsPayment && !isPaymentPath(to.path)) {
      return ROUTES.STUDENT_PAYMENT
    }
    if (isOnboardingPath(to.path) && session.onboardingComplete && session.needsPayment) {
      return ROUTES.STUDENT_PAYMENT
    }
    if (isPaymentPath(to.path) && session.paymentComplete && to.name !== 'student-payment-success') {
      return ROUTES.STUDENT_COURSES
    }
    if (
      isOnboardingPath(to.path) &&
      session.onboardingComplete &&
      !session.needsPayment &&
      !(to.name === 'onboarding-grade' && !session.grade)
    ) {
      return ROUTES.STUDENT_COURSES
    }
  }

  if (
    session?.role === 'student' &&
    isAuth &&
    isApiMode() &&
    to.meta.languageModule
  ) {
    let langAccess
    try {
      langAccess = await fetchLanguageAccess()
    } catch {
      if (to.name !== 'student-languages') {
        return ROUTES.STUDENT_LANGUAGES
      }
      return
    }

    const subscribed = langAccess.subscribed
    const placementDone = langAccess.placement_completed
    const routeName = to.name

    if (routeName === 'student-languages-subscribe') {
      if (subscribed) {
        return placementDone ? ROUTES.STUDENT_LANGUAGES : ROUTES.STUDENT_LANGUAGES_EXAM
      }
      return
    }

    if (!subscribed) {
      return ROUTES.STUDENT_LANGUAGES_SUBSCRIBE
    }

    // The interactive AI exam is the entry assessment. Let it (and the hub) through; the legacy
    // placement page stays reachable directly but is no longer the forced gate.
    if (
      routeName === 'student-languages-exam' ||
      routeName === 'student-languages-placement' ||
      routeName === 'student-languages'
    ) {
      return
    }

    if (!placementDone) {
      return ROUTES.STUDENT_LANGUAGES_EXAM
    }
  }
})

router.afterEach((to) => {
  sessionStorage.removeItem(CHUNK_RELOAD_KEY)
  document.title = to.meta.title ? `${to.meta.title} | EduSpark` : 'EduSpark — منصة التعليم الذكي'
})

export default router
