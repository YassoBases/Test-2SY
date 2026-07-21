<template>
  <JourneyShell>
    <template v-if="!session">
      <JourneyEmptyState
        icon="mdi-play-circle-outline"
        :title="t('student.englishJourney.session.empty')"
        :action-label="t('student.englishJourney.session.backHome')"
        :action-to="homeTo"
      />
    </template>

    <template v-else>
      <header class="session-view__header">
        <h1>{{ t('student.englishJourney.session.title') }}</h1>
        <p v-if="session.current_grammar_name" class="eng-island text-medium-emphasis" dir="ltr">
          {{ session.current_grammar_name }}
        </p>
      </header>

      <MissionCard :mission="session.mission" class="mb-4" />

      <AppCard solid padding="md" class="mb-4">
        <ol class="session-view__sections">
          <li v-for="(sec, i) in session.sections || []" :key="`${sec.kind}-${i}`">
            <div class="session-view__sec-title eng-island" dir="ltr">
              {{ sec.title || sec.kind }}
            </div>
            <p v-if="sec.purpose" class="session-view__sec-purpose eng-island" dir="ltr">
              {{ sec.purpose }}
            </p>
            <span v-if="sec.estimated_minutes" class="session-view__mins text-medium-emphasis">
              {{ sec.estimated_minutes }}′
            </span>
          </li>
        </ol>
      </AppCard>

      <AppButton variant="primary" size="large" @click="onComplete">
        {{ t('student.englishJourney.session.complete') }}
      </AppButton>
    </template>

    <template #sidebar>
      <AiTeacherSidebar
        :mission="session?.mission || null"
        :energy="session?.energy || null"
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
import MissionCard from '../../../components/english-journey/MissionCard.vue'
import AiTeacherSidebar from '../../../components/english-journey/AiTeacherSidebar.vue'
import JourneyEmptyState from '../../../components/english-journey/JourneyEmptyState.vue'
import AppCard from '../../../components/ui/AppCard.vue'
import AppButton from '../../../components/ui/AppButton.vue'

const { t } = useI18n()
const homeTo = ROUTES.STUDENT_ENGLISH_JOURNEY

const {
  teacherSession,
  averageConfidence,
  nextStage,
  hydrateSession,
  finishSession,
  loadJourney,
} = useEnglishJourney()

const session = computed(() => teacherSession.value)

onMounted(async () => {
  hydrateSession()
  if (!teacherSession.value) {
    await loadJourney({ withAdaptive: true, withTeacherStatus: true })
  }
})

async function onComplete() {
  await finishSession()
}
</script>

<style scoped>
.session-view__header {
  margin-block-end: 20px;
}

.session-view__header h1 {
  margin: 0 0 4px;
  font-size: 1.5rem;
}

.session-view__sections {
  margin: 0;
  padding-inline-start: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.session-view__sec-title {
  font-weight: 600;
}

.session-view__sec-purpose {
  margin: 4px 0 0;
  font-size: 0.875rem;
  color: var(--text-muted, #3f4f63);
}

.session-view__mins {
  font-size: 0.8125rem;
}

.eng-island {
  unicode-bidi: isolate;
}
</style>
