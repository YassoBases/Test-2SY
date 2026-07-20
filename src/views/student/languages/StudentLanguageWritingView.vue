<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-pencil"
      title="Writing"
      subtitle="Personalized writing practice based on your placement result"
    />
    <LanguageModuleTabs />

    <v-alert v-if="focus" type="success" variant="tonal" class="mb-4 rounded-lg" density="comfortable" icon="mdi-target">
      Practising: <strong>{{ focus }}</strong>
    </v-alert>
    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4">{{ loadError }}</v-alert>
    <LoadingState v-if="loading" variant="cards" :count="3" class="mb-6" />

    <template v-else>
      <section v-if="writingProfile" class="section-block">
        <div class="section-block__head">
          <div>
            <h3 class="section-block__title">Writing path</h3>
            <p class="section-block__subtitle mb-0">Next focus: {{ nextFocusLabel }}</p>
          </div>
        </div>
        <div class="profile-strip">
          <div class="profile-stat">
            <span>Practice level</span>
            <strong>{{ writingProfile.practice_level || writingProfile.level || studentLevel }}</strong>
            <small v-if="writingProfile.level && writingProfile.practice_level && writingProfile.level !== writingProfile.practice_level">
              placement {{ writingProfile.level }}
            </small>
          </div>
          <div class="profile-stat">
            <span>Practice</span>
            <strong>{{ writingProfile.completed_prompts || 0 }}/{{ writingProfile.total_prompts || prompts.length }}</strong>
          </div>
          <div class="profile-stat">
            <span>Average</span>
            <strong>{{ writingProfile.average_score_percent != null ? `${writingProfile.average_score_percent}%` : '-' }}</strong>
          </div>
        </div>
        <div class="path-grid mt-4">
          <div v-if="profileBreakdown.length" class="profile-panel">
            <div class="profile-panel__title">Skill profile</div>
            <div v-for="item in profileBreakdown" :key="item.code" class="skill-row">
              <div class="d-flex justify-space-between text-caption mb-1">
                <span>{{ item.label }}</span>
                <strong>{{ item.score_percent }}%</strong>
              </div>
              <v-progress-linear :model-value="item.score_percent" height="7" rounded color="secondary" />
            </div>
          </div>

          <div v-if="planSteps.length" class="profile-panel">
            <div class="profile-panel__title">Next path</div>
            <div v-for="step in planSteps" :key="step.order" class="plan-step">
              <v-icon size="18" :color="step.status === 'current' ? 'secondary' : 'medium-emphasis'">
                {{ step.status === 'checkpoint' ? 'mdi-flag-checkered' : step.status === 'rewrite' ? 'mdi-refresh' : 'mdi-target' }}
              </v-icon>
              <div>
                <strong>{{ step.title }}</strong>
                <span>{{ step.description }}</span>
              </div>
            </div>
          </div>

          <div v-if="checkpointStatus" class="profile-panel">
            <div class="d-flex justify-space-between align-center mb-2">
              <div class="profile-panel__title mb-0">Level checkpoint</div>
              <v-chip size="small" :color="checkpointStatus.ready ? 'success' : 'secondary'" variant="tonal">
                {{ checkpointStatus.next_level || 'C2' }}
              </v-chip>
            </div>
            <v-progress-linear :model-value="checkpointProgress" height="9" rounded color="secondary" />
            <div class="text-caption mt-2">
              {{ checkpointStatus.completed_prompts || 0 }}/{{ checkpointStatus.required_prompts || 6 }} tasks,
              {{ checkpointStatus.improved_rewrites || 0 }}/{{ checkpointStatus.required_rewrites || 2 }} rewrites
            </div>
            <div v-if="checkpointStatus.missing?.length" class="text-caption text-medium-emphasis mt-2">
              {{ checkpointStatus.missing[0] }}
            </div>
          </div>
        </div>
      </section>

      <v-row>
        <v-col cols="12" md="4">
          <section class="section-block">
            <div class="section-block__head">
              <h3 class="section-block__title">Exercises</h3>
            </div>
            <v-list density="comfortable" class="glass-card pa-0">
              <v-list-item
                v-for="p in prompts"
                :key="p.id"
                :active="selectedId === p.id"
                rounded="lg"
                @click="selectPrompt(p.id)"
              >
                <template #prepend>
                  <v-icon :color="p.recommended ? 'secondary' : 'medium-emphasis'">
                    {{ p.progress?.completed_at ? 'mdi-check-circle' : 'mdi-pencil-outline' }}
                  </v-icon>
                </template>
                <v-list-item-title class="d-flex align-center ga-2">
                  <span>{{ p.title }}</span>
                  <v-chip v-if="p.recommended" color="secondary" size="x-small" variant="flat">Next</v-chip>
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ p.target_focus || p.level }}
                  <span v-if="p.progress?.score_percent != null"> - {{ Math.round(p.progress.score_percent) }}%</span>
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
            <EmptyState v-if="!prompts.length" compact preset="languageExercise" />
          </section>
        </v-col>

        <v-col cols="12" md="8">
          <EmptyState
            v-if="!selectedId && prompts.length"
            compact
            icon="mdi-cursor-default-click-outline"
            title="Choose an exercise"
            description="Select an exercise from the list to begin."
          />
          <v-card v-else-if="prompt" class="glass-card pa-6" variant="flat">
            <div class="d-flex align-start justify-space-between ga-3 flex-wrap mb-3">
              <div>
                <div class="text-caption text-medium-emphasis mb-1">{{ prompt.task_type }} - {{ prompt.topic }}</div>
                <h3 class="text-h6 mb-1">{{ prompt.title }}</h3>
                <div class="text-caption">Focus: {{ prompt.target_focus }}</div>
              </div>
              <v-chip v-if="prompt.recommended" color="secondary" variant="flat" prepend-icon="mdi-target">Recommended</v-chip>
            </div>

            <v-alert
              v-if="prompt.recommendation_reason || prompt.practice_hint"
              type="info"
              variant="tonal"
              density="comfortable"
              class="mb-4 rounded-lg"
            >
              {{ prompt.recommendation_reason || prompt.practice_hint }}
            </v-alert>

            <div v-if="prompt.mini_lesson" class="lesson-panel mb-4">
              <div class="profile-panel__title">{{ prompt.mini_lesson.title }}</div>
              <p class="text-body-2 mb-2">{{ prompt.mini_lesson.explanation }}</p>
              <div v-if="prompt.mini_lesson.examples?.length" class="example-list">
                <span v-for="example in prompt.mini_lesson.examples" :key="example">{{ example }}</span>
              </div>
              <div v-if="prompt.mini_lesson.micro_practice" class="text-caption mt-2">
                {{ prompt.mini_lesson.micro_practice }}
              </div>
            </div>

            <div v-if="wordBank.length || sentenceStarters.length" class="scaffold-grid mb-4">
              <div v-if="wordBank.length" class="scaffold-panel">
                <div class="text-caption font-weight-bold mb-2">Word bank</div>
                <div class="chip-wrap">
                  <v-chip v-for="word in wordBank" :key="word" size="small" variant="tonal">{{ word }}</v-chip>
                </div>
              </div>
              <div v-if="sentenceStarters.length" class="scaffold-panel">
                <div class="text-caption font-weight-bold mb-2">Sentence starters</div>
                <div class="starter-list">
                  <span v-for="starter in sentenceStarters" :key="starter">{{ starter }}</span>
                </div>
              </div>
            </div>

            <div v-if="checklist.length" class="checklist-row mb-4">
              <span v-for="item in checklist" :key="item">
                <v-icon size="16" color="secondary">mdi-check-circle-outline</v-icon>
                {{ item }}
              </span>
            </div>

            <div class="text-body-1 font-weight-medium mb-3" dir="ltr">{{ prompt.prompt }}</div>
            <div class="text-caption mb-2">
              minimum: {{ prompt.min_words }} words - {{ prompt.min_sentences }} sentences
            </div>
            <v-textarea v-model="text" rows="8" auto-grow dir="ltr" />
            <div class="d-flex align-center justify-space-between ga-3 flex-wrap mt-2">
              <div class="text-caption">words: {{ wordCount }} - sentences: {{ sentenceCount }}</div>
              <v-btn
                color="secondary"
                :loading="submitting"
                :disabled="!canSubmit"
                prepend-icon="mdi-send"
                @click="submit"
              >
                {{ submitLabel }}
              </v-btn>
            </div>
            <v-alert
              v-if="validationMessage"
              type="warning"
              variant="tonal"
              density="comfortable"
              class="mt-3 rounded-lg"
              dir="ltr"
            >
              {{ validationMessage }}
            </v-alert>

            <v-alert v-if="result || currentFeedback" class="mt-4" :type="currentPassed ? 'success' : 'warning'" variant="tonal">
              <div class="font-weight-bold mb-1">
                Result: {{ currentScore }}% - {{ currentPassed ? 'complete' : 'rewrite recommended' }}
              </div>
              <div v-if="currentAttemptNumber" class="text-caption mb-1">
                Draft {{ currentAttemptNumber }}
                <span v-if="currentImprovement != null"> - improvement {{ currentImprovement > 0 ? '+' : '' }}{{ currentImprovement }}%</span>
              </div>
              <div>{{ currentFeedback }}</div>
              <div v-if="currentNextFocus" class="mt-2 text-caption">
                Next focus: {{ currentNextFocus }}
              </div>
              <div v-if="currentRewritePrompt" class="mt-2 text-caption">
                {{ currentRewritePrompt }}
              </div>
            </v-alert>

            <div v-if="criteriaEntries.length" class="criteria-box mt-4">
              <div v-for="c in criteriaEntries" :key="c.key" class="criterion-row">
                <div class="d-flex justify-space-between text-caption mb-1">
                  <span>{{ c.label }}</span>
                  <strong>{{ c.value }}%</strong>
                </div>
                <v-progress-linear :model-value="c.value" height="8" rounded color="secondary" />
              </div>
            </div>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import EmptyState from '../../../components/common/EmptyState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import { fetchWritingPrompt, fetchWritingPrompts, submitWritingPrompt } from '../../../api/language.js'
