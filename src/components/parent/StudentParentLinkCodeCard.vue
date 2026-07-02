<template>
  <v-card class="glass-card pa-6 mb-6" variant="flat">
    <div class="d-flex align-center gap-2 mb-2">
      <v-icon color="warning">mdi-account-child-circle</v-icon>
      <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.studentLinkCode.title') }}</h3>
    </div>
    <p class="text-body-2 text-medium-emphasis mb-4">
      {{ t('parent.studentLinkCode.hint') }}
    </p>

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg">
      {{ loadError }}
    </v-alert>

    <div v-if="loading" class="d-flex justify-center py-4">
      <v-progress-circular indeterminate color="primary" size="32" />
    </div>

    <template v-else-if="linkCode">
      <div class="code-display d-flex align-center justify-space-between flex-wrap gap-3 pa-4 rounded-lg mb-3">
        <span class="text-h5 font-weight-bold tracking-wide">{{ linkCode }}</span>
        <v-btn
          variant="tonal"
          color="primary"
          prepend-icon="mdi-content-copy"
          @click="copyCode"
        >
          {{ t('parent.studentLinkCode.copy') }}
        </v-btn>
      </div>
      <v-snackbar v-model="copied" color="success" timeout="2000">{{ t('parent.studentLinkCode.copied') }}</v-snackbar>
    </template>

    <v-btn
      v-else
      variant="outlined"
      color="primary"
      :loading="loading"
      @click="loadCode"
    >
      {{ t('parent.studentLinkCode.generate') }}
    </v-btn>
  </v-card>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchStudentLinkCode } from '../../api/parent.js'
import { getErrorMessage } from '../../api/client.js'
import { isApiMode } from '../../utils/session.js'

const { t } = useI18n()

const linkCode = ref('')
const loading = ref(false)
const loadError = ref('')
const copied = ref(false)

async function loadCode() {
  if (!isApiMode()) {
    loadError.value = t('parent.studentLinkCode.requiresServer')
    return
  }
  loading.value = true
  loadError.value = ''
  try {
    linkCode.value = await fetchStudentLinkCode()
  } catch (err) {
    loadError.value = getErrorMessage(err, t('parent.studentLinkCode.fetchError'))
  } finally {
    loading.value = false
  }
}

async function copyCode() {
  if (!linkCode.value) return
  try {
    await navigator.clipboard.writeText(linkCode.value)
    copied.value = true
  } catch {
    loadError.value = t('parent.studentLinkCode.copyError')
  }
}

onMounted(() => loadCode())
</script>

<style scoped>
.code-display {
  background: rgba(124, 108, 240, 0.1);
  border: 1px dashed rgba(124, 108, 240, 0.35);
}

.tracking-wide {
  letter-spacing: 0.12em;
}
</style>
