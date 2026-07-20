<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-history"
      title="Placement history"
      subtitle="Read-only results from your completed legacy and AI placement assessments"
    />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg">
      {{ loadError }}
    </v-alert>

    <LoadingState v-if="loading" variant="cards" :count="2" class="mb-6" />

    <v-alert
      v-else-if="!history.length"
      type="info"
      variant="tonal"
      class="rounded-lg"
    >
      No consistent historical placement result is available. No result was reconstructed from
      current learning analytics.
    </v-alert>

    <div v-else class="d-flex flex-column gap-4">
      <v-card
        v-for="result in history"
        :key="result.record_id"
        class="glass-card pa-6"
        variant="flat"
      >
        <div class="d-flex align-center justify-space-between flex-wrap gap-3 mb-5">
          <div>
            <div class="text-h6 font-weight-bold">Placement result</div>
            <div class="text-caption text-medium-emphasis mt-1">
              {{ formatDate(result.completed_at) }}
              <span aria-hidden="true"> · </span>
              {{ result.overall_calculation_method }}
            </div>
          </div>
          <div class="d-flex align-center gap-2">
            <v-chip size="small" variant="tonal" color="info">
              {{ sourceLabel(result.source) }}
            </v-chip>
            <v-chip color="secondary" variant="flat">
              Overall: {{ result.overall_level }}
            </v-chip>
          </div>
        </div>

        <v-row>
          <v-col v-for="score in result.skills" :key="score.skill" cols="6" sm="3">
            <div class="skill-level-box text-center pa-3 rounded-lg h-100">
              <div class="text-caption text-medium-emphasis">{{ skillLabel(score.skill) }}</div>
              <div class="text-h6 font-weight-bold text-secondary">{{ score.level }}</div>
              <div class="text-caption text-medium-emphasis">
                {{ formatScore(score.score_percent) }}%
              </div>
            </div>
          </v-col>
        </v-row>
      </v-card>
    </div>

    <div class="d-flex gap-2 flex-wrap mt-6">
      <v-btn color="secondary" variant="flat" @click="router.push(ROUTES.STUDENT_LANGUAGES)">
        Return to languages
      </v-btn>
      <v-btn variant="tonal" @click="router.push(ROUTES.STUDENT_LANGUAGES_EXAM)">
        Open AI placement exam
      </v-btn>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import { getErrorMessage } from '../../../api/client.js'
import { fetchPlacementHistory } from '../../../api/language.js'
import { ROUTES } from '../../../constants/app.js'

const router = useRouter()
const loading = ref(true)
const loadError = ref('')
const history = ref([])

const skillLabels = {
  reading: 'Reading',
  listening: 'Listening',
  writing: 'Writing',
  speaking: 'Speaking',
}

function skillLabel(skill) {
  return skillLabels[skill] || skill
}

function sourceLabel(source) {
  return source === 'ai_exam' ? 'AI exam' : 'Legacy history'
}

function formatDate(value) {
  if (!value) return 'Date unavailable'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Date unavailable'
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(date)
}

function formatScore(value) {
  const score = Number(value)
  return Number.isFinite(score) ? Math.round(score * 10) / 10 : 0
}

onMounted(async () => {
  try {
    const payload = await fetchPlacementHistory()
    history.value = payload?.available && Array.isArray(payload.results) ? payload.results : []
  } catch (error) {
    loadError.value = getErrorMessage(error, 'Placement history could not be loaded')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.page-container {
  max-width: 960px;
  margin: 0 auto;
}

.skill-level-box {
  background: rgba(var(--v-theme-on-surface), 0.04);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}
</style>
