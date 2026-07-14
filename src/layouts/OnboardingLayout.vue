<template>
  <div class="onboarding-layout" dir="rtl">
    <div class="onboarding-layout__inner">
      <OnboardingAccountHeader />
      <router-view />
    </div>
  </div>
</template>

<script setup>
import OnboardingAccountHeader from '../components/onboarding/OnboardingAccountHeader.vue'
</script>

<style scoped>
.onboarding-layout {
  min-height: 100dvh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 1rem 1rem 1.5rem;
  padding-top: max(1rem, env(safe-area-inset-top, 0px));
}

.onboarding-layout__inner {
  width: 100%;
  max-width: 720px;
}
</style>