import { useLanguageGate } from '../../../composables/useLanguageGate.js'
import { useLanguageAccess } from '../../../composables/useLanguageAccess.js'
import {
  countWritingSentences,
  countWritingWords,
  minWordsRequiredMessage,
  validateWritingText,
} from '../../../utils/languageValidation.js'

const router = useRouter()
const route = useRoute()
const focus = ref(route.query.focus ? String(route.query.focus) : '')
const { access, loadAccess } = useLanguageAccess()
const { handleLanguageApiError, getErrorMessage } = useLanguageGate()

const prompts = ref([])
const studentLevel = ref('')
const writingProfile = ref(null)
const recommendedPromptId = ref(null)
const loading = ref(true)
const loadError = ref('')
const selectedId = ref(null)
const prompt = ref(null)
const text = ref('')
const submitting = ref(false)
const result = ref(null)

const CRITERION_LABELS = {
  task_achievement: 'Task',
  coherence_cohesion: 'Organization',
  grammar_accuracy: 'Grammar accuracy',
  grammar_range: 'Grammar range',
  lexical_resource: 'Vocabulary',
  mechanics: 'Spelling and punctuation',
}

const wordCount = computed(() => countWritingWords(text.value))
const sentenceCount = computed(() => countWritingSentences(text.value))
const nextFocusLabel = computed(() => writingProfile.value?.next_focus?.label || 'Build a stronger draft')
const profileBreakdown = computed(() => writingProfile.value?.skill_breakdown || [])
const planSteps = computed(() => writingProfile.value?.plan_steps || [])
const checkpointStatus = computed(() => writingProfile.value?.checkpoint || null)
const checkpointProgress = computed(() => Math.max(0, Math.min(100, Math.round(Number(checkpointStatus.value?.progress_percent) || 0))))
const wordBank = computed(() => prompt.value?.word_bank || [])
const sentenceStarters = computed(() => prompt.value?.sentence_starters || [])
const checklist = computed(() => prompt.value?.checklist || [])
const currentAttemptNumber = computed(() => result.value?.attempt_number || prompt.value?.progress?.attempt_number || 0)
const currentImprovement = computed(() => result.value?.improvement_percent ?? prompt.value?.progress?.improvement_percent ?? null)
const currentRewritePrompt = computed(() => result.value?.rewrite_prompt || prompt.value?.progress?.rewrite_prompt || '')
const hasPreviousDraft = computed(() => Number(prompt.value?.progress?.attempt_count || 0) > 0)
const submitLabel = computed(() => hasPreviousDraft.value ? 'Send rewrite' : 'Send draft')

