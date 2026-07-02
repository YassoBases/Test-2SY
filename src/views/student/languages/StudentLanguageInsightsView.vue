<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-brain"
      title="AI Insights"
      subtitle="Your personal coach, weaknesses, pronunciation and growth"
    />
    <LanguageModuleTabs />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg">{{ loadError }}</v-alert>

    <LoadingState v-if="loading" variant="cards" :count="3" class="mb-6" />

    <template v-else>
      <!-- KPI row -->
      <v-row class="mb-4">
        <v-col cols="6" sm="3">
          <v-card class="glass-card kpi-card pa-4 text-center" variant="flat">
            <div class="text-caption text-medium-emphasis">Effective level</div>
            <div class="text-h6 font-weight-bold">{{ difficulty?.effective_level || '—' }}</div>
          </v-card>
        </v-col>
        <v-col cols="6" sm="3">
          <v-card class="glass-card kpi-card kpi-card--warning pa-4 text-center" variant="flat">
            <div class="text-caption text-medium-emphasis">Primary focus</div>
            <div class="text-subtitle-1 font-weight-bold text-truncate">{{ coach?.primary_weakness || '—' }}</div>
          </v-card>
        </v-col>
        <v-col cols="6" sm="3">
          <v-card class="glass-card kpi-card kpi-card--success pa-4 text-center" variant="flat">
            <div class="text-caption text-medium-emphasis">Pronunciation</div>
            <div class="text-h6 font-weight-bold">{{ pron?.averages?.overall ?? '—' }}</div>
          </v-card>
        </v-col>
        <v-col cols="6" sm="3">
          <v-card class="glass-card kpi-card pa-4 text-center" variant="flat">
            <div class="text-caption text-medium-emphasis">Error trend</div>
            <div class="text-subtitle-1 font-weight-bold text-capitalize">{{ report?.trend || '—' }}</div>
          </v-card>
        </v-col>
      </v-row>

      <!-- Coach -->
      <section v-if="coach" class="section-block mb-4">
        <div class="section-block__head">
          <h3 class="section-block__title">Your coach</h3>
          <div class="section-block__subtitle">A personalized next step, updated as you learn</div>
        </div>
        <v-card class="glass-card pa-4" variant="flat">
          <p class="text-body-1 mb-3">{{ coach.coaching_message }}</p>
          <div v-if="coach.weekly_goal" class="mb-2">
            <v-icon size="18" color="secondary" class="mr-1">mdi-flag-checkered</v-icon>
            <strong>This week:</strong> {{ coach.weekly_goal }}
          </div>
          <div v-if="coach.recommended_activity" class="mb-2">
            <v-icon size="18" color="secondary" class="mr-1">mdi-target</v-icon>
            <strong>Try:</strong> {{ coach.recommended_activity }}
          </div>
          <div v-if="coach.recommended_vocabulary?.length" class="mt-3">
            <v-chip v-for="w in coach.recommended_vocabulary" :key="w" size="small" class="mr-1 mb-1" variant="tonal">{{ w }}</v-chip>
          </div>
          <v-btn size="small" variant="text" color="secondary" class="mt-2" :loading="refreshing" @click="refreshCoach">
            <v-icon start size="18">mdi-refresh</v-icon> Refresh advice
          </v-btn>
        </v-card>
      </section>

      <!-- Weaknesses -->
      <section class="section-block mb-4">
        <div class="section-block__head">
          <h3 class="section-block__title">Recurring mistakes</h3>
          <div class="section-block__subtitle">What to gently work on — tracked across all your sessions</div>
        </div>
        <v-card class="glass-card pa-4" variant="flat">
          <template v-if="topErrors.length">
            <div v-for="(e, i) in topErrors" :key="i" class="d-flex align-center mb-2">
              <v-chip size="x-small" :color="errorColor(e.error_type)" variant="tonal" class="mr-2 text-capitalize">{{ e.error_type }}</v-chip>
              <span class="flex-grow-1">{{ e.incorrect_form }}</span>
              <span class="text-medium-emphasis text-caption">×{{ e.occurrence_count }}</span>
            </div>
          </template>
          <EmptyState v-else preset="languageInsightsClear" compact />
        </v-card>
      </section>

      <!-- Pronunciation -->
      <section v-if="pron && pron.count" class="section-block mb-4">
        <div class="section-block__head">
          <h3 class="section-block__title">Pronunciation</h3>
          <div class="section-block__subtitle">Average over your last {{ pron.count }} attempts</div>
        </div>
        <v-card class="glass-card pa-4" variant="flat">
          <div v-for="dim in pronDims" :key="dim" class="mb-3">
            <div class="d-flex justify-space-between text-caption mb-1">
              <span class="text-capitalize">{{ dim }}</span>
              <span>{{ pron.averages[dim] }}</span>
            </div>
            <v-progress-linear :model-value="pron.averages[dim]" height="8" rounded color="secondary" bg-color="rgba(255,255,255,0.08)" />
          </div>
        </v-card>
      </section>

      <!-- Growth -->
      <section v-if="cefrPoints.length || vocabPoints.length" class="section-block mb-4">
        <div class="section-block__head">
          <h3 class="section-block__title">Growth</h3>
          <div class="section-block__subtitle">Your trajectory over time</div>
        </div>
        <v-row>
          <v-col cols="12" sm="6">
            <v-card class="glass-card pa-4" variant="flat">
              <div class="text-caption text-medium-emphasis mb-1">Overall CEFR</div>
              <div class="text-h6 font-weight-bold">
                {{ cefr?.summary?.start || '—' }} <v-icon size="18">mdi-arrow-right</v-icon> {{ cefr?.summary?.current || '—' }}
              </div>
              <div class="text-caption text-capitalize text-medium-emphasis">{{ cefr?.summary?.trend }}</div>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6">
            <v-card class="glass-card pa-4" variant="flat">
              <div class="text-caption text-medium-emphasis mb-1">Words learned</div>
              <div class="text-h6 font-weight-bold">
                {{ vocab?.summary?.start ?? '—' }} <v-icon size="18">mdi-arrow-right</v-icon> {{ vocab?.summary?.current ?? '—' }}
              </div>
              <div class="text-caption text-medium-emphasis">+{{ vocab?.summary?.change ?? 0 }}</div>
            </v-card>
          </v-col>
        </v-row>
      </section>

      <!-- Memory editor -->
      <section class="section-block mb-4">
        <div class="section-block__head">
          <h3 class="section-block__title">Tell your coach about you</h3>
          <div class="section-block__subtitle">Interests and goals personalize your lessons</div>
        </div>
        <v-card class="glass-card pa-4" variant="flat">
          <v-combobox
            v-model="memInterests" label="Interests" multiple chips closable-chips
            variant="outlined" density="comfortable" class="mb-3" hint="e.g. gaming, travel, technology" persistent-hint
          />
          <v-combobox
            v-model="memGoals" label="Learning goals" multiple chips closable-chips
            variant="outlined" density="comfortable" hint="e.g. reach B2 by summer" persistent-hint
          />
          <div class="d-flex align-center mt-3">
            <v-btn color="secondary" :loading="savingMemory" @click="saveMemory">Save</v-btn>
            <v-fade-transition><span v-if="memorySaved" class="text-success text-caption ml-3">Saved ✓</span></v-fade-transition>
          </div>
        </v-card>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import EmptyState from '../../../components/common/EmptyState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import {
  fetchCoachRecommendation,
  fetchErrorReport,
  fetchDifficultyProfile,
  fetchPronunciationTrends,
  fetchCefrProgress,
  fetchVocabularyGrowth,
  fetchLearnerMemory,
  updateLearnerMemory,
} from '../../../api/language.js'
import { useLanguageAccess } from '../../../composables/useLanguageAccess.js'
import { useLanguageGate } from '../../../composables/useLanguageGate.js'

