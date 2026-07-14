<template>
  <div class="future-rewards">
    <p class="text-body-2 text-medium-emphasis mb-4">
      {{ t('student.achievements.futureRewardsIntro') }}
    </p>
    <v-row dense>
      <v-col v-for="item in items" :key="item.key" cols="12" sm="6">
        <div class="future-rewards__item pa-4 rounded-lg h-100">
          <div class="d-flex align-center gap-2 mb-2">
            <v-icon :color="item.color" size="20">{{ item.icon }}</v-icon>
            <span class="text-body-2 font-weight-bold">{{ item.title }}</span>
          </div>
          <p class="text-caption text-medium-emphasis mb-0">{{ item.description }}</p>
        </div>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const items = computed(() => [
  {
    key: 'specialTitles',
    icon: 'mdi-crown-outline',
    color: 'warning',
    title: t('student.achievements.futureRewardItems.specialTitles.title'),
    description: t('student.achievements.futureRewardItems.specialTitles.description'),
  },
  {
    key: 'leaderboards',
    icon: 'mdi-podium',
    color: 'secondary',
    title: t('student.achievements.futureRewardItems.leaderboards.title'),
    description: t('student.achievements.futureRewardItems.leaderboards.description'),
  },
  {
    key: 'competitions',
    icon: 'mdi-trophy-outline',
    color: 'success',
    title: t('student.achievements.futureRewardItems.competitions.title'),
    description: t('student.achievements.futureRewardItems.competitions.description'),
  },
  {
    key: 'rewards',
    icon: 'mdi-gift-outline',
    color: 'primary',
    title: t('student.achievements.futureRewardItems.rewards.title'),
    description: t('student.achievements.futureRewardItems.rewards.description'),
  },
  {
    key: 'platformPerks',
    icon: 'mdi-star-four-points',
    color: 'info',
    title: t('student.achievements.futureRewardItems.platformPerks.title'),
    description: t('student.achievements.futureRewardItems.platformPerks.description'),
  },
])
</script>

<style scoped>
.future-rewards__item {
  background: rgba(124, 108, 240, 0.06);
  border: 1px dashed rgba(124, 108, 240, 0.25);
}
</style>
