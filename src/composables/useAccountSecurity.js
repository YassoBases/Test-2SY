import { ref } from 'vue'
import {
  changeEmailApi,
  changePasswordApi,
  confirmEnableTwoFactorApi,
  disableTwoFactorApi,
  fetchAccountSecurity,
  requestEnableTwoFactorApi,
  resendVerificationApi,
} from '../api/auth.js'
import { getErrorMessage } from '../api/client.js'
import { getSession, setSession } from '../utils/session.js'
import { mergeUserIntoSession } from '../utils/studentFlow.js'

const ROLE_LABELS = {
  teacher: 'معلم',
  student: 'طالب',
  parent: 'ولي أمر',
  admin: 'مسؤول',
}

export function useAccountSecurity() {
  const account = ref(null)
  const loading = ref(false)
  const savingEmail = ref(false)
  const savingPassword = ref(false)
  const resendingVerification = ref(false)
  const enablingTwoFactor = ref(false)
  const confirmingTwoFactor = ref(false)
  const disablingTwoFactor = ref(false)
  const twoFactorChallenge = ref(null)

  async function loadAccount() {
    loading.value = true
    try {
      account.value = await fetchAccountSecurity()
    } finally {
      loading.value = false
    }
  }

  function roleLabel(role) {
    return ROLE_LABELS[role] || role || '—'
  }

  function formatCreatedAt(value) {
    if (!value) return '—'
    try {
      return new Date(value).toLocaleDateString('ar-SY', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    } catch {
      return '—'
    }
  }

  function syncSessionUser(user) {
    const session = getSession()
    if (!session || !user) return
    setSession(mergeUserIntoSession(session, user))
  }

  async function changeEmail({ newEmail, currentPassword }) {
    savingEmail.value = true
    try {
      const user = await changeEmailApi({ newEmail, currentPassword })
      syncSessionUser(user)
      account.value = {
        ...account.value,
        email: user.email,
        email_verified: user.email_verified ?? false,
        email_verified_at: user.email_verified_at ?? null,
      }
      return user
    } catch (err) {
      throw new Error(getErrorMessage(err, 'تعذر تغيير البريد'))
    } finally {
      savingEmail.value = false
    }
  }

  async function changePassword({ currentPassword, newPassword, confirmPassword }) {
    savingPassword.value = true
    try {
      const user = await changePasswordApi({ currentPassword, newPassword, confirmPassword })
      syncSessionUser(user)
      return user
    } catch (err) {
      throw new Error(getErrorMessage(err, 'تعذر تغيير كلمة المرور'))
    } finally {
      savingPassword.value = false
    }
  }

  async function resendVerification() {
    resendingVerification.value = true
    try {
      const result = await resendVerificationApi()
      await loadAccount()
      return result
    } catch (err) {
      throw new Error(getErrorMessage(err, 'تعذر إرسال رسالة التأكيد'))
    } finally {
      resendingVerification.value = false
    }
  }

  async function requestEnableTwoFactor(password) {
    enablingTwoFactor.value = true
    try {
      const result = await requestEnableTwoFactorApi(password)
      twoFactorChallenge.value = {
        challengeToken: result.challenge_token,
        maskedEmail: result.masked_email,
        expiresInSeconds: result.expires_in_seconds,
      }
      return result
    } catch (err) {
      throw new Error(getErrorMessage(err, 'تعذر بدء تفعيل المصادقة الثنائية'))
    } finally {
      enablingTwoFactor.value = false
    }
  }

  async function confirmEnableTwoFactor(code) {
    if (!twoFactorChallenge.value?.challengeToken) {
      throw new Error('جلسة التفعيل غير صالحة')
    }
    confirmingTwoFactor.value = true
    try {
      const result = await confirmEnableTwoFactorApi({
        challengeToken: twoFactorChallenge.value.challengeToken,
        code,
      })
      twoFactorChallenge.value = null
      await loadAccount()
      return result
    } catch (err) {
      throw new Error(getErrorMessage(err, 'رمز التفعيل غير صحيح'))
    } finally {
      confirmingTwoFactor.value = false
    }
  }

  async function disableTwoFactor(password) {
    disablingTwoFactor.value = true
    try {
      const result = await disableTwoFactorApi(password)
      twoFactorChallenge.value = null
      await loadAccount()
      return result
    } catch (err) {
      throw new Error(getErrorMessage(err, 'تعذر إيقاف المصادقة الثنائية'))
    } finally {
      disablingTwoFactor.value = false
    }
  }

  function cancelTwoFactorSetup() {
    twoFactorChallenge.value = null
  }

  return {
    account,
    loading,
    savingEmail,
    savingPassword,
    resendingVerification,
    enablingTwoFactor,
    confirmingTwoFactor,
    disablingTwoFactor,
    twoFactorChallenge,
    loadAccount,
    roleLabel,
    formatCreatedAt,
    changeEmail,
    changePassword,
    resendVerification,
    requestEnableTwoFactor,
    confirmEnableTwoFactor,
    disableTwoFactor,
    cancelTwoFactorSetup,
  }
}
