<template>
  <v-card
    :class="cardClasses"
    :to="to"
    :href="href"
    variant="flat"
    v-bind="$attrs"
  >
    <slot />
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  /** stat | content | analytics | message */
  variant: { type: String, default: 'content' },
  interactive: { type: Boolean, default: false },
  solid: { type: Boolean, default: true },
  to: { type: [String, Object], default: undefined },
  href: { type: String, default: undefined },
})

const cardClasses = computed(() => {
  const base = ['content-card']
  if (props.solid) base.push('glass-card--solid')
  if (props.interactive) base.push('content-card--interactive', 'eduspark-card-hover')
  if (props.variant === 'stat' || props.variant === 'analytics') {
    base.push('stat-card', 'glass-card')
  } else if (props.variant === 'message') {
    base.push('message-card')
  } else {
    base.push('glass-card')
  }
  return base
})
</script>
