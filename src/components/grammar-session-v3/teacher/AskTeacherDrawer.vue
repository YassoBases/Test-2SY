<template>
  <div v-if="open" class="ask-drawer" role="dialog" aria-modal="true" :aria-label="t('student.grammarTeacher.ask.title')">
    <div class="ask-drawer__backdrop" @click="$emit('close')" />
    <div class="ask-drawer__panel">
      <header class="ask-drawer__head">
        <h3>{{ t('student.grammarTeacher.ask.title') }}</h3>
        <AppButton variant="ghost" size="small" @click="$emit('close')">
          {{ t('student.grammarTeacher.ask.close') }}
        </AppButton>
      </header>

      <p class="ask-drawer__hint">{{ t('student.grammarTeacher.ask.hint') }}</p>

      <textarea
        v-model="draftProxy"
        class="ask-drawer__input eng-island"
        dir="ltr"
        rows="3"
        :placeholder="t('student.grammarTeacher.ask.placeholder')"
        :disabled="loading"
      />

      <v-alert v-if="error" type="error" variant="tonal" class="mb-2 rounded-lg" density="compact">
        {{ error }}
      </v-alert>

      <div class="ask-drawer__actions">
        <AppButton variant="secondary" :disabled="loading" @click="$emit('close')">
          {{ t('student.grammarTeacher.ask.cancel') }}
        </AppButton>
        <AppButton
          variant="primary"
          :loading="loading"
          prepend-icon="mdi-chat-question-outline"
          @click="$emit('submit')"
        >
          {{ t('student.grammarTeacher.ask.send') }}
        </AppButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AppButton from '../../ui/AppButton.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  draft: { type: String, default: '' },
  error: { type: String, default: '' },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'submit', 'update:draft'])
const { t } = useI18n()

const draftProxy = computed({
  get: () => props.draft,
  set: (v) => emit('update:draft', v),
})
</script>

<style scoped>
.ask-drawer {
  position: fixed;
  inset: 0;
  z-index: 40;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.ask-drawer__backdrop {
  position: absolute;
  inset: 0;
  background: rgba(12, 25, 41, 0.35);
}

.ask-drawer__panel {
  position: relative;
  width: min(560px, 100%);
  padding: 20px;
  border-radius: 20px 20px 0 0;
  background: var(--surface-elevated, #fff);
}

.ask-drawer__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-block-end: 8px;
}

.ask-drawer__head h3 {
  margin: 0;
  font-size: 1.15rem;
}

.ask-drawer__hint {
  margin: 0 0 12px;
  font-size: 0.875rem;
  color: var(--text-muted, #3f4f63);
}

.ask-drawer__input {
  width: 100%;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid color-mix(in srgb, var(--text-muted, #3f4f63) 28%, transparent);
  font: inherit;
  resize: vertical;
  margin-block-end: 12px;
}

.ask-drawer__actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
