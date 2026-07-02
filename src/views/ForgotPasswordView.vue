<template>
  <AuthShell
    :subtitle="t('auth.forgotPassword.subtitle')"
    :footer-link="loginFooterLink"
  >
    <template #brand>
      <EduSparkLogo size="auth" class="mb-2" />
    </template>

    <v-alert
      v-if="successMessage"
      type="success"
      variant="tonal"
      density="compact"
      class="mb-4 rounded-lg"
    >
      {{ successMessage }}
    </v-alert>

    <v-form v-else @submit.prevent="handleSubmit">
      <v-text-field
        v-model="email"
        :label="t('auth.fields.email')"
        type="email"
        prepend-inner-icon="mdi-email-outline"
        autocomplete="email"
        :error-messages="errors.email"
        class="mb-4"
        @update:model-value="clearError('email')"
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
        class="btn-glow mb-2"
        :loading="loading"
      >
        {{ t('auth.forgotPassword.submit') }}
      </v-btn>

      <p class="text-caption text-medium-emphasis text-center mb-0">
        {{ t('auth.forgotPassword.privacyNote') }}
      </p>
    </v-form>
  </AuthShell>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AuthShell from '../components/auth/AuthShell.vue'
import EduSparkLogo from '../components/auth/EduSparkLogo.vue'
import { forgotPasswordApi } from '../api/auth.js'
import { getErrorMessage } from '../api/client.js'
import { validateForgotPassword } from '../utils/validate.js'
import { ROUTES } from '../constants/app.js'

const { t } = useI18n()

const loginFooterLink = computed(() => ({
  text: t('auth.footer.rememberPassword'),
  label: t('auth.footer.login'),
  to: ROUTES.LOGIN,
}))

const email = ref('')
const loading = ref(false)
const submitError = ref('')
const successMessage = ref('')
const errors = reactive({})

function clearError(field) {
  delete errors[field]
  submitError.value = ''
}

async function handleSubmit() {
  Object.keys(errors).forEach((k) => delete errors[k])
  const validation = validateForgotPassword({ email: email.value })
  Object.assign(errors, validation)
  if (Object.keys(validation).length) return

  loading.value = true
  submitError.value = ''
  try {
    const result = await forgotPasswordApi(email.value)
    successMessage.value = result.detail || t('auth.forgotPassword.successDefault')
  } catch (err) {
    submitError.value = getErrorMessage(err, t('auth.forgotPassword.errors.sendFailed'))
  } finally {
    loading.value = false
  }
}
</script>
