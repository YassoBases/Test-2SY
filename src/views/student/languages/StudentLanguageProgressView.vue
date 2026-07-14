<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-chart-line"
      title="Progress"
      subtitle="Your levels and growth towards the next level"
    />
    <LanguageModuleTabs />

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-4 rounded-lg">{{ loadError }}</v-alert>

    <LoadingState v-if="loading" variant="cards" :count="3" class="mb-6" />

    <template v-else-if="data">
      <v-row class="mb-4">
        <v-col cols="6" sm="4" md="2">
          <v-card class="glass-card kpi-card pa-3 text-center" variant="flat">
            <div class="text-caption text-medium-emphasis">General level</div>
            <div class="text-h6 font-weight-bold">{{ data.overall_level || '—' }}</div>
          </v-card>
        </v-col>
        <v-col v-for='skill in levelSkills' :key="skill.key" cols="6" sm="4" md="2">
          <v-card class="glass-card kpi-card pa-3 text-center" variant="flat">
            <div class="text-caption text-medium-emphasis">{{ skill.label }}</div>
            <div class="text-h6 font-weight-bold">{{ skill.level || '—' }}</div>
            <div class='text-caption text-secondary mt-1'>
              growth: {{ growthPercent(skill.key) }}%
            </div>
          </v-card>
        </v-col>
      </v-row>

      <v-card v-if="adaptiveSkills.length" class="glass-card pa-4 mb-4" variant="flat">
        <div class="text-subtitle-2 font-weight-bold mb-2">Adaptive difficulty</div>
        <div class="d-flex flex-wrap gap-2">
          <v-chip
            v-for="s in adaptiveSkills"
            :key="s.key"
            size="small"
            variant="tonal"
            :color="s.passes_to_promote === 0 ? 'success' : 'secondary'"
          >
            {{ s.label }}: {{ s.current_level }}
            <span class="ml-1 text-caption">· {{ s.passes_to_promote }}↑ {{ s.fails_to_demote }}↓</span>
          </v-chip>
        </div>
        <div class="text-caption text-medium-emphasis mt-2">
          ↑ strong lessons (≥85%) left to level up · ↓ weak lessons (&lt;55%) before dropping
        </div>
      </v-card>

      <v-row class="mb-4">
        <v-col cols="12" sm="6" md="3">
          <v-card class="glass-card kpi-card kpi-card--success pa-4" variant="flat">
            <div class="text-caption text-medium-emphasis">Current Streak</div>
            <div class="text-h4 font-weight-bold text-success">🔥 <AnimatedNumber :value="data.current_streak" /></div>
            <div class="text-caption">Longest: {{ data.longest_streak }}</div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="glass-card kpi-card kpi-card--success pa-4" variant="flat">
            <div class="text-caption text-medium-emphasis">Vocabulary Learned</div>
            <div class="text-h5 font-weight-bold text-success"><AnimatedNumber :value="data.vocabulary_learned" /></div>
            <div class="text-caption">Review Later: {{ data.vocabulary_learning }}</div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="glass-card kpi-card pa-4" variant="flat">
            <div class="text-caption text-medium-emphasis">Writing Completed</div>
            <div class="text-h5 font-weight-bold"><AnimatedNumber :value="data.writing_completed" /></div>
            <div class="text-body-2 mt-1">{{ data.writing_completion_percent }}%</div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="glass-card kpi-card pa-4" variant="flat">
            <div class="text-caption text-medium-emphasis">Speaking Completed</div>
            <div class="text-h5 font-weight-bold"><AnimatedNumber :value="data.speaking_completed" /></div>
            <div class="text-body-2 mt-1">{{ data.speaking_completion_percent }}%</div>
          </v-card>
        </v-col>
      </v-row>

      <v-row class="mb-4">
        <v-col cols="12" sm="6" md="3">
          <v-card class="glass-card kpi-card pa-4" variant="flat">
            <div class="text-caption text-medium-emphasis">Completed activities</div>
            <div class="text-h5 font-weight-bold"><AnimatedNumber :value="data.completed_activities" /></div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="glass-card kpi-card pa-4" variant="flat">
            <div class="text-caption text-medium-emphasis">Continue reading</div>
            <v-progress-linear
              :model-value="data.reading_completion_percent"
              color="secondary"
              height="8"
              rounded
              class="mt-2"
            />
            <div class="text-body-2 mt-1">{{ data.reading_completion_percent }}%</div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="glass-card kpi-card pa-4" variant="flat">
            <div class="text-caption text-medium-emphasis">Complete listening</div>
            <v-progress-linear
              :model-value="data.listening_completion_percent"
              color="secondary"
              height="8"
              rounded
              class="mt-2"
            />
            <div class="text-body-2 mt-1">{{ data.listening_completion_percent }}%</div>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card class="glass-card kpi-card pa-4" variant="flat">
            <div class="text-caption text-medium-emphasis">Known Words (total)</div>
            <div class="text-h5 font-weight-bold"><AnimatedNumber :value="data.vocabulary_count" /></div>
          </v-card>
        </v-col>
      </v-row>

      <section v-if="learner && (weakComponents.length || skillStrengthList.length)" class="section-block">
        <div class="section-block__head">
          <h3 class="section-block__title">Focus areas</h3>
          <p class="section-block__subtitle mb-0">Your skill strength and what to work on next</p>
        </div>
        <v-card class="glass-card pa-5" variant="flat">
          <div v-if="skillStrengthList.length" class="mb-4">
            <div class="text-caption text-medium-emphasis mb-2">
              Skill strength <span class="text-disabled">— your CEFR level per skill (A1 → C2)</span>
            </div>
            <LanguageSkillRadar v-if="skillStrengthList.length >= 3" :skills="skillStrengthList" />
            <template v-else>
              <div v-for="s in skillStrengthList" :key="s.key" class="conf-row mb-2">
                <span class="conf-label text-body-2">{{ s.label }}</span>
                <v-progress-linear
                  :model-value="s.value"
                  :color="s.value < 40 ? 'error' : (s.value < 70 ? 'warning' : 'success')"
                  height="8" rounded class="conf-bar"
                />
                <span class="conf-val text-body-2 font-weight-bold">{{ s.value }}%</span>
              </div>
            </template>
          </div>
          <div v-if="weakComponents.length">
            <div class="text-caption text-medium-emphasis mb-2">
              Skills to strengthen — tap one to practise it<span v-if="dueCount"> · {{ dueCount }} due for review</span>
            </div>
            <div class="d-flex flex-wrap gap-2">
              <v-chip
                v-for="c in weakComponents"
                :key="c.code"
                size="small"
                variant="tonal"
                :color="c.mastery < 40 ? 'error' : (c.mastery < 70 ? 'warning' : 'success')"
                @click="practiceSkill(c.skill)"
              >
                {{ skillLabel(c.skill) }} · {{ prettyComponent(c.code) }} · {{ c.mastery }}%
              </v-chip>
            </div>
          </div>
        </v-card>
      </section>

      <section ref="smartReviewEl" class="section-block">
        <div class="section-block__head d-flex align-center justify-space-between flex-wrap gap-2">
          <div>
            <h3 class="section-block__title">Smart review</h3>
            <p class="section-block__subtitle mb-0">
              {{ practiceSkillFocus ? `Focused on ${skillLabel(practiceSkillFocus)}` : 'A few quick questions, picked for your weak spots' }}
            </p>
          </div>
          <v-btn color="secondary" variant="tonal" size="small" :loading="practiceBusy" @click="startPractice()">
            {{ practiceItems.length ? 'New set' : 'Start' }}
          </v-btn>
        </div>
        <v-card class="glass-card pa-5" variant="flat">
          <SmartReviewGame
            v-if="practiceItems.length"
            :items="practiceItems"
            @finish="onPracticeFinish"
            @replay="startPractice(practiceSkillFocus)"
          />
          <EmptyState
            v-else
            compact
            icon="mdi-lightbulb-on-outline"
            title="Ready when you are"
            description="Start a quick adaptive review built from your learner profile."
          />
        </v-card>
      </section>

      <section class="section-block">
        <div class="section-block__head">
          <h3 class="section-block__title">Recent activity</h3>
          <p class="section-block__subtitle mb-0">Your latest language learning events</p>
        </div>
        <v-card class="glass-card pa-5" variant="flat">
          <v-list v-if="data.recent_activity?.length" density="comfortable">
            <v-list-item v-for="ev in data.recent_activity" :key="ev.id">
              <v-list-item-title>{{ ev.title || ev.event_type }}</v-list-item-title>
              <v-list-item-subtitle>
                {{ formatDate(ev.created_at) }}
                <span v-if="ev.score_percent != null"> — {{ ev.score_percent }}%</span>
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
          <EmptyState
            v-else
            compact
            icon="mdi-history"
            title="No activity yet"
            description="Your recent language activity will appear here."
          />
        </v-card>
      </section>
    </template>

    <LevelUpCelebration
      :show="levelUpState.show"
      :from="levelUpState.from"
      :to="levelUpState.to"
      @close="dismissLevelUp"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import EmptyState from '../../../components/common/EmptyState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import LanguageSkillRadar from '../../../components/language/LanguageSkillRadar.vue'
