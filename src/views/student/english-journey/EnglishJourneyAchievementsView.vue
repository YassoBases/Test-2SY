<template>
  <JourneyShell>
    <h1 class="ach-title">{{ t('student.englishJourney.achievements.title') }}</h1>

    <template v-if="loading && !progress">
      <v-skeleton-loader type="article" />
    </template>

    <JourneyEmptyState
      v-else-if="!progress?.overall_completed"
      icon="mdi-trophy-outline"
      :title="t('student.englishJourney.achievements.empty')"
      :action-label="t('student.englishJourney.hero.cta')"
      :action-to="homeTo"
    />

    <div v-else class="ach-grid">
      <AppCard solid padding="md">
        <p class="ach-label">{{ t('student.englishJourney.achievements.completedStages') }}</p>
        <p class="ach-value">
          {{ progress.overall_completed }} / {{ progress.overall_total }}
        </p>
      </AppCard>
      <AppCard solid padding="md">
        <p class="ach-label">{{ t('student.englishJourney.achievements.streak') }}</p>
        <p class="ach-value">{{ streakDays }}</p>
      </AppCard>
      <AppCard solid padding="md">
        <p class="ach-label">{{ t('student.englishJourney.achievements.confidence') }}</p>
        <p class="ach-value">{{ Math.round(averageConfidence) }}%</p>
      </AppCard>
      <AppCard solid padding="md">
        <p class="ach-label">{{ t('student.englishJourney.achievements.levelProgress') }}</p>
        <p class="ach-value eng-island" dir="ltr">
          {{ progress.cefr_label }} · {{ progress.level_percent }}%
        </p>
      </AppCard>
    </div>

    <template #sidebar>
      <AiTeacherSidebar
        :mission="teacherSession?.mission || null"
        :energy="teacherSession?.energy || null"
        :confidence="averageConfidence"
        :next-milestone="nextStage?.display_name || ''"
      />
    </template>
  </JourneyShell>
</template>

<script setup>
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useEnglishJourney } from '../../../composables/useEnglishJourney.js'
import { ROUTES } from '../../../constants/app.js'
import JourneyShell from '../../../components/english-journey/JourneyShell.vue'
import AiTeacherSidebar from '../../../components/english-journey/AiTeacherSidebar.vue'
import JourneyEmptyState from '../../../components/english-journey/JourneyEmptyState.vue'
import AppCard from '../../../components/ui/AppCard.vue'

const { t } = useI18n()
const homeTo = ROUTES.STUDENT_ENGLISH_JOURNEY

const {
  loading,
  progress,
  streakDays,
  averageConfidence,
  teacherSession,
  nextStage,
  loadJourney,
} = useEnglishJourney()

onMounted(() => loadJourney())
</script>

<style scoped>
.ach-title {
  margin: 0 0 20px;
  font-size: 1.5rem;
}

.ach-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.ach-label {
  margin: 0 0 8px;
  font-size: 0.8125rem;
  color: var(--text-muted, #3f4f63);
}

.ach-value {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
