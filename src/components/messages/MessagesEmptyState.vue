<template>
  <div class="messages-empty empty-state" :class="variant">
    <div class="messages-empty__icon">
      <v-icon :size="iconSize" color="primary">{{ icon }}</v-icon>
    </div>
    <h3 v-if="title" class="messages-empty__title">{{ title }}</h3>
    <p v-if="subtitle" class="messages-empty__subtitle">{{ subtitle }}</p>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: 'mdi-message-text-outline' },
  iconSize: { type: [Number, String], default: 48 },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  variant: { type: String, default: 'default' },
})
</script>

<style scoped>
.messages-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 2rem 1.5rem;
}

.messages-empty__icon {
  width: 80px;
  height: 80px;
  margin-bottom: 1rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--em-surface-control);
  border: 1px solid var(--em-border-subtle);
}

.messages-empty__title {
  margin: 0 0 8px;
  font-family: var(--font-display);
  font-size: 1.0625rem;
  font-weight: 700;
  color: var(--em-text);
}

.messages-empty__subtitle {
  margin: 0 0 1rem;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--em-text-muted);
  max-width: 320px;
}

.messages-empty--compact {
  padding: 1.5rem 1rem;
}

.messages-empty--compact .messages-empty__icon {
  width: 64px;
  height: 64px;
  margin-bottom: 0.75rem;
}

.messages-empty--compact .messages-empty__title {
  font-size: 0.9375rem;
}

.messages-empty--compact .messages-empty__subtitle {
  font-size: 0.8125rem;
  margin-bottom: 0.75rem;
}
</style>
