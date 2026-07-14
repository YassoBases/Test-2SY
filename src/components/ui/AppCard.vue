<template>
  <v-card
    :class="cardClasses"
    :variant="variant"
    :to="to"
    :href="href"
    :link="Boolean(to || href)"
    :ripple="interactive"
    v-bind="$attrs"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="onPointerUp"
    @pointercancel="onPointerCancel"
  >
    <slot />
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  variant: { type: String, default: 'flat' },
  solid: { type: Boolean, default: false },
  elevated: { type: Boolean, default: false },
  interactive: { type: Boolean, default: false },
  padding: { type: String, default: 'md' },
  to: { type: [String, Object], default: undefined },
  href: { type: String, default: undefined },
})

const router = useRouter()

const TAP_MOVE_THRESHOLD_PX = 10

const cardClasses = computed(() => [
  'app-card',
  'glass-card',
  props.solid && 'glass-card--solid',
  props.elevated && 'glass-card--elevated',
  props.interactive && 'app-card--interactive em-hover-lift',
  props.padding === 'sm' && 'app-card--pad-sm',
  props.padding === 'md' && 'app-card--pad-md',
  props.padding === 'lg' && 'app-card--pad-lg',
  props.padding === 'none' && 'app-card--pad-none',
])

let pointerOrigin = null
let pointerDragged = false

function resetPointer() {
  pointerOrigin = null
  pointerDragged = false
}

function onPointerDown(event) {
  if (!props.to || props.href) return
  pointerOrigin = { x: event.clientX, y: event.clientY }
  pointerDragged = false
}

function onPointerMove(event) {
  if (!pointerOrigin) return
  const dx = Math.abs(event.clientX - pointerOrigin.x)
  const dy = Math.abs(event.clientY - pointerOrigin.y)
  if (dx > TAP_MOVE_THRESHOLD_PX || dy > TAP_MOVE_THRESHOLD_PX) {
    pointerDragged = true
  }
}

function onPointerUp(event) {
  if (!props.to || props.href || !pointerOrigin || pointerDragged) {
    resetPointer()
    return
  }

  const pointerType = event.pointerType
  resetPointer()

  // Horizontal scroll rails can suppress click on touch; router.push matches v-card :to behavior.
  if (pointerType === 'touch' || pointerType === 'pen') {
    router.push(props.to)
  }
}

function onPointerCancel() {
  resetPointer()
}
</script>

<style scoped>
.app-card {
  border-radius: var(--em-radius-md) !important;
}

.app-card--pad-sm :deep(.v-card-text),
.app-card--pad-sm {
  padding: var(--em-space-md);
}

.app-card--pad-md :deep(.v-card-text),
.app-card--pad-md {
  padding: var(--em-space-lg);
}

.app-card--pad-lg :deep(.v-card-text),
.app-card--pad-lg {
  padding: var(--em-space-xl);
}

.app-card--pad-none :deep(.v-card-text) {
  padding: 0;
}

.app-card--interactive {
  cursor: pointer;
  touch-action: manipulation;
}
</style>
