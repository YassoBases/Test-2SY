<template>
  <div class="platform-preview">
    <div class="preview-glow" aria-hidden="true" />
    <div class="preview-frame glass-card">
      <div class="preview-header d-flex align-center justify-space-between pa-3">
        <div class="d-flex align-center gap-2">
          <div class="preview-dot preview-dot--cyan" />
          <span class="text-caption font-weight-bold">{{ t('auth.welcome.platformPreview.title') }}</span>
        </div>
        <v-chip size="x-small" variant="tonal" color="secondary">
          {{ t('auth.welcome.platformPreview.live') }}
        </v-chip>
      </div>

      <div class="preview-body pa-3">
        <div
          v-for="(card, i) in cards"
          :key="card.id"
          class="preview-card"
          :class="`preview-card--delay-${i}`"
          :style="{ animationDelay: `${i * 0.15}s` }"
        >
          <div class="d-flex align-center gap-2 mb-2">
            <v-icon :color="card.color" size="18">{{ card.icon }}</v-icon>
            <span class="text-caption font-weight-bold">{{ card.title }}</span>
          </div>
          <p class="text-h6 font-weight-bold mb-1" :class="`text-${card.color}`">{{ card.value }}</p>
          <p class="text-caption text-medium-emphasis mb-0">{{ card.sub }}</p>
          <div v-if="card.bars" class="mini-bars d-flex align-end gap-1 mt-2">
            <div
              v-for="(h, bi) in card.bars"
              :key="bi"
              class="mini-bar"
              :style="{ height: `${h}%`, animationDelay: `${bi * 0.1}s` }"
            />
          </div>
          <v-progress-linear
            v-if="card.progress != null"
            :model-value="card.progress"
            :color="card.color"
            height="4"
            rounded
            class="mt-2"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const CARD_META = [
  { id: 'quiz', icon: 'mdi-clipboard-check', color: 'success', progress: 82 },
  { id: 'attendance', icon: 'mdi-calendar-check', color: 'secondary', progress: 85 },
  { id: 'routine', icon: 'mdi-calendar-clock', color: 'primary' },
  { id: 'analytics', icon: 'mdi-chart-timeline-variant', color: 'warning', bars: [45, 72, 58, 91, 68] },
]

const cards = computed(() =>
  CARD_META.map((meta) => ({
    ...meta,
    title: t(`auth.welcome.platformPreview.cards.${meta.id}.title`),
    value: t(`auth.welcome.platformPreview.cards.${meta.id}.value`),
    sub: t(`auth.welcome.platformPreview.cards.${meta.id}.sub`),
  })),
)
</script>

<style scoped>
.platform-preview {
  position: relative;
  width: 100%;
  max-width: 380px;
  margin-inline: auto;
}

.preview-glow {
  position: absolute;
  inset: -20%;
  background: radial-gradient(circle, rgba(34, 211, 238, 0.15) 0%, transparent 60%);
  animation: preview-glow-pulse 5s ease-in-out infinite;
}

.preview-frame {
  position: relative;
  border: 1px solid rgba(34, 211, 238, 0.25) !important;
  background: rgba(10, 16, 36, 0.75) !important;
  backdrop-filter: blur(24px);
  overflow: hidden;
}

.preview-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.preview-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--em-purple);
  box-shadow: 0 0 8px var(--em-purple);
}

.preview-dot--cyan {
  background: var(--em-cyan);
  box-shadow: 0 0 8px var(--em-cyan);
}

.preview-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.preview-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
  animation: card-float 5s ease-in-out infinite;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.preview-card:hover {
  border-color: rgba(34, 211, 238, 0.35);
  box-shadow: 0 0 24px rgba(124, 108, 240, 0.15);
}

.preview-card--delay-1 { animation-delay: 0.4s; }
.preview-card--delay-2 { animation-delay: 0.8s; }
.preview-card--delay-3 { animation-delay: 1.2s; }

.mini-bars {
  height: 28px;
}

.mini-bar {
  flex: 1;
  background: linear-gradient(180deg, var(--em-cyan), var(--em-purple));
  border-radius: 3px 3px 0 0;
  animation: bar-grow 2s ease-in-out infinite alternate;
}

@keyframes card-float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-6px); }
}

@keyframes preview-glow-pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes bar-grow {
  from { opacity: 0.6; }
  to { opacity: 1; }
}
</style>