const validationMessage = computed(() => {
  if (!prompt.value || !text.value.trim()) return ''
  const check = validateWritingText(text.value, {
    minWords: prompt.value.min_words,
    minSentences: prompt.value.min_sentences,
  })
  return check.ok ? '' : check.message
})

const canSubmit = computed(() => {
  if (!prompt.value || !text.value.trim()) return false
  return validateWritingText(text.value, {
    minWords: prompt.value.min_words,
    minSentences: prompt.value.min_sentences,
  }).ok
})

const currentCriteria = computed(() => result.value?.criteria || prompt.value?.progress?.criteria || {})
const criteriaEntries = computed(() => Object.entries(currentCriteria.value).map(([key, raw]) => ({
  key,
  label: CRITERION_LABELS[key] || key.replaceAll('_', ' '),
  value: Math.max(0, Math.min(100, Math.round(Number(raw) || 0))),
})))
const currentFeedback = computed(() => result.value?.feedback || prompt.value?.progress?.feedback || '')
const currentScore = computed(() => Math.round(result.value?.score_percent ?? prompt.value?.progress?.score_percent ?? 0))
const currentPassed = computed(() => Boolean(result.value?.passed || prompt.value?.progress?.completed_at))
const currentNextFocus = computed(() => result.value?.next_focus?.label || prompt.value?.progress?.metrics?.next_focus?.label || '')

