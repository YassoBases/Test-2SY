<template>
  <p class="typing-line text-h6 font-weight-medium">
    <span class="typing-prefix">{{ t('common.brand.name') }} </span>
    <span class="typing-text">{{ displayText }}</span>
    <span class="typing-cursor" aria-hidden="true">|</span>
  </p>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { useTypingEffect } from '../../composables/useTypingEffect.js'

const { t, tm } = useI18n()

const { displayText } = useTypingEffect(tm('auth.welcome.typingPhrases'), {
  typeSpeed: 58,
  deleteSpeed: 30,
  pauseMs: 2400,
})
</script>

<style scoped>
.typing-line {
  min-height: 2rem;
  color: var(--em-text-muted);
  direction: rtl;
}

.typing-prefix {
  color: var(--em-cyan);
  font-weight: 600;
}

.typing-text {
  color: var(--em-text);
}

.typing-cursor {
  display: inline-block;
  color: var(--em-cyan);
  font-weight: 300;
  margin-inline-start: 2px;
  animation: cursor-blink 1s step-end infinite;
}

@keyframes cursor-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
</style>
