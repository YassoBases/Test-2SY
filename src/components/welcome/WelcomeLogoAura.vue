<template>
  <div class="logo-aura" aria-hidden="true">
    <div class="logo-aura__bloom" />
    <div class="logo-aura__bloom logo-aura__bloom--cyan" />
    <div class="logo-aura__ray logo-aura__ray--1" />
    <div class="logo-aura__ray logo-aura__ray--2" />
    <div
      v-for="s in sparks"
      :key="s.id"
      class="logo-aura__spark"
      :style="s.style"
    />
    <div class="logo-aura__logo">
      <EduSparkLogo variant="landing" />
    </div>
  </div>
</template>

<script setup>
import EduSparkLogo from '../auth/EduSparkLogo.vue'

const sparks = Array.from({ length: 6 }, (_, i) => ({
  id: i,
  style: {
    left: `${18 + i * 14}%`,
    top: `${12 + (i % 3) * 28}%`,
    animationDelay: `${i * 0.7}s`,
  },
}))
</script>

<style scoped>
.logo-aura {
  position: relative;
  width: clamp(92px, 13vh, 124px);
  height: clamp(92px, 13vh, 124px);
  flex-shrink: 0;
  animation: logo-float 8s ease-in-out infinite;
}

.logo-aura__bloom {
  position: absolute;
  inset: -35%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(124, 108, 240, 0.35) 0%, transparent 68%);
  filter: blur(18px);
  animation: bloom-pulse 5s ease-in-out infinite;
}

.logo-aura__bloom--cyan {
  inset: -25%;
  background: radial-gradient(circle, rgba(34, 211, 238, 0.22) 0%, transparent 70%);
  animation-delay: -2.5s;
}

.logo-aura__ray {
  position: absolute;
  width: 1px;
  height: 140%;
  top: -20%;
  left: 50%;
  background: linear-gradient(180deg, transparent, rgba(34, 211, 238, 0.25), transparent);
  transform-origin: center;
  opacity: 0.4;
}

.logo-aura__ray--1 {
  transform: rotate(25deg);
  animation: ray-shimmer 6s ease-in-out infinite;
}

.logo-aura__ray--2 {
  transform: rotate(-30deg);
  animation: ray-shimmer 7s ease-in-out infinite reverse;
}

.logo-aura__spark {
  position: absolute;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: rgba(34, 211, 238, 0.8);
  box-shadow: 0 0 8px rgba(34, 211, 238, 0.6);
  animation: spark-drift 4s ease-in-out infinite;
}

.logo-aura__logo {
  position: relative;
  z-index: 2;
  width: 100%;
  height: 100%;
}

@keyframes logo-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

@keyframes bloom-pulse {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.06); }
}

@keyframes ray-shimmer {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 0.5; }
}

@keyframes spark-drift {
  0%, 100% { transform: translate(0, 0); opacity: 0.4; }
  50% { transform: translate(4px, -8px); opacity: 0.9; }
}
</style>
