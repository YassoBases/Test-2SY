<template>
  <Transition :name="name" mode="out-in">
    <div :key="stageKey" class="stage-transition">
      <slot />
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  stageKey: { type: String, required: true },
  name: { type: String, default: 'session-stage' },
})
</script>

<style scoped>
.stage-transition {
  width: 100%;
}

.session-stage-enter-active,
.session-stage-leave-active {
  transition:
    opacity 220ms ease-out,
    transform 220ms ease-out;
}

.session-stage-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.session-stage-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (prefers-reduced-motion: reduce) {
  .session-stage-enter-active,
  .session-stage-leave-active {
    transition: none;
  }
}
</style>
