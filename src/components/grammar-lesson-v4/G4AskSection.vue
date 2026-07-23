<template>
  <section class="g4-section" aria-labelledby="g4-ask-title">
    <h2 id="g4-ask-title" class="g4-section__title">
      {{ t('student.grammarV4.ask.title') }}
    </h2>
    <p class="g4-section__sub">
      {{ t('student.grammarV4.ask.subtitle', { topic: topic || '—' }) }}
    </p>

    <div class="chat" role="log" aria-live="polite">
      <div v-if="!messages.length" class="chat__empty">
        {{ t('student.grammarV4.ask.empty') }}
      </div>
      <div
        v-for="(m, i) in messages"
        :key="i"
        class="bubble"
        :class="m.role === 'student' ? 'bubble--student' : 'bubble--assistant'"
      >
        <p>{{ m.text }}</p>
        <AppButton
          v-if="m.role === 'assistant'"
          variant="ghost"
          size="small"
          prepend-icon="mdi-volume-high"
          @click="$emit('play', m.text, /[\u0600-\u06FF]/.test(m.text) ? 'ar-SA' : 'en-US')"
        >
          {{ t('student.grammarV4.playAudio') }}
        </AppButton>
      </div>
    </div>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-3 rounded-lg">{{ error }}</v-alert>

    <div class="composer">
      <textarea
        :value="draft"
        class="composer__input"
        rows="2"
        :placeholder="t('student.grammarV4.ask.placeholder')"
        :disabled="loading"
        @input="$emit('update:draft', $event.target.value)"
        @keydown.enter.exact.prevent="$emit('send')"
      />
      <AppButton
        variant="primary"
        :loading="loading"
        prepend-icon="mdi-send"
        @click="$emit('send')"
      >
        {{ t('student.grammarV4.ask.send') }}
      </AppButton>
    </div>
  </section>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import AppButton from '../ui/AppButton.vue'

defineProps({
  messages: { type: Array, default: () => [] },
  draft: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  topic: { type: String, default: '' },
})

defineEmits(['update:draft', 'send', 'play'])
const { t } = useI18n()
</script>

<style scoped>
.g4-section__title {
  margin: 0 0 8px;
  font-size: 1.5rem;
  font-family: var(--font-display, Tajawal, sans-serif);
}

.g4-section__sub {
  margin: 0 0 16px;
  color: var(--text-muted, #3f4f63);
}

.chat {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 160px;
  max-height: 420px;
  overflow: auto;
  padding: 16px;
  border-radius: 16px;
  background: var(--surface-elevated, #fff);
  margin-block-end: 12px;
}

.chat__empty {
  color: var(--text-muted, #3f4f63);
  font-size: 0.95rem;
}

.bubble {
  max-width: 92%;
  padding: 12px 14px;
  border-radius: 16px;
}

.bubble p {
  margin: 0 0 6px;
  line-height: 1.55;
  white-space: pre-wrap;
}

.bubble--student {
  align-self: flex-end;
  background: color-mix(in srgb, var(--color-primary, #6366f1) 14%, transparent);
}

.bubble--assistant {
  align-self: flex-start;
  background: color-mix(in srgb, var(--text-muted, #3f4f63) 8%, #fff);
}

.composer {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.composer__input {
  flex: 1;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid color-mix(in srgb, var(--text-muted, #3f4f63) 25%, transparent);
  font: inherit;
  resize: vertical;
  background: var(--surface-elevated, #fff);
}
</style>
