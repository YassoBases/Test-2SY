<template>
  <v-card class="glass-card gamification-card pa-5" variant="flat">
    <div class="d-flex align-center justify-space-between flex-wrap gap-3 mb-4">
      <div class="d-flex align-center gap-3">
        <div class="level-badge">
          <span class="level-badge__num">{{ profile.level }}</span>
        </div>
        <div>
          <div class="text-caption text-medium-emphasis">{{ t('student.achievements.widgets.currentLevel') }}</div>
          <div class="text-h5 font-weight-bold">Level {{ profile.level }}</div>
        </div>
      </div>
      <v-chip color="warning" variant="tonal" size="small">
        {{ profile.streak_display || t('student.achievements.streakDaysShort', { n: profile.current_streak }) }}
      </v-chip>
    </div>

    <div class="mb-3">
      <div class="d-flex justify-space-between text-body-2 mb-1">
        <span>{{ formatNumber(profile.total_xp) }} XP</span>
        <span v-if="!profile.is_max_level" class="text-medium-emphasis">
          {{ t('student.achievements.xpToNext', { xp: formatNumber(profile.xp_to_next_level), n: profile.level + 1 }) }}
        </span>
        <span v-else class="text-success">{{ t('student.achievements.maxLevel') }}</span>
      </div>
      <v-progress-linear
        :model-value="profile.progress_percent"
        color="secondary"
        height="8"
        rounded
      />
    </div>

    <div v-if="profile.achievements?.length" class="mt-4">
      <div class="text-caption text-medium-emphasis mb-2">{{ t('student.achievements.widgets.latestAchievements') }}</div>
      <div class="d-flex flex-wrap gap-2">
        <v-chip
          v-for="ach in profile.achievements.slice(0, 4)"
          :key="ach.achievement_key"
          size="small"
          variant="tonal"
          color="primary"
        >
          {{ ach.icon }} {{ ach.title }}
        </v-chip>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  profile: {
    type: Object,
    default: () => ({
      level: 1,
      total_xp: 0,
      xp_to_next_level: 500,
      progress_percent: 0,
      current_streak: 0,
      is_max_level: false,
      achievements: [],
    }),
  },
})

const { t, locale } = useI18n()

function formatNumber(value) {
  const loc = locale.value === 'ar' ? 'ar-SY' : 'en-US'
  return Number(value || 0).toLocaleString(loc)
}
</script>

<style scoped>
.level-badge {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(124, 108, 240, 0.35), rgba(34, 211, 238, 0.25));
  border: 1px solid rgba(124, 108, 240, 0.4);
}

.level-badge__num {
  font-size: 1.25rem;
  font-weight: 800;
}
</style>
