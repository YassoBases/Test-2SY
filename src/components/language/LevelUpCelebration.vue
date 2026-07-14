<template>
  <Transition name="lvlup-fade">
    <div v-if="show" class="lvlup-overlay" @click="$emit('close')">
      <div
        class="lvlup-card"
        v-motion
        :initial="{ scale: 0.55, opacity: 0, y: 40 }"
        :enter="{ scale: 1, opacity: 1, y: 0, transition: { type: 'spring', stiffness: 240, damping: 16 } }"
        @click.stop
      >
        <div class="lvlup-eyebrow">⚡ LEVEL UP</div>

        <div class="lvlup-badge-wrap">
          <span class="lvlup-ring" />
          <span class="lvlup-ring lvlup-ring--2" />
          <div
            class="lvlup-badge"
            v-motion
            :initial="{ scale: 0 }"
            :enter="{ scale: 1, transition: { delay: 220, type: 'spring', stiffness: 200, damping: 12 } }"
          >
            {{ to }}
          </div>
        </div>

        <div class="lvlup-sub">
          You reached <strong>{{ to }}</strong><template v-if="from"> — up from {{ from }}</template>! 🎉
        </div>
        <p class="lvlup-note">New lessons and harder challenges are unlocked.</p>

        <v-btn color="secondary" variant="flat" size="large" rounded="lg" @click.stop="$emit('close')">
          Keep going
        </v-btn>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { watch } from 'vue'
import { celebrateBig, celebrateShower } from '../../composables/useCelebrate.js'

const props = defineProps({
  show: { type: Boolean, default: false },
  from: { type: String, default: '' },
  to: { type: String, default: '' },
})
defineEmits(['close'])

let stop = null
watch(
  () => props.show,
  (v) => {
    if (v) {
      celebrateBig()
      stop = celebrateShower(2800)
    } else if (stop) {
      stop()
      stop = null
    }
  },
)
</script>

<style scoped>
.lvlup-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(8, 11, 22, 0.66);
  backdrop-filter: blur(10px);
  padding: 24px;
}
.lvlup-card {
  position: relative;
  text-align: center;
  padding: 40px 32px 32px;
  border-radius: 28px;
  background: linear-gradient(160deg, rgba(34, 211, 238, 0.12), rgba(167, 139, 250, 0.12)), rgba(20, 24, 38, 0.92);
  border: 1px solid rgba(var(--v-theme-secondary), 0.35);
  box-shadow: 0 30px 80px -20px rgba(34, 211, 238, 0.45);
  max-width: 380px;
  width: 100%;
}
.lvlup-eyebrow {
  font-size: 0.8rem;
  font-weight: 800;
  letter-spacing: 3px;
  color: rgb(var(--v-theme-secondary));
  margin-bottom: 18px;
}
.lvlup-badge-wrap {
  position: relative;
  width: 150px;
  height: 150px;
  margin: 0 auto 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.lvlup-badge {
  width: 116px;
  height: 116px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.6rem;
  font-weight: 900;
  color: #fff;
  background: conic-gradient(from 200deg, #22d3ee, #a78bfa, #34d399, #22d3ee);
  box-shadow: 0 0 40px rgba(34, 211, 238, 0.7), inset 0 0 18px rgba(255, 255, 255, 0.25);
  animation: badgePulse 1.8s ease-in-out infinite;
}
.lvlup-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid rgba(var(--v-theme-secondary), 0.6);
  animation: ringOut 1.8s ease-out infinite;
}
.lvlup-ring--2 { animation-delay: 0.9s; }
.lvlup-sub { font-size: 1.05rem; color: rgba(255, 255, 255, 0.92); margin-bottom: 4px; }
.lvlup-note { font-size: 0.82rem; color: rgba(255, 255, 255, 0.6); margin-bottom: 20px; }

@keyframes badgePulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.06); }
}
@keyframes ringOut {
  0% { transform: scale(0.78); opacity: 0.9; }
  100% { transform: scale(1.5); opacity: 0; }
}
.lvlup-fade-enter-active, .lvlup-fade-leave-active { transition: opacity 0.3s ease; }
.lvlup-fade-enter-from, .lvlup-fade-leave-to { opacity: 0; }

@media (prefers-reduced-motion: reduce) {
  .lvlup-badge, .lvlup-ring { animation: none; }
}
</style>
