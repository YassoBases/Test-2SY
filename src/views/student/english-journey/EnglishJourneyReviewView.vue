<template>
  <JourneyShell>
    <h1 class="review-title">{{ t('student.englishJourney.review.title') }}</h1>

    <template v-if="loading && !levels.length">
      <v-skeleton-loader type="article" />
    </template>

    <JourneyEmptyState
      v-else-if="!completedStages.length"
      icon="mdi-book-open-page-variant-outline"
      :title="t('student.englishJourney.review.empty')"
      :description="t('student.englishJourney.review.emptyHint')"
      :action-label="t('student.englishJourney.session.backHome')"
      :action-to="homeTo"
    />

    <div v-else class="review-groups">
      <section v-for="group in reviewGroups" :key="group.cefr" class="review-group">
        <h2 class="review-group__cefr eng-island" dir="ltr">{{ group.cefr }}</h2>
        <div class="review-group__grid">
          <StageCard
            v-for="stage in group.stages"
            :key="stage.grammar_id"
            :stage="stage"
            @select="openStage(stage.grammar_id)"
          />
        </div>
      </section>
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
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useEnglishJourney } from '../../../composables/useEnglishJourney.js'
import { ROUTES } from '../../../constants/app.js'
import JourneyShell from '../../../components/english-journey/JourneyShell.vue'
import StageCard from '../../../components/english-journey/StageCard.vue'
import AiTeacherSidebar from '../../../components/english-journey/AiTeacherSidebar.vue'
import JourneyEmptyState from '../../../components/english-journey/JourneyEmptyState.vue'

const CEFR_ORDER = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

const { t } = useI18n()
const homeTo = ROUTES.STUDENT_ENGLISH_JOURNEY

const {
  loading,
  levels,
  completedStages,
  completedByLevel,
  teacherSession,
  averageConfidence,
  nextStage,
  loadJourney,
  openStage,
} = useEnglishJourney()

const reviewGroups = computed(() =>
  CEFR_ORDER.filter((cefr) => (completedByLevel.value[cefr] || []).length).map((cefr) => ({
    cefr,
    stages: completedByLevel.value[cefr],
  })),
)

onMounted(() => loadJourney())
</script>

<style scoped>
.review-title {
  margin: 0 0 20px;
  font-size: 1.5rem;
}

.review-groups {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.review-group__cefr {
  margin: 0 0 12px;
  font-size: 1.25rem;
  color: var(--color-primary-deep, #4f46e5);
}

.review-group__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
