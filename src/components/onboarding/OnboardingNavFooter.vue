<template>
  <div class="onboarding-nav-footer">
    <OnboardingBackButton v-if="showBack" :to="backTo" />
    <div v-else class="onboarding-nav-footer__spacer" />

    <div class="onboarding-nav-footer__primary">
      <slot />
    </div>
  </div>
</template>

<script setup>
import OnboardingBackButton from './OnboardingBackButton.vue'

defineProps({
  showBack: { type: Boolean, default: true },
  backTo: { type: [String, Object], default: null },
})
</script>

<style scoped>
.onboarding-nav-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: 2rem;
  flex-wrap: wrap;
}

.onboarding-nav-footer__primary {
  display: flex;
  justify-content: center;
  flex: 1;
  min-width: 0;
}

.onboarding-nav-footer__spacer {
  width: 4.5rem;
  flex-shrink: 0;
}

@media (max-width: 599px) {
  .onboarding-nav-footer {
    flex-direction: column-reverse;
    align-items: stretch;
  }

  .onboarding-nav-footer__primary :deep(.v-btn) {
    width: 100%;
  }
}
</style>
