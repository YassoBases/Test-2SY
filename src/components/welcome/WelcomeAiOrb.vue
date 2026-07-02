<template>
  <div class="ai-orb-cluster">
    <div class="ai-orb-wrap" :class="{ 'ai-orb-wrap--logo': showLogo }">
      <div class="ai-orb__halo ai-orb__halo--outer" aria-hidden="true" />
      <div class="ai-orb__halo ai-orb__halo--mid" aria-hidden="true" />
      <div class="ai-orb__core">
        <div class="ai-orb__inner" :class="{ 'ai-orb__inner--logo': showLogo }">
          <EduSparkLogo v-if="showLogo" size="hero" class="ai-orb__logo" />
          <v-icon v-else color="white" size="28" class="ai-orb__icon">mdi-brain</v-icon>
        </div>
        <div class="ai-orb__ring" aria-hidden="true" />
        <div class="ai-orb__ring ai-orb__ring--2" aria-hidden="true" />
      </div>
      <div class="ai-orb__pulse" aria-hidden="true" />
    </div>
    <slot />
  </div>
</template>

<script setup>
import EduSparkLogo from '../auth/EduSparkLogo.vue'

defineProps({
  showLogo: { type: Boolean, default: false },
})
</script>

<style scoped>
.ai-orb-cluster {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.ai-orb-wrap {
  position: relative;
  width: clamp(72px, 11vh, 96px);
  height: clamp(72px, 11vh, 96px);
  margin: 0 auto;
  animation: orb-float 7s ease-in-out infinite;
}

.ai-orb-wrap--logo {
  width: clamp(80px, 12vh, 104px);
  height: clamp(80px, 12vh, 104px);
}

.ai-orb__halo {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  animation: halo-breathe 4s ease-in-out infinite;
}

.ai-orb__halo--outer {
  inset: -22px;
  background: radial-gradient(circle, rgba(34, 211, 238, 0.2) 0%, transparent 70%);
}

.ai-orb__halo--mid {
  inset: -10px;
  background: radial-gradient(circle, rgba(124, 108, 240, 0.35) 0%, transparent 65%);
  animation-delay: -1.5s;
}

.ai-orb__core {
  position: relative;
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.ai-orb__inner {
  position: absolute;
  inset: 8%;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(145deg, rgba(124, 108, 240, 0.85), rgba(34, 211, 238, 0.7));
  box-shadow:
    0 0 32px rgba(34, 211, 238, 0.45),
    0 0 64px rgba(124, 108, 240, 0.3),
    inset 0 0 24px rgba(255, 255, 255, 0.12);
  z-index: 2;
  overflow: hidden;
}

.ai-orb__inner--logo {
  inset: 4%;
  background: rgba(12, 18, 40, 0.65);
  border: 1px solid rgba(124, 108, 240, 0.4);
}

.ai-orb__logo {
  margin: 0 !important;
}

.ai-orb__logo :deep(.eduspark-logo) {
  width: 100% !important;
  height: 100% !important;
}

.ai-orb__logo :deep(.eduspark-logo__ring) {
  inset: -3px;
  opacity: 0.7;
}

.ai-orb__logo :deep(.eduspark-logo:hover) {
  transform: none;
}

.ai-orb__icon {
  filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.5));
}

.ai-orb__ring {
  position: absolute;
  inset: -4%;
  border-radius: 50%;
  border: 1px solid rgba(34, 211, 238, 0.4);
  animation: ring-spin 8s linear infinite;
}

.ai-orb__ring--2 {
  inset: -10%;
  border-color: rgba(124, 108, 240, 0.25);
  animation-duration: 12s;
  animation-direction: reverse;
}

.ai-orb__pulse {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid rgba(34, 211, 238, 0.45);
  animation: pulse-ring 3s ease-out infinite;
}

:deep(.orb-tagline) {
  margin: 0.35rem 0 0;
  font-size: clamp(0.65rem, 1.4vh, 0.78rem);
  line-height: 1.45;
  font-weight: 600;
  text-align: center;
  color: var(--em-cyan);
  text-shadow: 0 0 20px rgba(34, 211, 238, 0.35);
  direction: rtl;
}

@keyframes orb-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

@keyframes halo-breathe {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.06); }
}

@keyframes ring-spin {
  to { transform: rotate(360deg); }
}

@keyframes pulse-ring {
  0% { transform: scale(1); opacity: 0.55; }
  100% { transform: scale(1.5); opacity: 0; }
}
</style>
