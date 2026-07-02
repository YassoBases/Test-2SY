<template>
  <div class="aurora" aria-hidden="true">
    <span class="blob b1" />
    <span class="blob b2" />
    <span class="blob b3" />
  </div>
</template>

<script setup>
// Decorative living gradient background — slow-drifting colour blobs. Purely cosmetic.
</script>

<style scoped>
.aurora {
  position: absolute;
  inset: 0;
  overflow: hidden;
  z-index: 0;
  pointer-events: none;
  border-radius: inherit;
}
.blob {
  position: absolute;
  width: 46vw;
  height: 46vw;
  max-width: 640px;
  max-height: 640px;
  border-radius: 50%;
  filter: blur(90px);
  opacity: 0.3;
  mix-blend-mode: screen;
  animation: drift 20s ease-in-out infinite;
}
.b1 { background: radial-gradient(circle, #22d3ee, transparent 70%); top: -12%; left: -8%; }
.b2 { background: radial-gradient(circle, #a78bfa, transparent 70%); bottom: -18%; right: -8%; animation-delay: -7s; }
.b3 { background: radial-gradient(circle, #34d399, transparent 70%); top: 25%; right: 22%; animation-delay: -13s; }

@keyframes drift {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(7%, 9%) scale(1.18); }
  66% { transform: translate(-6%, 4%) scale(0.92); }
}
@media (prefers-reduced-motion: reduce) {
  .blob { animation: none; }
}
</style>
