<template>
  <section class="stage-container" :aria-labelledby="titleId">
    <header v-if="title || subtitle" class="stage-container__head">
      <p v-if="eyebrow" class="stage-container__eyebrow">{{ eyebrow }}</p>
      <h2 :id="titleId" class="stage-container__title">{{ title }}</h2>
      <p v-if="subtitle" class="stage-container__subtitle">{{ subtitle }}</p>
    </header>
    <div class="stage-container__body">
      <slot />
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  eyebrow: { type: String, default: '' },
  stageId: { type: String, default: 'stage' },
})

const titleId = computed(() => `session-stage-title-${props.stageId}`)
</script>

<style scoped>
.stage-container {
  padding: 28px 28px 32px;
  border-radius: 24px;
  background: var(--surface-elevated, #fff);
  min-height: 320px;
}

.stage-container__eyebrow {
  margin: 0 0 8px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-primary-deep, #4f46e5);
}

.stage-container__title {
  margin: 0 0 8px;
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-family: var(--font-display, Tajawal, sans-serif);
  line-height: 1.2;
}

.stage-container__subtitle {
  margin: 0 0 24px;
  font-size: 1.05rem;
  line-height: 1.55;
  color: var(--text-muted, #3f4f63);
  max-width: 42rem;
}

.stage-container__body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@media (max-width: 600px) {
  .stage-container {
    padding: 20px 16px 24px;
  }
}
</style>
