<template>
  <div v-if="profile" class="gamification-panel">
    <v-row dense class="mb-4">
      <v-col cols="6" sm="3">
        <div class="stat-pill pa-3 rounded-lg text-center">
          <div class="text-h5 font-weight-bold text-secondary">Lv {{ profile.level }}</div>
          <div class="text-caption">{{ t('student.achievements.widgets.level') }}</div>
        </div>
      </v-col>
      <v-col cols="6" sm="3">
        <div class="stat-pill pa-3 rounded-lg text-center">
          <div class="text-h5 font-weight-bold">{{ formatNumber(profile.total_xp) }}</div>
          <div class="text-caption">XP</div>
        </div>
      </v-col>
      <v-col cols="6" sm="3">
        <div class="stat-pill pa-3 rounded-lg text-center">
          <div class="text-h5 font-weight-bold text-warning">🔥 {{ profile.current_streak }}</div>
          <div class="text-caption">{{ t('student.achievements.widgets.streak') }}</div>
        </div>
      </v-col>
      <v-col cols="6" sm="3">
        <div class="stat-pill pa-3 rounded-lg text-center">
          <div class="text-h5 font-weight-bold">{{ profile.achievement_count || 0 }}</div>
          <div class="text-caption">{{ t('student.achievements.widgets.achievement') }}</div>
        </div>
      </v-col>
    </v-row>

    <div v-if="profile.achievements?.length">
      <div class="text-subtitle-2 font-weight-bold mb-2">{{ t('student.achievements.widgets.achievementsTitle') }}</div>
      <div
        v-for="ach in profile.achievements"
        :key="ach.achievement_key"
        class="achievement-row d-flex align-start gap-3 pa-3 rounded-lg mb-2"
      >
        <span class="achievement-row__icon">{{ ach.icon }}</span>
        <div>
          <div class="text-body-2 font-weight-medium">{{ ach.title }}</div>
          <div class="text-caption text-medium-emphasis">{{ ach.description }}</div>
        </div>
      </div>
    </div>
    <p v-else class="text-body-2 text-medium-emphasis mb-0">{{ t('student.achievements.widgets.noAchievementsYet') }}</p>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  profile: { type: Object, default: null },
  readOnly: { type: Boolean, default: true },
})

const { t, locale } = useI18n()

function formatNumber(value) {
  const loc = locale.value === 'ar' ? 'ar-SY' : 'en-US'
  return Number(value || 0).toLocaleString(loc)
}
</script>

<style scoped>
.stat-pill {
  background: rgba(124, 108, 240, 0.08);
  border: 1px solid rgba(124, 108, 240, 0.15);
}

.achievement-row {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(124, 108, 240, 0.12);
}

.achievement-row__icon {
  font-size: 1.5rem;
  line-height: 1;
}
</style>
