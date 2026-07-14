<template>
  <v-snackbar
    v-model="toastState.show"
    :timeout="toastState.timeout"
    location="top"
    class="app-toast"
    :class="`app-toast--${toastState.type}`"
  >
    <div class="d-flex align-center gap-3">
      <v-avatar :color="typeColor" size="36" variant="tonal" class="flex-shrink-0">
        <v-icon :icon="typeIcon" size="20" />
      </v-avatar>
      <span class="app-toast__text">{{ toastState.text }}</span>
    </div>
    <template #actions>
      <v-btn
        variant="text"
        size="small"
        class="text-medium-emphasis"
        @click="toastState.show = false"
      >
        {{ t('common.close') }}
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { toastState } from '../../composables/useToast.js'

const { t } = useI18n()

const meta = {
  success: { icon: 'mdi-check-circle', color: 'success' },
  error: { icon: 'mdi-alert-circle', color: 'error' },
  warning: { icon: 'mdi-alert', color: 'warning' },
  info: { icon: 'mdi-information', color: 'info' },
}

const typeIcon = computed(() => meta[toastState.type]?.icon ?? meta.info.icon)
const typeColor = computed(() => meta[toastState.type]?.color ?? 'info')
</script>

<style scoped>
.app-toast__text {
  line-height: 1.45;
}
</style>
