<template>
  <div class="brand-lockup" :class="{ 'brand-lockup--centered': centered }">
    <EduMindLogo size="landing" />
  </div>
</template>

<script setup>
import EduMindLogo from '../auth/EduMindLogo.vue'

defineProps({
  centered: { type: Boolean, default: false },
})
</script>

<style scoped>
.brand-lockup {
  display: flex;
  align-items: center;
}

.brand-lockup--centered {
  justify-content: center;
}
</style>