import AnimatedNumber from '../../../components/common/AnimatedNumber.vue'
import SmartReviewGame from '../../../components/language/SmartReviewGame.vue'
import LevelUpCelebration from '../../../components/language/LevelUpCelebration.vue'
import { levelUpState, checkLevelUp, dismissLevelUp } from '../../../composables/useLevelUp.js'
import {
  fetchAdaptiveState,
  fetchLanguageProgress,
  fetchLearnerModelProfile,
  fetchLearnerPractice,
  submitLearnerPractice,
} from '../../../api/language.js'
import { useLanguageAccess } from '../../../composables/useLanguageAccess.js'
import { useLanguageGate } from '../../../composables/useLanguageGate.js'

const { access, loadAccess } = useLanguageAccess()
const { handleLanguageApiError, getErrorMessage } = useLanguageGate()

const data = ref(null)
const adaptive = ref(null)
const learner = ref(null)
const loading = ref(true)
const loadError = ref('')

const SKILL_LABELS = { reading: 'Reading', listening: 'Listening', writing: 'Writing', speaking: 'Speaking' }

function skillLabel(key) {
  return SKILL_LABELS[key] || (key || '').replace(/\b\w/g, (m) => m.toUpperCase())
}

const CEFR_ORDER = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const cefrRank = (lv) => {
  const i = CEFR_ORDER.indexOf(lv)
  return i < 0 ? 0 : i
}
function skillLevelOf(skillKey) {
  return data.value?.[`${skillKey}_level`] || 'A1'
}

