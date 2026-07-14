<template>
  <section :class="sectionClasses">
    <header v-if="title || subtitle || $slots.actions" class="app-section__head">
      <div class="app-section__titles">
        <p v-if="eyebrow" class="app-section__eyebrow">{{ eyebrow }}</p>
        <h2 v-if="title" class="app-section__title">{{ title }}</h2>
        <p v-if="subtitle" class="app-section__subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.actions" class="app-section__actions">
        <slot name="actions" />
      </div>
    </header>
    <div class="app-section__body">
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
  spacing: { type: String, default: 'md' },
  divider: { type: Boolean, default: true },
})

const sectionClasses = computed(() => [
  'app-section',
  'section-block',
  props.spacing === 'sm' && 'app-section--sm',
  props.spacing === 'lg' && 'app-section--lg',
  !props.divider && 'app-section--no-divider',
])
</script>

<style scoped>
.app-section {
  margin-bottom: var(--em-space-xl);
}

.app-section--sm {
  margin-bottom: var(--em-space-lg);
}

.app-section--lg {
  margin-bottom: var(--em-space-2xl);
}

.app-section__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--em-space-md);
  flex-wrap: wrap;
  margin-bottom: var(--em-space-md);
  padding-bottom: var(--em-space-sm);
  border-bottom: 1px solid var(--em-border-subtle);
}

.app-section--no-divider .app-section__head {
  border-bottom: none;
  padding-bottom: 0;
}

.app-section__eyebrow {
  margin: 0 0 4px;
  font-size: var(--em-text-caption);
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--em-primary-deep);
}

.app-section__title {
  margin: 0 0 4px;
  font-family: var(--font-display);
  font-size: var(--em-text-title);
  font-weight: 700;
  color: var(--em-text);
}

.app-section__subtitle {
  margin: 0;
  font-size: var(--em-text-sm);
  color: var(--em-text-muted);
  max-width: 52ch;
}

.app-section__actions {
  display: flex;
  align-items: center;
  gap: var(--em-space-sm);
}
</style>
