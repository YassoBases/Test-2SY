<template>
  <div>
    <!-- playing -->
    <template v-if="!done && current">
      <div class="d-flex align-center justify-space-between mb-2">
        <span class="text-caption text-medium-emphasis">Question {{ idx + 1 }} / {{ items.length }}</span>
        <Transition name="combo-pop">
          <span v-if="combo >= 2" class="combo-chip">🔥 {{ combo }} combo</span>
        </Transition>
      </div>
      <v-progress-linear :model-value="(idx / items.length) * 100" color="secondary" height="6" rounded class="mb-4" />

      <div class="flip-card" :class="{ flipped: checked }">
        <div class="flip-inner">
          <!-- FRONT -->
          <div class="face front pa-5" dir="ltr">
            <div class="text-body-1 font-weight-medium mb-3">{{ current.stem }}</div>
            <button
              v-for="(opt, oi) in current.choices"
              :key="oi"
              class="opt"
              :class="{ sel: selected === oi }"
              @click="selected = oi"
            >
              <span class="opt-key">{{ String.fromCharCode(65 + oi) }}</span>{{ opt }}
            </button>
            <v-btn class="mt-3" color="secondary" variant="flat" block :disabled="selected === null" @click="check">
              Check
            </v-btn>
          </div>
          <!-- BACK -->
          <div class="face back pa-6" :class="lastCorrect ? 'back-ok' : 'back-bad'" dir="ltr">
            <v-icon size="46" :icon="lastCorrect ? 'mdi-check-circle' : 'mdi-close-circle'" :color="lastCorrect ? 'success' : 'error'" class="mb-2" />
            <div class="text-h6 font-weight-bold mb-1">{{ lastCorrect ? 'Correct!' : 'Not quite' }}</div>
            <div v-if="lastCorrect" class="text-body-2 mb-4">{{ combo >= 3 ? "You're on fire! 🔥" : 'Nice work.' }}</div>
            <div v-else class="text-body-2 mb-4">Answer: <strong>{{ current.choices[current.correct_index] }}</strong></div>
            <v-btn color="secondary" variant="flat" block @click="next">
              {{ idx + 1 < items.length ? 'Next' : 'Finish' }}
            </v-btn>
          </div>
        </div>
      </div>
    </template>

    <!-- summary -->
    <div
      v-else-if="done"
      class="text-center pa-4"
      v-motion
      :initial="{ scale: 0.85, opacity: 0 }"
      :enter="{ scale: 1, opacity: 1, transition: { type: 'spring', stiffness: 220, damping: 16 } }"
    >
      <v-icon size="52" :color="score === items.length ? 'warning' : 'secondary'" class="mb-2">
        {{ score === items.length ? 'mdi-trophy' : 'mdi-check-decagram' }}
      </v-icon>
      <div class="text-h4 font-weight-bold mb-1">{{ score }} / {{ items.length }}</div>
      <div class="text-body-2 text-medium-emphasis mb-4">Best combo: 🔥 {{ maxCombo }}</div>
      <v-btn color="secondary" variant="tonal" @click="$emit('replay')">Another set</v-btn>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { celebrate, celebrateBig } from '../../composables/useCelebrate.js'

const props = defineProps({ items: { type: Array, default: () => [] } })
const emit = defineEmits(['finish', 'replay'])

const idx = ref(0)
const selected = ref(null)
const checked = ref(false)
const lastCorrect = ref(false)
const combo = ref(0)
const maxCombo = ref(0)
const score = ref(0)
const done = ref(false)
const results = ref([])

const current = computed(() => props.items[idx.value] || null)

function reset() {
  idx.value = 0
  selected.value = null
  checked.value = false
  lastCorrect.value = false
  combo.value = 0
  maxCombo.value = 0
  score.value = 0
  done.value = false
  results.value = []
}

function check() {
  if (selected.value === null || checked.value) return
  const correct = selected.value === current.value.correct_index
  lastCorrect.value = correct
  checked.value = true
  results.value.push({ component_code: current.value.component_code, correct })
  if (correct) {
    score.value += 1
    combo.value += 1
    maxCombo.value = Math.max(maxCombo.value, combo.value)
  } else {
    combo.value = 0
  }
}

function next() {
  if (idx.value + 1 < props.items.length) {
    idx.value += 1
    selected.value = null
    checked.value = false
  } else {
    done.value = true
    if (score.value === props.items.length) celebrateBig()
    else if (score.value > 0) celebrate()
    emit('finish', results.value)
  }
}

watch(() => props.items, reset)
</script>

<style scoped>
.flip-card { perspective: 1300px; }
.flip-inner {
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.6s cubic-bezier(0.4, 0.15, 0.2, 1);
  min-height: 230px;
}
.flip-card.flipped .flip-inner { transform: rotateY(180deg); }
.face {
  border-radius: 16px;
  border: 1px solid rgba(var(--v-theme-secondary), 0.22);
  background: rgba(var(--v-theme-surface), 0.6);
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}
.face.back {
  position: absolute;
  inset: 0;
  transform: rotateY(180deg);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.back-ok { border-color: rgba(var(--v-theme-success), 0.5); background: rgba(var(--v-theme-success), 0.08); }
.back-bad { border-color: rgba(var(--v-theme-error), 0.5); background: rgba(var(--v-theme-error), 0.08); }

.opt {
  display: flex;
  align-items: center;
  width: 100%;
  text-align: left;
  padding: 11px 14px;
  margin-bottom: 8px;
  border-radius: 11px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.15);
  background: rgba(var(--v-theme-on-surface), 0.03);
  color: inherit;
  font: inherit;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s, transform 0.1s;
}
.opt:hover { border-color: rgba(var(--v-theme-secondary), 0.55); }
.opt:active { transform: scale(0.99); }
.opt.sel { border-color: rgb(var(--v-theme-secondary)); background: rgba(var(--v-theme-secondary), 0.14); }
.opt-key {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  margin-right: 10px;
  border-radius: 6px;
  font-size: 0.72rem;
  font-weight: 800;
  background: rgba(var(--v-theme-secondary), 0.2);
  color: rgb(var(--v-theme-secondary));
  flex: 0 0 auto;
}

.combo-chip {
  font-weight: 800;
  font-size: 0.8rem;
  color: #fff;
  background: linear-gradient(90deg, #fb923c, #f43f5e);
  padding: 3px 12px;
  border-radius: 999px;
  box-shadow: 0 0 16px rgba(244, 63, 94, 0.5);
}
.combo-pop-enter-active { transition: transform 0.35s cubic-bezier(0.2, 1.4, 0.4, 1), opacity 0.2s; }
.combo-pop-enter-from { transform: scale(0) rotate(-12deg); opacity: 0; }

@media (prefers-reduced-motion: reduce) {
  .flip-inner { transition: none; }
}
</style>
