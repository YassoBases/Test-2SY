<template>
  <header
    class="page-header"
    :class="{
      'page-header--compact': compact,
      'page-header--panel': panel,
    }"
  >
    <div class="d-flex flex-wrap align-end justify-space-between gap-4">
      <div class="flex-grow-1">
        <span v-if="eyebrow" class="section-eyebrow">
          <v-icon v-if="eyebrowIcon" size="14">{{ eyebrowIcon }}</v-icon>
          {{ eyebrow }}
        </span>
        <h1 class="section-title" :class="{ 'eduspark-gradient-text': gradientTitle }">
          {{ title }}
        </h1>
        <p v-if="subtitle" class="section-subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.actions" class="flex-shrink-0">
        <slot name="actions" />
      </div>
    </div>
    <slot />
  </header>
</template>

<script setup>
defineProps({
  eyebrow: { type: String, default: '' },
  eyebrowIcon: { type: String, default: '' },
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  gradientTitle: { type: Boolean, default: false },
  compact: { type: Boolean, default: false },
  panel: { type: Boolean, default: true },
})
</script>

<style scoped>
.page-header {
  margin-bottom: 2rem;
}

.page-header--compact {
  margin-bottom: 1.25rem;
}
</style>