const { access, loadAccess } = useLanguageAccess()
const { handleLanguageApiError, getErrorMessage } = useLanguageGate()

const loading = ref(true)
const loadError = ref('')
const refreshing = ref(false)
const savingMemory = ref(false)
const memorySaved = ref(false)

const coach = ref(null)
const report = ref(null)
const difficulty = ref(null)
const pron = ref(null)
const cefr = ref(null)
const vocab = ref(null)
const memory = ref(null)

const memInterests = ref([])
const memGoals = ref([])

const pronDims = ['clarity', 'fluency', 'pace', 'stress', 'intonation']
const topErrors = computed(() => {
  const r = report.value
  if (!r) return []
  return [...(r.top_grammar_errors || []), ...(r.top_vocabulary_errors || []), ...(r.top_pronunciation_errors || [])]
    .sort((a, b) => (b.occurrence_count || 0) - (a.occurrence_count || 0))
    .slice(0, 6)
})
const cefrPoints = computed(() => cefr.value?.data_points || [])
const vocabPoints = computed(() => vocab.value?.data_points || [])

function errorColor(type) {
  return type === 'pronunciation' ? 'warning' : type === 'vocabulary' ? 'info' : 'error'
}

async function refreshCoach() {
  refreshing.value = true
  try {
    coach.value = await fetchCoachRecommendation(true)
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Could not refresh advice')
  } finally {
    refreshing.value = false
  }
}

async function saveMemory() {
  savingMemory.value = true
  memorySaved.value = false
  try {
    memory.value = await updateLearnerMemory({
      interests: memInterests.value,
      learning_goals: memGoals.value,
    })
    memorySaved.value = true
    setTimeout(() => (memorySaved.value = false), 2500)
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Could not save')
  } finally {
    savingMemory.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    await loadAccess()
    const [c, r, d, p, cp, vg, m] = await Promise.allSettled([
      fetchCoachRecommendation(),
      fetchErrorReport(),
      fetchDifficultyProfile(),
      fetchPronunciationTrends(),
      fetchCefrProgress(),
      fetchVocabularyGrowth(),
      fetchLearnerMemory(),
    ])
    if (c.status === 'fulfilled') coach.value = c.value
    if (r.status === 'fulfilled') report.value = r.value
    if (d.status === 'fulfilled') difficulty.value = d.value
    if (p.status === 'fulfilled') pron.value = p.value
    if (cp.status === 'fulfilled') cefr.value = cp.value
    if (vg.status === 'fulfilled') vocab.value = vg.value
    if (m.status === 'fulfilled') {
      memory.value = m.value
      memInterests.value = m.value.interests || []
      memGoals.value = m.value.learning_goals || []
    }
    // Surface a gate redirect if every call failed because access was lost.
    const firstErr = [c, r, d, p, cp, vg, m].find((x) => x.status === 'rejected')
    if (firstErr && !coach.value && !report.value) {
      handleLanguageApiError(firstErr.reason, access.value)
    }
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) {
      loadError.value = getErrorMessage(e, 'Unable to load insights')
    }
  } finally {
    loading.value = false
  }
})
</script>