function applyWritingList(res) {
  prompts.value = res.prompts || []
  studentLevel.value = res.student_level || ''
  writingProfile.value = res.writing_profile || null
  recommendedPromptId.value = res.recommended_prompt_id || prompts.value.find((p) => p.recommended)?.id || null
}

onMounted(async () => {
  try {
    await loadAccess(true)
    if (access.value?.redirect) {
      router.push(access.value.redirect)
      return
    }
    const res = await fetchWritingPrompts()
    applyWritingList(res)
    const firstId = recommendedPromptId.value || prompts.value[0]?.id
    if (firstId) await selectPrompt(firstId)
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) {
      loadError.value = getErrorMessage(e, 'Unable to download')
    }
  } finally {
    loading.value = false
  }
})

async function selectPrompt(id) {
  selectedId.value = id
  result.value = null
  loadError.value = ''
  try {
    prompt.value = await fetchWritingPrompt(id)
    const listItem = prompts.value.find((p) => p.id === id)
    if (listItem) {
      prompt.value = { ...listItem, ...prompt.value, recommended: listItem.recommended }
    }
    text.value = prompt.value.progress?.submitted_text || ''
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) {
      loadError.value = getErrorMessage(e, 'Unable to load the exercise')
    }
  }
}

async function submit() {
  if (!selectedId.value || !prompt.value) return
  const check = validateWritingText(text.value, {
    minWords: prompt.value.min_words,
    minSentences: prompt.value.min_sentences,
  })
  if (!check.ok) {
    loadError.value = check.message || minWordsRequiredMessage(prompt.value.min_words)
    return
  }
  submitting.value = true
  loadError.value = ''
  try {
    result.value = await submitWritingPrompt(selectedId.value, text.value)
    const res = await fetchWritingPrompts()
    applyWritingList(res)
    const refreshedPrompt = await fetchWritingPrompt(selectedId.value)
    const listItem = prompts.value.find((p) => p.id === selectedId.value)
    prompt.value = { ...(listItem || {}), ...refreshedPrompt }
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Unable to send')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.page-container {
  max-width: 1100px;
  margin: 0 auto;
}

.profile-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.profile-stat {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 8px;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.72);
}

.profile-stat span {
  display: block;
  color: rgba(var(--v-theme-on-surface), 0.64);
  font-size: 0.78rem;
}

.profile-stat strong {
  display: block;
  margin-top: 4px;
  font-size: 1.05rem;
}

.profile-stat small {
  display: block;
  margin-top: 2px;
  color: rgba(var(--v-theme-on-surface), 0.52);
  font-size: 0.72rem;
}

.path-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.profile-panel,
.lesson-panel,
.scaffold-panel {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.72);
  padding: 12px;
}

.profile-panel__title {
  font-size: 0.82rem;
  font-weight: 800;
  margin-bottom: 10px;
}

.skill-row + .skill-row,
.plan-step + .plan-step {
  margin-top: 10px;
}

.plan-step {
  display: grid;
  grid-template-columns: 22px 1fr;
  gap: 8px;
  align-items: start;
}

.plan-step strong,
.plan-step span {
  display: block;
}

.plan-step strong {
  font-size: 0.84rem;
}

.plan-step span {
  color: rgba(var(--v-theme-on-surface), 0.62);
  font-size: 0.74rem;
  line-height: 1.35;
}

.example-list,
.chip-wrap,
.checklist-row,
.starter-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.example-list span,
.starter-list span,
.checklist-row span {
  border-radius: 8px;
  background: rgba(var(--v-theme-secondary), 0.1);
  color: rgb(var(--v-theme-on-surface));
  padding: 6px 8px;
  font-size: 0.8rem;
}

.checklist-row span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.scaffold-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.criteria-box {
  display: grid;
  gap: 12px;
}

@media (max-width: 700px) {
  .profile-strip,
  .path-grid,
  .scaffold-grid {
    grid-template-columns: 1fr;
  }
}
</style>
