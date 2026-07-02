<template>
  <v-btn
    :class="btnClasses"
    :color="vuetifyColor"
    :variant="vuetifyVariant"
    :size="size"
    :rounded="rounded"
    :loading="loading"
    :disabled="disabled"
    :to="to"
    :href="href"
    :block="block"
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
    validator: (v) => ['primary', 'secondary', 'ghost', 'danger', 'tonal'].includes(v),
  },
  size: { type: String, default: 'default' },
  rounded: { type: [String, Boolean], default: 'lg' },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  block: { type: Boolean, default: false },
  to: { type: [String, Object], default: undefined },
  href: { type: String, default: undefined },
})

const btnClasses = computed(() => [
  'app-btn',
  'em-press',
  `app-btn--${props.variant}`,
  props.variant === 'primary' && 'btn-glow em-btn em-btn--primary',
  props.variant === 'secondary' && 'btn-glow-outline em-btn em-btn--secondary',
  props.variant === 'ghost' && 'em-btn em-btn--ghost',
  props.variant === 'danger' && 'em-btn em-btn--danger',
])

const vuetifyColor = computed(() => {
  if (props.variant === 'danger') return 'error'
  if (props.variant === 'tonal') return 'primary'
  if (props.variant === 'ghost') return undefined
  return undefined
})

const vuetifyVariant = computed(() => {
  if (props.variant === 'tonal') return 'tonal'
  if (props.variant === 'ghost') return 'text'
  if (props.variant === 'primary' || props.variant === 'danger') return 'flat'
  return 'outlined'
})
</script>

<style scoped>
.app-btn {
  font-weight: 700 !important;
  letter-spacing: 0 !important;
  text-transform: none !important;
}

.app-btn--primary.btn-glow,
.app-btn--secondary.btn-glow-outline {
  border-radius: var(--em-radius-sm) !important;
}
</style>
