<template>
  <div :class="rootClasses" :aria-hidden="decorative ? 'true' : undefined">
    <EduMindLogo :size="context" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import EduMindLogo from '../auth/EduMindLogo.vue'

const props = defineProps({
  context: {
    type: String,
    default: 'inline',
    validator: (v) => ['sidebar', 'loading', 'inline', 'empty'].includes(v),
  },
  decorative: { type: Boolean, default: true },
})

const rootClasses = computed(() => [
  'eduspark-brand-icon',
  `eduspark-brand-icon--${props.context}`,
])
</script>

<style scoped>
.eduspark-brand-icon {
  line-height: 0;
}

.eduspark-brand-icon--sidebar {
  display: flex;
  justify-content: center;
  width: 100%;
}

.eduspark-brand-icon--loading,
.eduspark-brand-icon--inline {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.eduspark-brand-icon--empty {
  width: 72px;
  height: 72px;
  margin-inline: auto;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--em-surface-control, rgba(var(--v-theme-on-surface), 0.04));
  border: 1px solid var(--em-border-subtle);
}
</style>
