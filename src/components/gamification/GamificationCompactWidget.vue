<template>
  <v-card
    class="glass-card gamification-compact pa-4"
    variant="flat"
    :to="to"
    link
    :ripple="false"
  >
    <div class="d-flex align-center justify-space-between gap-3">
      <div class="d-flex align-center gap-4 flex-wrap">
        <div class="compact-stat">
          <span class="compact-stat__label">{{ t('student.achievements.widgets.level') }}</span>
          <span class="compact-stat__value text-secondary">Lv {{ profile.level }}</span>
        </div>
        <div class="compact-stat">
          <span class="compact-stat__label">XP</span>
          <span class="compact-stat__value">{{ formatNumber(profile.total_xp) }}</span>
        </div>
        <div class="compact-stat">
          <span class="compact-stat__label">{{ t('student.achievements.widgets.streak') }}</span>
          <span class="compact-stat__value text-warning">{{ profile.streak_display || `🔥 ${profile.current_streak}` }}</span>
        </div>
      </div>
      <v-icon color="medium-emphasis" size="20">mdi-chevron-left</v-icon>
    </div>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  profile: {
    type: Object,
    required: true,
  },
  to: {
    type: String,
    required: true,
  },
})

const { t, locale } = useI18n()

function formatNumber(value) {
  const loc = locale.value === 'ar' ? 'ar-SY' : 'en-US'
  return Number(value || 0).toLocaleString(loc)
}
</script>

<style scoped>
.gamification-compact {
  border: 1px solid rgba(124, 108, 240, 0.2);
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.gamification-compact:hover {
  border-color: rgba(124, 108, 240, 0.45);
  transform: translateY(-1px);
}

.compact-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 72px;
}

.compact-stat__label {
  font-size: 0.7rem;
  color: rgba(255, 255, 255, 0.55);
}

.compact-stat__value {
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.2;
}
</style>