// Per-skill STRENGTH = average mastery of the components AT OR BELOW the learner's level for that
// skill (the things they're expected to know). Averaging in far-above-level components — which are
// seeded as "not yet" — would unfairly drag a solid B1 reader down to ~40%.
const skillStrengthList = computed(() => {
  const groups = {}
  for (const c of learner.value?.components || []) (groups[c.skill] ||= []).push(c)
  const out = []
  for (const k of Object.keys(SKILL_LABELS)) {
    const list = groups[k]
    if (!list?.length) continue
    // Strength = absolute position on the CEFR ladder (A1..C2 -> 0..100), nudged by how well the
    // learner has mastered up to that level. This reflects real ability (B1 reader > A2 writer),
    // instead of normalising every skill to its own level (which made them all look equal).
    const skRank = cefrRank(skillLevelOf(k)) // 0 (A1) .. 5 (C2)
    const scope = list.filter((c) => cefrRank(c.cefr_level) <= skRank)
    // mastery within the level; when nothing sits at/below (e.g. A1 with A2-entry catalogue),
    // assume a mid baseline so a beginner isn't shown as ~0.
    const m = scope.length
      ? Math.min(1, scope.reduce((a, c) => a + (c.p_mastery || 0), 0) / scope.length)
      : 0.6
    const value = Math.round(((skRank + m) / 6) * 100)
    out.push({ key: k, label: SKILL_LABELS[k], value })
  }
  return out
})

