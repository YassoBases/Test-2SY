import { api } from './client.js'
import { VIEWER_PARENT } from '../utils/session.js'

/** Map FastAPI TokenResponse (snake_case) to app session shape. */
export function normalizeAuthResponse(data) {
  if (data?.requires_2fa) {
    return {
      requires2fa: true,
      challengeToken: data.challenge_token ?? null,
      expiresInSeconds: data.expires_in_seconds ?? null,
      maskedEmail: data.masked_email ?? null,
      resendAvailableInSeconds: data.resend_available_in_seconds ?? 60,
    }
  }
  if (!data?.user) {
    throw new Error('استجابة غير صالحة من الخادم')
  }
  const viewerMode = data.viewer_mode ?? data.user?.viewer_mode ?? null
  const user = {
    ...data.user,
    viewer_mode: viewerMode,
  }
  return {
    accessToken: data.access_token ?? data.accessToken ?? null,
    refreshToken: data.refresh_token ?? data.refreshToken ?? null,
    sessionId: data.session_id ?? data.sessionId ?? null,
    user,
    viewerMode,
  }
}

export async function logoutApi(refreshToken) {
  const body = refreshToken ? { refresh_token: refreshToken } : {}
  await api.post('/auth/logout', body)
}

export async function fetchAuthSessions() {
  const { data } = await api.get('/auth/sessions')
  return data
}

export async function revokeAuthSession(sessionId) {
  await api.delete(`/auth/sessions/${sessionId}`)
}

export async function revokeAllAuthSessions() {
  await api.delete('/auth/sessions')
}

export async function fetchMe() {
  const { data } = await api.get('/auth/me')
  return data
}

export async function fetchAccountSecurity() {
  const { data } = await api.get('/auth/account')
  return data
}

export async function changePasswordApi({ currentPassword, newPassword, confirmPassword }) {
  const { data } = await api.post('/auth/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
    confirm_password: confirmPassword,
  })
  return data
}

export async function changeEmailApi({ newEmail, currentPassword }) {
  const { data } = await api.post('/auth/change-email', {
    new_email: String(newEmail).trim().toLowerCase(),
    current_password: currentPassword,
  })
  return data
}

export async function loginApi({ email, password, viewerMode }) {
  const body = {
    email: String(email).trim().toLowerCase(),
    password,
  }
  if (viewerMode === VIEWER_PARENT) {
    body.viewer_mode = VIEWER_PARENT
  }
  const { data } = await api.post('/auth/login', body)
  return normalizeAuthResponse(data)
}

export async function registerApi({ name, email, password, role }) {
  const { data } = await api.post('/auth/register', {
    name: name.trim(),
    email: String(email).trim().toLowerCase(),
    password,
    role,
  })
  return normalizeAuthResponse(data)
}

export async function forgotPasswordApi(email) {
  const { data } = await api.post('/auth/forgot-password', {
    email: String(email).trim().toLowerCase(),
  })
  return data
}

export async function resetPasswordApi({ token, newPassword, confirmPassword }) {
  const { data } = await api.post('/auth/reset-password', {
    token,
    new_password: newPassword,
    confirm_password: confirmPassword,
  })
  return data
}

export async function verifyEmailApi(token) {
  const { data } = await api.post('/auth/verify-email', { token })
  return data
}

export async function resendVerificationApi() {
  const { data } = await api.post('/auth/resend-verification')
  return data
}

export async function verifyTwoFactorLoginApi({ challengeToken, code }) {
  const { data } = await api.post('/auth/verify-2fa', {
    challenge_token: challengeToken,
    code,
  })
  return normalizeAuthResponse(data)
}

export async function resendTwoFactorCodeApi(challengeToken) {
  const { data } = await api.post('/auth/resend-2fa', {
    challenge_token: challengeToken,
  })
  return data
}

export async function requestEnableTwoFactorApi(password) {
  const { data } = await api.post('/auth/2fa/enable', { password })
  return data
}

export async function confirmEnableTwoFactorApi({ challengeToken, code }) {
  const { data } = await api.post('/auth/2fa/enable/confirm', {
    challenge_token: challengeToken,
    code,
  })
  return data
}

export async function disableTwoFactorApi(password) {
  const { data } = await api.post('/auth/2fa/disable', { password })
  return data
}
