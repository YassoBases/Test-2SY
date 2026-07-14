<template>
  <div class="welcome-bg" aria-hidden="true">
    <div class="welcome-bg__base" />
    <div class="welcome-bg__aurora welcome-bg__aurora--1" />
    <div class="welcome-bg__aurora welcome-bg__aurora--2" />
    <div class="welcome-bg__aurora welcome-bg__aurora--3" />
    <div class="welcome-bg__sheen" />
    <div
      v-for="p in particles"
      :key="p.id"
      class="welcome-bg__particle"
      :style="p.style"
    />
  </div>
</template>

<script setup>
const particles = Array.from({ length: 18 }, (_, i) => ({
  id: i,
  style: {
    left: `${8 + (i * 17.3) % 88}%`,
    top: `${12 + (i * 13.7) % 78}%`,
    width: `${2 + (i % 3)}px`,
    height: `${2 + (i % 3)}px`,
    animationDelay: `${(i * 0.45) % 5}s`,
    animationDuration: `${6 + (i % 5) * 1.2}s`,
    opacity: 0.15 + (i % 4) * 0.08,
  },
}))
</script>

<style scoped>
.welcome-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.welcome-bg__base {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 55% at 50% -10%, rgba(91, 79, 207, 0.22) 0%, transparent 58%),
    radial-gradient(ellipse 60% 45% at 15% 85%, rgba(34, 211, 238, 0.08) 0%, transparent 52%),
    radial-gradient(ellipse 55% 40% at 88% 72%, rgba(124, 108, 240, 0.1) 0%, transparent 48%),
    linear-gradient(168deg, #050810 0%, #0a1224 38%, #070d18 100%);
}

.welcome-bg__aurora {
  position: absolute;
  border-radius: 50%;
  filter: blur(72px);
  opacity: 0.55;
  will-change: transform, opacity;
}

.welcome-bg__aurora--1 {
  width: min(68vw, 520px);
  height: min(68vw, 520px);
  top: -18%;
  left: 50%;
  transform: translateX(-50%);
  background: radial-gradient(circle, rgba(124, 108, 240, 0.45) 0%, rgba(124, 108, 240, 0) 68%);
  animation: aurora-drift-1 22s ease-in-out infinite;
}

.welcome-bg__aurora--2 {
  width: min(55vw, 420px);
  height: min(55vw, 420px);
  bottom: -12%;
  left: -8%;
  background: radial-gradient(circle, rgba(34, 211, 238, 0.28) 0%, rgba(34, 211, 238, 0) 70%);
  animation: aurora-drift-2 26s ease-in-out infinite;
}

.welcome-bg__aurora--3 {
  width: min(48vw, 380px);
  height: min(48vw, 380px);
  top: 38%;
  right: -10%;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.22) 0%, rgba(59, 130, 246, 0) 72%);
  animation: aurora-drift-3 20s ease-in-out infinite;
}

.welcome-bg__sheen {
  position: absolute;
  inset: -20%;
  background: linear-gradient(
    115deg,
    transparent 42%,
    rgba(34, 211, 238, 0.04) 48%,
    rgba(124, 108, 240, 0.06) 52%,
    transparent 58%
  );
  animation: aurora-sheen 14s ease-in-out infinite;
}

.welcome-bg__particle {
  position: absolute;
  border-radius: 50%;
  background: rgba(186, 230, 253, 0.85);
  box-shadow: 0 0 10px rgba(34, 211, 238, 0.35);
  animation: particle-float ease-in-out infinite;
}

@keyframes aurora-drift-1 {
  0%, 100% { transform: translateX(-50%) translateY(0) scale(1); opacity: 0.5; }
  50% { transform: translateX(-46%) translateY(28px) scale(1.06); opacity: 0.62; }
}

@keyframes aurora-drift-2 {
  0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.42; }
  50% { transform: translate(32px, -24px) scale(1.08); opacity: 0.55; }
}

@keyframes aurora-drift-3 {
  0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.38; }
  50% { transform: translate(-28px, 20px) scale(1.05); opacity: 0.5; }
}

@keyframes aurora-sheen {
  0%, 100% { transform: translateX(-8%) rotate(0deg); opacity: 0.35; }
  50% { transform: translateX(8%) rotate(2deg); opacity: 0.65; }
}

@keyframes particle-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-14px); }
}

@media (prefers-reduced-motion: reduce) {
  .welcome-bg__aurora,
  .welcome-bg__sheen,
  .welcome-bg__particle {
    animation: none;
  }
}
</style>
