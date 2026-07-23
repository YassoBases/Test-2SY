<template>
  <div class="session-controls">
    <AppButton
      variant="secondary"
      :disabled="!canBack || loading"
      prepend-icon="mdi-arrow-left"
      @click="$emit('back')"
    >
      {{ t('student.grammarSession.controls.back') }}
    </AppButton>

    <AppButton
      v-if="isLast"
      variant="primary"
      size="large"
      :loading="loading"
      prepend-icon="mdi-check"
      @click="$emit('finish')"
    >
      {{ primaryLabel || t('student.grammarSession.controls.finish') }}
    </AppButton>

    <AppButton
      v-else
      variant="primary"
      size="large"
      :disabled="!canNext || loading"
      append-icon="mdi-arrow-right"
      @click="$emit('continue')"
    >
      {{ primaryLabel || t('student.grammarSession.controls.continue') }}
    </AppButton>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import AppButton from '../ui/AppButton.vue'

defineProps({
  canBack: { type: Boolean, default: false },
  canNext: { type: Boolean, default: true },
  isLast: { type: Boolean, default: false },
  primaryLabel: { type: String, default: '' },
  loading: { type: Boolean, default: false },
})

defineEmits(['back', 'next', 'continue', 'finish'])
const { t } = useI18n()
</script>

<style scoped>
.session-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: flex-end;
}
</style>
