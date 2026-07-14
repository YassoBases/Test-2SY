import { ROUTES } from '../constants/app.js'
import { isPersonalizationSetupComplete } from './personalizationSetup.js'

function readFlag(patch, session, snakeKey, camelKey) {
  if (!patch) return session?.[camelKey]
  if (Object.prototype.hasOwnProperty.call(patch, snakeKey)) return patch[snakeKey]
  if (Object.prototype.hasOwnProperty.call(patch, camelKey)) return patch[camelKey]
  return session?.[camelKey]
}

export function mergeUserIntoSession(session, patch) {
  if (!patch) return session
  return {
    ...session,
    id: patch.id ?? session?.id,
    name: patch.name ?? session?.name,
    email: patch.email ?? session?.email,
    role: patch.role ?? session?.role,
    onboardingComplete: readFlag(patch, session, 'onboarding_complete', 'onboardingComplete'),
    needsPayment: readFlag(patch, session, 'needs_payment', 'needsPayment'),
    paymentComplete: readFlag(patch, session, 'payment_complete', 'paymentComplete'),
    teacherSetupComplete: readFlag(patch, session, 'teacher_setup_complete', 'teacherSetupComplete'),
    onboardingStep: readFlag(patch, session, 'onboarding_step', 'onboardingStep') ?? 'grade',
    grade: patch.grade ?? session?.grade ?? null,
  }
}

export function resolvePostAuthRoute(user) {
  if (!user) return ROUTES.LOGIN
  if (user.viewer_mode === 'parent' || user.viewerMode === 'parent') {
    return ROUTES.PARENT_DASHBOARD
  }
  if (user.role === 'parent') {
    return ROUTES.PARENT_DASHBOARD
  }
  if (user.role === 'teacher') {
    const setupDone = user.teacher_setup_complete ?? user.teacherSetupComplete
    return setupDone ? ROUTES.TEACHER_DASHBOARD : ROUTES.TEACHER_SETUP
  }
  if (user.role === 'student') {
    const onboardingDone = user.onboarding_complete ?? user.onboardingComplete
    const needsPayment = user.needs_payment ?? user.needsPayment
    if (!onboardingDone) {
      const step = user.onboarding_step || user.onboardingStep || 'grade'
      if (step !== 'grade' && !isPersonalizationSetupComplete()) {
        return ROUTES.ONBOARDING_PERSONALIZE
      }
      if (step === 'teachers') return ROUTES.ONBOARDING_TEACHERS
      if (step === 'subjects') return ROUTES.ONBOARDING_SUBJECTS
      return ROUTES.ONBOARDING_GRADE
    }
    if (needsPayment) return ROUTES.STUDENT_PAYMENT
    return ROUTES.STUDENT_COURSES
  }
  return ROUTES.STUDENT_COURSES
}

/** Resume a post-login path only when it matches the user's flow state. */
export function safeAuthRedirect(path, user) {
  if (!path || typeof path !== 'string' || !path.startsWith('/') || path.startsWith('//')) {
    return null
  }
  if (user?.role !== 'student') return null
  return null
}

export function onboardingRouteForSession(session) {
  if (!session?.onboardingComplete) {
    const step = session?.onboardingStep || 'grade'
    if (step !== 'grade' && session?.grade && !isPersonalizationSetupComplete()) {
      return ROUTES.ONBOARDING_PERSONALIZE
    }
    if (step === 'teachers') return ROUTES.ONBOARDING_TEACHERS
    if (step === 'subjects') return ROUTES.ONBOARDING_SUBJECTS
    return ROUTES.ONBOARDING_GRADE
  }
  if (session?.needsPayment) return ROUTES.STUDENT_PAYMENT
  return ROUTES.STUDENT_COURSES
}

export function isPublicEntryRoute(to) {
  return to.meta.guest === true
}
