<template>
  <div class="achievements-page slide-up-enter-active">
    <PageHeader
      :eyebrow="t('student.achievements.header.eyebrow')"
      eyebrow-icon="mdi-trophy"
      :title="t('student.achievements.header.title')"
      :subtitle="t('student.achievements.header.subtitle')"
      gradient-title
    />

    <v-alert v-if="error" type="error" variant="tonal" class="mb-5 rounded-lg">{{ error }}</v-alert>
    <LoadingState v-if="loading" variant="cards" :count="3" class="mb-6" />

    <template v-else-if="profile">
      <v-card class="glass-card hero-card pa-5 mb-6" variant="flat">
        <v-row align="center">
          <v-col cols="12" md="4" class="text-center text-md-start">
            <div class="hero-level">
              <span class="hero-level__num">{{ profile.level }}</span>
            </div>
            <div class="text-h5 font-weight-bold mt-2">{{ t('student.achievements.level', { n: profile.level }) }}</div>
            <div class="text-body-2 text-medium-emphasis">
              {{ t('student.achievements.totalXp', { xp: profile.total_xp?.toLocaleString() }) }}
            </div>
          </v-col>
          <v-col cols="12" md="8">
            <div class="d-flex justify-space-between text-body-2 mb-2">
              <span>{{ t('student.achievements.levelProgress') }}</span>
              <span v-if="!profile.is_max_level" class="text-medium-emphasis">
                {{ t('student.achievements.xpToNext', { xp: profile.xp_to_next_level?.toLocaleString(), n: profile.level + 1 }) }}
              </span>
              <span v-else class="text-success">{{ t('student.achievements.maxLevel') }}</span>
            </div>
            <v-progress-linear
              :model-value="profile.progress_percent"
              color="secondary"
              height="10"
              rounded
              class="mb-3"
            />
            <div class="d-flex flex-wrap gap-4">
              <v-chip color="warning" variant="tonal" size="small">
                {{ profile.streak_display || t('student.achievements.streakDaysShort', { n: profile.current_streak }) }}
              </v-chip>
              <v-chip color="primary" variant="tonal" size="small">
                {{ t('student.achievements.longestStreak', { n: profile.longest_streak }) }}
              </v-chip>
              <v-chip color="secondary" variant="tonal" size="small">
                {{ t('student.achievements.badgeCount', { earned: profile.achievement_count, total: profile.badges?.length || 0 }) }}
              </v-chip>
            </div>
          </v-col>
        </v-row>
      </v-card>

      <v-row class="mb-6">
        <v-col cols="12" md="6">
          <section class="section-block">
            <div class="section-block__head">
              <h3 class="section-block__title">{{ t('student.achievements.sections.recentXp') }}</h3>
              <p class="section-block__subtitle mb-0">{{ t('student.achievements.sections.recentXpSubtitle') }}</p>
            </div>
            <v-card class="glass-card pa-4" variant="flat">
              <RecentXpActivity :items="profile.recent_activity || []" />
            </v-card>
          </section>
        </v-col>
        <v-col cols="12" md="6">
          <section class="section-block">
            <div class="section-block__head">
              <h3 class="section-block__title">{{ t('student.achievements.sections.streak') }}</h3>
              <p class="section-block__subtitle mb-0">{{ t('student.achievements.sections.streakSubtitle') }}</p>
            </div>
            <v-card class="glass-card pa-5 text-center streak-card" variant="flat">
              <div class="streak-card__flame">🔥</div>
              <div class="text-h3 font-weight-bold text-warning">{{ profile.current_streak }}</div>
              <div class="text-body-2 text-medium-emphasis mb-3">{{ t('student.achievements.sections.streakDays') }}</div>
              <v-progress-linear
                :model-value="streakProgress"
                color="warning"
                height="6"
                rounded
              />
              <div class="text-caption text-medium-emphasis mt-2">
                {{ t('student.achievements.sections.streakGoal') }}
              </div>
            </v-card>
          </section>
        </v-col>
      </v-row>

      <section class="section-block mb-6">
        <div class="section-block__head">
          <h3 class="section-block__title">{{ t('student.achievements.sections.badges') }}</h3>
          <p class="section-block__subtitle mb-0">{{ t('student.achievements.sections.badgesSubtitle') }}</p>
        </div>
        <v-card class="glass-card pa-4" variant="flat">
          <AchievementBadgeGrid :badges="profile.badges || []" />
        </v-card>
      </section>

      <v-row>
        <v-col cols="12" lg="7">
          <section class="section-block mb-6">
            <div class="section-block__head">
              <h3 class="section-block__title">{{ t('student.achievements.sections.xpRules') }}</h3>
              <p class="section-block__subtitle mb-0">{{ t('student.achievements.sections.xpRulesSubtitle') }}</p>
            </div>
            <v-card class="glass-card pa-4" variant="flat">
              <XpRulesList :rules="profile.xp_rules || []" />
            </v-card>
          </section>
        </v-col>
        <v-col cols="12" lg="5">
          <section class="section-block mb-6">
            <div class="section-block__head">
              <h3 class="section-block__title">{{ t('student.achievements.sections.futureRewards') }}</h3>
              <p class="section-block__subtitle mb-0">{{ t('student.achievements.sections.futureRewardsSubtitle') }}</p>
            </div>
            <v-card class="glass-card pa-4" variant="flat">
              <FutureRewardsInfo />
            </v-card>
          </section>
        </v-col>
      </v-row>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import PageHeader from '../../components/common/PageHeader.vue'
import LoadingState from '../../components/common/LoadingState.vue'
import AchievementBadgeGrid from '../../components/gamification/AchievementBadgeGrid.vue'
import RecentXpActivity from '../../components/gamification/RecentXpActivity.vue'
import XpRulesList from '../../components/gamification/XpRulesList.vue'
import FutureRewardsInfo from '../../components/gamification/FutureRewardsInfo.vue'
import { useGamification } from '../../composables/useGamification.js'
import { isApiMode } from '../../utils/session.js'

const { t } = useI18n()
const { profile, loading, error, load } = useGamification()

const streakProgress = computed(() => {
  const days = profile.value?.current_streak || 0
  return Math.min(100, Math.round((days / 30) * 100))
})

onMounted(() => {
  if (isApiMode()) load()
})
</script>

<style scoped>
.achievements-page {
  max-width: 1100px;
}

.hero-card {
  border: 1px solid rgba(124, 108, 240, 0.3);
}

.hero-level {
  width: 88px;
  height: 88px;
  margin: 0 auto;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(124, 108, 240, 0.4), rgba(34, 211, 238, 0.3));
  border: 2px solid rgba(124, 108, 240, 0.55);
  box-shadow: 0 0 24px rgba(124, 108, 240, 0.25);
}

@media (min-width: 960px) {
  .hero-level {
    margin: 0;
  }
}

.hero-level__num {
  font-size: 2rem;
  font-weight: 800;
  color: var(--em-cyan);
}

.streak-card {
  min-height: 220px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.streak-card__flame {
  font-size: 2.5rem;
  line-height: 1;
}
</style>
