<template>
  <AuthShell
    :subtitle="t('auth.twoFactor.subtitle')"
    :footer-link="loginFooterLink"
  >
    <template #brand>
      <EduSparkLogo size="auth" class="mb-2" />
    </template>

    <div v-if="!challengeToken" class="text-center py-4">
      <v-icon size="48" color="error" class="mb-3">mdi-shield-off-outline</v-icon>
      <p class="text-body-1 mb-4">{{ t('auth.twoFactor.invalidSession') }}</p>
      <v-btn :to="ROUTES.LOGIN" color="primary" variant="flat" rounded="lg">
        {{ t('auth.footer.login') }}
      </v-btn>
    </div>

    <v-form v-else @submit.prevent="handleVerify">
      <v-alert type="info" variant="tonal" density="comfortable" class="mb-4 rounded-lg">
        {{ t('auth.twoFactor.codeSent', { email: maskedEmail || t('auth.twoFactor.emailFallback') }) }}
      </v-alert>

      <div class="countdown-row mb-4">
        <v-icon size="18" class="me-1">mdi-timer-outline</v-icon>
        <span v-if="secondsLeft > 0" class="text-body-2">
          {{ t('auth.twoFactor.expiresIn', { time: formattedCountdown }) }}
        </span>
        <span v-else class="text-body-2 text-warning">{{ t('auth.twoFactor.expired') }}</span>
      </div>

      <v-otp-input
        v-model="code"
        length="6"
        type="number"
        class="mb-4 otp-rtl"
        :disabled="submitting"
        @update:model-value="clearError"
      />

      <v-alert
        v-if="submitError"
        type="error"
        variant="tonal"
        density="compact"
        class="mb-4 rounded-lg"
      >
        {{ submitError }}
      </v-alert>

      <v-btn
        type="submit"
        size="x-large"
        block
        rounded="lg"
        class="btn-glow mb-3"
        :loading="submitting"
        :disabled="code.length !== 6"
      >
        {{ t('auth.twoFactor.submit') }}
      </v-btn>

      <v-btn
        variant="text"
        block
        rounded="lg"
        :loading="resending"
        :disabled="resendCooldown > 0"
        @click="handleResend"
      >
        {{
          resendCooldown > 0
            ? t('auth.twoFactor.resendCooldown', { seconds: resendCooldown })
            : t('auth.twoFactor.resend')
        }}
      </v-btn>
    </v-form>
  </AuthShell>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AuthShell from '../components/auth/AuthShell.vue'
import EduSparkLogo from '../components/auth/EduSparkLogo.vue'
import { resendTwoFactorCodeApi, verifyTwoFactorLoginApi } from '../api/auth.js'
import { getErrorMessage } from '../api/client.js'
import { useAuth } from '../composables/useAuth.js'
import { ROUTES } from '../constants/app.js'

const TWO_FA_SESSION_KEY = 'eduspark_2fa_pending'

const { t } = useI18n()
const router = useRouter()
const { completeTwoFactorLogin } = useAuth()

const challengeToken = ref('')
const maskedEmail = ref('')
const selectedRole = ref(null)
const code = ref('')
const submitting = ref(false)
const resending = ref(false)
const submitError = ref('')
const secondsLeft = ref(0)
const resendCooldown = ref(0)

let countdownTimer = null
let resendTimer = null

const loginFooterLink = computed(() => ({
  text: t('auth.footer.backTo'),
  label: t('auth.footer.login'),
  to: ROUTES.LOGIN,
}))

const formattedCountdown = computed(() => {
  const m = Math.floor(secondsLeft.value / 60)
  const s = secondsLeft.value % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

function loadPending() {
  try {
    const raw = sessionStorage.getItem(TWO_FA_SESSION_KEY)
    if (!raw) return
    const data = JSON.parse(raw)
    challengeToken.value = data.challengeToken || ''
    maskedEmail.value = data.maskedEmail || ''
    selectedRole.value = data.selectedRole || null
    secondsLeft.value = Number(data.expiresInSeconds) || 600
    resendCooldown.value = Number(data.resendAvailableInSeconds) || 0
  } catch {
    challengeToken.value = ''
  }
}

function savePending(patch = {}) {
  const current = {
    challengeToken: challengeToken.value,
    maskedEmail: maskedEmail.value,
    selectedRole: selectedRole.value,
    expiresInSeconds: secondsLeft.value,
    resendAvailableInSeconds: resendCooldown.value,
    ...patch,
  }
  sessionStorage.setItem(TWO_FA_SESSION_KEY, JSON.stringify(current))
}

function clearPending() {
  sessionStorage.removeItem(TWO_FA_SESSION_KEY)
}

function startCountdown() {
  clearInterval(countdownTimer)
  countdownTimer = setInterval(() => {
    if (secondsLeft.value > 0) secondsLeft.value -= 1
  }, 1000)
}

function startResendCooldown(seconds) {
  resendCooldown.value = seconds
  clearInterval(resendTimer)
  resendTimer = setInterval(() => {
    if (resendCooldown.value > 0) resendCooldown.value -= 1
    else clearInterval(resendTimer)
  }, 1000)
}

function clearError() {
  submitError.value = ''
}

async function handleVerify() {
  if (code.value.length !== 6) return
  submitting.value = true
  submitError.value = ''
  try {
    const data = await verifyTwoFactorLoginApi({
      challengeToken: challengeToken.value,
      code: code.value,
    })
    clearPending()
    await completeTwoFactorLogin(data, selectedRole.value)
  } catch (err) {
    submitError.value = getErrorMessage(err, t('auth.twoFactor.errors.invalidCode'))
  } finally {
    submitting.value = false
  }
}

async function handleResend() {
  if (resendCooldown.value > 0) return
  resending.value = true
  submitError.value = ''
  try {
    const result = await resendTwoFactorCodeApi(challengeToken.value)
    secondsLeft.value = result.expires_in_seconds || 600
    savePending({ expiresInSeconds: secondsLeft.value })
    startResendCooldown(result.resend_available_in_seconds || 60)
    showResendSuccess()
  } catch (err) {
    submitError.value = getErrorMessage(err, t('auth.twoFactor.errors.resendFailed'))
  } finally {
    resending.value = false
  }
}

function showResendSuccess() {
  submitError.value = ''
}

onMounted(() => {
  loadPending()
  if (!challengeToken.value) return
  startCountdown()
  if (resendCooldown.value > 0) startResendCooldown(resendCooldown.value)
})

onUnmounted(() => {
  clearInterval(countdownTimer)
  clearInterval(resendTimer)
  savePending()
})
</script>

<style scoped>
.countdown-row {
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.75);
}

.otp-rtl :deep(input) {
  direction: ltr;
  text-align: center;
}
</style>
