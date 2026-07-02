<template>
  <div class="verify-page page-container">
    <v-card class="verify-card glass-card mx-auto pa-8" max-width="560" variant="flat">
      <div class="text-center mb-6">
        <v-icon size="56" :color="statusColor">{{ statusIcon }}</v-icon>
        <h1 class="text-h5 font-weight-bold mt-3 mb-1">{{ t('auth.verifyCertificate.title') }}</h1>
        <p class="text-body-2 text-medium-emphasis mb-0 font-mono">{{ certificateNumber }}</p>
      </div>

      <div v-if="loading" class="py-6">
        <v-progress-linear indeterminate color="secondary" rounded />
      </div>

      <v-alert v-else-if="loadError" type="error" variant="tonal" class="rounded-lg">
        {{ loadError }}
      </v-alert>

      <template v-else-if="result">
        <v-alert :type="result.valid ? 'success' : 'error'" variant="tonal" class="rounded-lg mb-6">
          {{ result.valid ? t('auth.verifyCertificate.valid') : t('auth.verifyCertificate.invalid') }}
        </v-alert>

        <v-list v-if="result.valid" lines="two" class="bg-transparent">
          <v-list-item>
            <v-list-item-title class="text-caption text-medium-emphasis">
              {{ t('auth.verifyCertificate.studentName') }}
            </v-list-item-title>
            <v-list-item-subtitle class="text-body-1">{{ result.student_name }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item>
            <v-list-item-title class="text-caption text-medium-emphasis">
              {{ t('auth.verifyCertificate.level') }}
            </v-list-item-title>
            <v-list-item-subtitle class="text-body-1">{{ result.certificate_level }}</v-list-item-subtitle>
          </v-list-item>
          <v-list-item>
            <v-list-item-title class="text-caption text-medium-emphasis">
              {{ t('auth.verifyCertificate.issuedAt') }}
            </v-list-item-title>
            <v-list-item-subtitle class="text-body-1">{{ formatDate(result.issued_at) }}</v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </template>
    </v-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { verifyLanguageCertificate } from '../api/language.js'

const { t, locale } = useI18n()
const route = useRoute()
const loading = ref(true)
const loadError = ref('')
const result = ref(null)

const certificateNumber = computed(() => route.params.certificateNumber || '')

const statusColor = computed(() => {
  if (loading.value) return 'secondary'
  if (!result.value?.valid) return 'error'
  return 'success'
})

const statusIcon = computed(() => {
  if (loading.value) return 'mdi-certificate'
  if (!result.value?.valid) return 'mdi-close-circle'
  return 'mdi-check-decagram'
})

function formatDate(value) {
  if (!value) return '—'
  const dateLocale = locale.value === 'ar' ? 'ar-SA' : 'en-US'
  return new Date(value).toLocaleDateString(dateLocale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    result.value = await verifyLanguageCertificate(certificateNumber.value)
  } catch (err) {
    loadError.value = err.response?.data?.detail || err.message || t('auth.verifyCertificate.verifyFailed')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.verify-page {
  min-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding-top: 2rem;
  padding-bottom: 2rem;
}

.font-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}
</style>
