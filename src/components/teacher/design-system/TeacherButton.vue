<template>
  <v-btn
    :class="btnClasses"
    :color="vuetifyColor"
    :variant="vuetifyVariant"
    :size="size"
    rounded="lg"
    :loading="loading"
    :disabled="disabled"
    :to="to"
    :href="href"
    :block="block"
    :icon="icon"
    v-bind="$attrs"
  >
    <slot />
  </v-btn>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'secondary', 'ghost', 'tonal', 'danger'].includes(v),
  },
  size: { type: String, default: 'default' },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  block: { type: Boolean, default: false },
  icon: { type: [Boolean, String], default: false },
  to: { type: [String, Object], default: undefined },
  href: { type: String, default: undefined },
})

const btnClasses = computed(() => [
  'tds-btn',
  'em-press',
  `tds-btn--${props.variant}`,
  props.variant === 'primary' && 'btn-glow',
  props.variant === 'secondary' && 'btn-glow-outline',
])

const vuetifyColor = computed(() => {
  if (props.variant === 'danger') return 'error'
  if (props.variant === 'tonal') return 'primary'
  if (props.variant === 'secondary') return 'secondary'
  if (props.variant === 'primary') return 'secondary'
  return undefined
})

const vuetifyVariant = computed(() => {
  if (props.variant === 'tonal') return 'tonal'
  if (props.variant === 'ghost') return 'text'
  if (props.variant === 'primary' || props.variant === 'danger') return 'flat'
  if (props.variant === 'secondary') return 'outlined'
  return 'text'
})
</script>
