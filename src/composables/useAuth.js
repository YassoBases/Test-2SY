import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { loginApi, logoutApi, registerApi } from '../api/auth.js'
import { getErrorMessage } from '../api/client.js'
import { getSession, setSession, clearSession, isApiMode, isParentViewer } from '../utils/session.js'
import { ROUTES } from '../constants/app.js'
import { mergeUserIntoSession, resolvePostAuthRoute, safeAuthRedirect } from '../utils/studentFlow.js'
import { ensureTeacherProfile, invalidateTeacherProfileCache } from './useTeacherProfile.js'

const TWO_FA_SESSION_KEY = 'eduspark_2fa_pending'

export function useAuth() {
  const router = useRouter()
  const route = useRoute()

  const session = computed(() => getSession())
  const isAuthenticated = computed(() =>
    isApiMode()
      ? !!session.value?.accessToken
      : !!(session.value?.accessToken || session.value?.loggedInAt),
  )
  const user = computed(() => session.value)
  const role = computed(() => session.value?.role ?? null)
  const viewerMode = computed(() => session.value?.viewerMode ?? null)
  const isParentMode = computed(() => isParentViewer())

  async function persistAndRedirect(
    { user: u, accessToken, refreshToken, sessionId, viewerMode: vm },
    selectedRole,
    { isRegistration = false } = {},
  ) {
    if (!u?.email) {
      throw new Error('استجابة غير صالحة من الخادم')
    }

    if (selectedRole && u.role && u.role !== selectedRole) {
      const roleLabels = { teacher: 'معلم', student: 'طالب', parent: 'ولي أمر' }
      throw new Error(
        `هذا الحساب لـ${roleLabels[u.role] || u.role}. اختر نوع الحساب الصحيح عند تسجيل الدخول.`,
      )
    }

    if (!accessToken) {
      throw new Error('لم يُرجع الخادم رمز الدخول')
    }

    const merged = mergeUserIntoSession(
      {
        email: u.email,
        name: u.name,
        role: u.role,
        viewerMode: vm || null,
        accessToken,
        refreshToken: refreshToken || null,
        sessionId: sessionId || null,
        loggedInAt: new Date().toISOString(),
      },
      u,
    )
    setSession(merged)

    if (u.role === 'teacher') {
      await ensureTeacherProfile()
    }

    if (u.role === 'parent') {
      if (isRegistration) {
        return router.push(ROUTES.PARENT_LINK)
      }
      return router.push(ROUTES.PARENT_DASHBOARD)
    }

    if (isRegistration && u.role === 'student') {
      return router.push(ROUTES.ONBOARDING_GRADE)
    }

    const resume = safeAuthRedirect(route.query.redirect, u)
    return router.push(resume || resolvePostAuthRoute(u))
  }

  async function login({ email, password, name, role: userRole }) {
    if (isApiMode()) {
      clearSession()
      invalidateTeacherProfileCache()
      const data = await loginApi({ email, password })
      if (data.requires2fa) {
        sessionStorage.setItem(
          TWO_FA_SESSION_KEY,
          JSON.stringify({
            challengeToken: data.challengeToken,
            maskedEmail: data.maskedEmail,
            expiresInSeconds: data.expiresInSeconds,
            resendAvailableInSeconds: data.resendAvailableInSeconds,
            selectedRole: userRole,
          }),
        )
        await router.push(ROUTES.LOGIN_VERIFY_2FA)
        return
      }
      await persistAndRedirect(data, userRole)
      return
    }
    setSession({
      email: email.trim(),
      name: name || email.split('@')[0],
      role: userRole,
      loggedInAt: new Date().toISOString(),
    })
    if (userRole === 'parent') await router.push(ROUTES.PARENT_DASHBOARD)
    else if (userRole === 'teacher') await router.push(ROUTES.TEACHER_DASHBOARD)
    else await router.push(ROUTES.ONBOARDING_GRADE)
  }

  async function register({ name, email, password, role: userRole }) {
    if (isApiMode()) {
      clearSession()
      invalidateTeacherProfileCache()
      const data = await registerApi({ name, email, password, role: userRole })
      await persistAndRedirect(data, userRole, { isRegistration: true })
      return
    }
    setSession({
      email: email.trim(),
      name: name.trim(),
      role: userRole,
      accessToken: 'mock-token',
      onboardingComplete: false,
      needsPayment: false,
      paymentComplete: false,
      onboardingStep: 'grade',
      registeredAt: new Date().toISOString(),
    })
    if (userRole === 'teacher') await router.push(ROUTES.TEACHER_DASHBOARD)
    else if (userRole === 'parent') await router.push(ROUTES.PARENT_LINK)
    else await router.push(ROUTES.ONBOARDING_GRADE)
  }

  async function completeTwoFactorLogin(data, selectedRole) {
    await persistAndRedirect(data, selectedRole)
  }

  async function logout() {
    if (isApiMode()) {
      try {
        await logoutApi(session.value?.refreshToken)
      } catch {
        /* session may already be revoked */
      }
    }
    clearSession()
    invalidateTeacherProfileCache()
    router.push(ROUTES.LOGIN)
  }

  return {
    session,
    isAuthenticated,
    user,
    role,
    viewerMode,
    isParentMode,
    login,
    completeTwoFactorLogin,
    register,
    logout,
    getErrorMessage,
  }
}