// "Skills to strengthen" = the weakest components WITHIN REACH (at most one CEFR band above the
// learner's level for that skill) — never C1/C2 items for an A2 learner.
const weakComponents = computed(() =>
  [...(learner.value?.components || [])]
    .filter((c) => cefrRank(c.cefr_level) <= cefrRank(skillLevelOf(c.skill)) + 1)
    .sort((a, b) => (a.p_mastery || 0) - (b.p_mastery || 0))
    .slice(0, 6)
    .map((c) => ({ ...c, mastery: Math.round((c.p_mastery || 0) * 100) })),
)

const dueCount = computed(() => learner.value?.due_count || 0)

function prettyComponent(code) {
  const tail = String(code || '').split('.').pop() || ''
  return tail.replace(/_/g, ' ').replace(/\b\w/g, (m) => m.toUpperCase())
}

// --- Smart review (adaptive practice — the flip-card game owns per-question state) ---
const smartReviewEl = ref(null)
const practiceSkillFocus = ref('')
const practiceItems = ref([])
const practiceBusy = ref(false)

async function loadLearner() {
  try {
    learner.value = await fetchLearnerModelProfile()
  } catch {
    /* learner-model surface is best-effort */
  }
}

async function startPractice(skill = '') {
  if (practiceBusy.value) return
  practiceBusy.value = true
  practiceSkillFocus.value = typeof skill === 'string' ? skill : ''
  try {
    const res = await fetchLearnerPractice(4, practiceSkillFocus.value)
    practiceItems.value = res.items || []
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Could not start the review')
  } finally {
    practiceBusy.value = false
  }
}

async function practiceSkill(skill) {
  await startPractice(skill)
  // bring the (now-focused) Smart review into view
  smartReviewEl.value?.$el?.scrollIntoView?.({ behavior: 'smooth', block: 'start' })
  smartReviewEl.value?.scrollIntoView?.({ behavior: 'smooth', block: 'start' })
}

async function onPracticeFinish(results) {
  if (!results?.length) return
  try {
    await submitLearnerPractice(results)
  } catch {
    /* non-fatal: still graded locally */
  }
  await loadLearner() // reflect the new evidence in the focus areas
}

const ADAPTIVE_LABELS = { reading: 'Reading', listening: 'Listening', writing: 'Writing', speaking: 'Speaking' }
const adaptiveSkills = computed(() => {
  const s = adaptive.value?.skills || {}
  return ['reading', 'listening', 'writing', 'speaking']
    .filter((k) => s[k])
    .map((k) => ({ key: k, label: ADAPTIVE_LABELS[k], ...s[k] }))
})

const levelSkills = computed(() => [
  { key: 'reading', label: 'Reading', level: data.value?.reading_level },
  { key: 'listening', label: 'Listen', level: data.value?.listening_level },
  { key: 'writing', label: 'Writing', level: data.value?.writing_level },
  { key: 'speaking', label: 'Speaking', level: data.value?.speaking_level },
])

function growthPercent(skillKey) {
  const g = data.value?.skill_growth?.[skillKey]
  return g?.growth_percent ?? 0
}

onMounted(async () => {
  try {
    await loadAccess(true)
    data.value = await fetchLanguageProgress()
    checkLevelUp(data.value?.overall_level)
    try {
      adaptive.value = await fetchAdaptiveState()
    } catch {
      /* adaptive strip is best-effort */
    }
    await loadLearner()
  } catch (e) {
    if (!handleLanguageApiError(e, access.value)) {
      loadError.value = getErrorMessage(e, 'Unable to load progress')
    }
  } finally {
    loading.value = false
  }
})

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString('de-DE')
  } catch {
    return iso
  }
}
</script>

<style scoped>
.page-container {
  max-width: 1100px;
  margin: 0 auto;
}
.conf-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.conf-label {
  flex: 0 0 84px;
}
.conf-bar {
  flex: 1 1 auto;
}
.conf-val {
  flex: 0 0 44px;
  text-align: right;
}
</style>
