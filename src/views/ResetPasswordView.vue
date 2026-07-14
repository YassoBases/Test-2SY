<template>
  <AuthShell
    :subtitle="t('auth.resetPassword.subtitle')"
    :footer-link="loginFooterLink"
  >
    <template #brand>
      <EduSparkLogo size="auth" class="mb-2" />
    </template>

    <v-alert
      v-if="!token"
      type="error"
      variant="tonal"
      density="compact"
      class="mb-4 rounded-lg"
    >
      {{ t('auth.resetPassword.invalidToken') }}
    </v-alert>

    <v-alert
      v-else-if="successMessage"
      type="success"
      variant="tonal"
      density="compact"
      class="mb-4 rounded-lg"
    >
      {{ successMessage }}
      <div class="mt-3">
        <v-btn :to="ROUTES.LOGIN" color="primary" variant="flat" rounded="lg">
          {{ t('auth.footer.login') }}
        </v-btn>
      </div>
    </v-alert>

    <v-form v-else @submit.prevent="handleSubmit">
      <v-text-field
        v-model="newPassword"
        :label="t('auth.fields.newPassword')"
        :type="showNewPassword ? 'text' : 'password'"
        prepend-inner-icon="mdi-lock-outline"
        :append-inner-icon="showNewPassword ? 'mdi-eye-off' : 'mdi-eye'"
        autocomplete="new-password"
        :error-messages="errors.newPassword"
        class="mb-1"
        @click:append-inner="showNewPassword = !showNewPassword"
        @update:model-value="clearError('newPassword')"
      />
      <div v-if="newPassword" class="mb-3">
        <div class="d-flex align-center justify-space-between text-caption mb-1">
          <span class="text-medium-emphasis">{{ t('auth.resetPassword.strengthLabel') }}</span>
          <v-chip size="x-small" :color="strength.color" variant="tonal">
            {{ strength.labelKey ? t(strength.labelKey) : '' }}
          </v-chip>
        </div>
        <v-progress-linear
          :model-value="strengthPercent(newPassword)"
          :color="strength.color"
          height="6"
          rounded
        />
      </div>

      <v-text-field
        v-model="confirmPassword"
        :label="t('auth.fields.confirmNewPassword')"
        :type="showConfirmPassword ? 'text' : 'password'"
        prepend-inner-icon="mdi-lock-check"
        :append-inner-icon="showConfirmPassword ? 'mdi-eye-off' : 'mdi-eye'"
        autocomplete="new-password"
        :error-messages="errors.confirmPassword"
        class="mb-4"
        @click:append-inner="showConfirmPassword = !showConfirmPassword"
        @update:model-value="clearError('confirmPassword')"
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
        class="btn-glow"
        :loading="loading"
      >
        {{ t('auth.resetPassword.submit') }}
      </v-btn>
    </v-form>
  </AuthShell>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AuthShell from '../components/auth/AuthShell.vue'
import EduSparkLogo from '../components/auth/EduSparkLogo.vue'
import { resetPasswordApi } from '../api/auth.js'
import { getErrorMessage } from '../api/client.js'
import { validateResetPassword } from '../utils/validate.js'
import { scorePassword, strengthPercent } from '../utils/passwordStrength.js'
import { ROUTES } from '../constants/app.js'

const { t } = useI18n()
const route = useRoute()

const token = computed(() => String(route.query.token || '').trim())
const newPassword = ref('')
const confirmPassword = ref('')
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const submitError = ref('')
const successMessage = ref('')
const errors = reactive({})

const strength = computed(() => scorePassword(newPassword.value))

const loginFooterLink = computed(() => ({
  text: t('auth.footer.rememberPassword'),
  label: t('auth.footer.login'),
  to: ROUTES.LOGIN,
}))

function clearError(field) {
  delete errors[field]
  submitError.value = ''
}

async function handleSubmit() {
  Object.keys(errors).forEach((k) => delete errors[k])
  const validation = validateResetPassword({
    token: token.value,
    newPassword: newPassword.value,
    confirmPassword: confirmPassword.value,
  })
  Object.assign(errors, validation)
  if (Object.keys(validation).length) return

  loading.value = true
  submitError.value = ''
  try {
    const result = await resetPasswordApi({
      token: token.value,
      newPassword: newPassword.value,
      confirmPassword: confirmPassword.value,
    })
    successMessage.value = result.detail || t('auth.resetPassword.successDefault')
  } catch (err) {
    submitError.value = getErrorMessage(err, t('auth.resetPassword.errors.updateFailed'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-link {
  color: var(--em-cyan);
  text-decoration: none;
}
</style>
