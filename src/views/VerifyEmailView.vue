<template>
  <AuthShell
    :subtitle="t('auth.verifyEmail.subtitle')"
    :footer-link="loginFooterLink"
  >
    <template #brand>
      <EduSparkLogo size="auth" class="mb-2" />
    </template>

    <div v-if="!token" class="text-center py-4">
      <v-icon size="48" color="error" class="mb-3">mdi-link-off</v-icon>
      <p class="text-body-1 mb-0">{{ t('auth.verifyEmail.invalidToken') }}</p>
    </div>

    <div v-else-if="verifying" class="text-center py-8">
      <v-progress-circular indeterminate color="primary" size="40" class="mb-4" />
      <p class="text-body-1 mb-0">{{ t('auth.verifyEmail.verifying') }}</p>
    </div>

    <v-alert
      v-else-if="successMessage"
      type="success"
      variant="tonal"
      density="comfortable"
      class="rounded-lg"
    >
      {{ successMessage }}
      <div class="mt-3">
        <v-btn :to="ROUTES.LOGIN" color="primary" variant="flat" rounded="lg">
          {{ t('auth.footer.login') }}
        </v-btn>
      </div>
    </v-alert>

    <v-alert
      v-else-if="errorMessage"
      type="error"
      variant="tonal"
      density="comfortable"
      class="rounded-lg"
    >
      {{ errorMessage }}
    </v-alert>
  </AuthShell>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import AuthShell from '../components/auth/AuthShell.vue'
import EduSparkLogo from '../components/auth/EduSparkLogo.vue'
import { verifyEmailApi } from '../api/auth.js'
import { getErrorMessage } from '../api/client.js'
import { ROUTES } from '../constants/app.js'

const { t } = useI18n()
const route = useRoute()
const token = computed(() => String(route.query.token || '').trim())
const verifying = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const loginFooterLink = computed(() => ({
  text: t('auth.footer.backTo'),
  label: t('auth.footer.login'),
  to: ROUTES.LOGIN,
}))

onMounted(async () => {
  if (!token.value) return
  verifying.value = true
  try {
    const result = await verifyEmailApi(token.value)
    successMessage.value = result.detail || t('auth.verifyEmail.successDefault', {
      email: result.email || t('auth.verifyEmail.emailFallback'),
    })
  } catch (err) {
    errorMessage.value = getErrorMessage(err, t('auth.verifyEmail.errors.failed'))
  } finally {
    verifying.value = false
  }
})
</script>
