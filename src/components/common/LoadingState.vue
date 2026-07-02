<template>
  <div :class="wrapperClass">
    <template v-if="variant === 'inline'">
      <div class="em-loading-inline">
        <v-progress-circular indeterminate :size="size" :width="2" color="primary" />
        <span v-if="label" class="text-body-2">{{ label }}</span>
      </div>
    </template>
    <template v-else-if="variant === 'bar'">
      <v-progress-linear indeterminate color="primary" rounded class="mb-2" />
      <p v-if="label" class="text-caption text-medium-emphasis mb-0">{{ label }}</p>
    </template>
    <template v-else>
      <v-skeleton-loader
        v-for="i in count"
        :key="i"
        :type="skeletonType"
        class="em-skeleton glass-card rounded-lg"
      />
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  /** cards | table | article | bar | inline */
  variant: { type: String, default: 'cards' },
  count: { type: Number, default: 3 },
  label: { type: String, default: '' },
  size: { type: Number, default: 32 },
})

const skeletonType = computed(() => {
  const map = {
    cards: 'card',
    table: 'table',
    article: 'article',
    list: 'list-item@3',
  }
  return map[props.variant] || 'card'
})

const wrapperClass = computed(() => {
  if (props.variant === 'inline' || props.variant === 'bar') return ''
  return props.variant === 'table' ? '' : 'em-loading-grid em-loading-grid--cards'
})
</script>
