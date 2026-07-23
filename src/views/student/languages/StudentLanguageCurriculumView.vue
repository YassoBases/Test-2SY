<template>
  <div class="page-container slide-up-enter-active">
    <PageHeader
      eyebrow="Learn languages"
      eyebrow-icon="mdi-map-marker-path"
      title="Curriculum"
      subtitle="Your CEFR learning path — master each level to unlock the next"
    />
    <LanguageModuleTabs />

    <v-card v-if="dailyPlan && dailyPlan.items.length" class="glass-card pa-4 mb-4" variant="flat" dir="ltr">
      <div class="d-flex align-center gap-2 mb-2 flex-wrap">
        <v-icon color="secondary">mdi-calendar-check</v-icon>
        <span class="text-subtitle-1 font-weight-bold">Today's mission</span>
        <v-spacer />
        <span class="text-caption font-weight-bold">{{ dailyPlan.completed_today }}/{{ dailyPlan.goal }} done</span>
      </div>
      <v-progress-linear
        :model-value="dailyPlan.goal ? (100 * dailyPlan.completed_today / dailyPlan.goal) : 0"
        :color="dailyPlan.completed_today >= dailyPlan.goal ? 'success' : 'secondary'"
        height="6"
        rounded
        class="mb-3"
      />
      <v-list density="compact" class="bg-transparent pa-0">
        <v-list-item v-for="(it, i) in dailyPlan.items" :key="i" class="px-0">
          <template #prepend>
            <v-icon size="18" :color="it.done ? 'success' : featureColor(it.feature)" class="me-2">
              {{ it.done ? 'mdi-check-circle' : featureIcon(it.feature) }}
            </v-icon>
          </template>
          <v-list-item-title
            class="text-body-2"
            :class="{ 'text-medium-emphasis text-decoration-line-through': it.done }"
          >
            {{ it.title }}
          </v-list-item-title>
          <v-list-item-subtitle v-if="it.detail" class="text-caption">{{ it.detail }}</v-list-item-subtitle>
          <template #append>
            <v-chip v-if="it.done" size="x-small" color="success" variant="tonal">Done</v-chip>
            <v-btn v-else size="small" variant="tonal" color="secondary" @click="startItem(it)">Start</v-btn>
          </template>
        </v-list-item>
      </v-list>
    </v-card>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{ error }}</v-alert>
    <LoadingState v-if="loading" variant="cards" :count="3" class="mb-6" />

    <template v-else-if="data">
      <v-row class="mb-4">
        <v-col cols="6" sm="4">
          <v-card class="glass-card kpi-card pa-3 text-center" variant="flat">
            <div class="text-caption text-medium-emphasis">Current level</div>
            <div class="text-h6 font-weight-bold">{{ data.current_level }}</div>
          </v-card>
        </v-col>
        <v-col cols="6" sm="4">
          <v-card class="glass-card kpi-card kpi-card--success pa-3 text-center" variant="flat">
            <div class="text-caption text-medium-emphasis">Objectives mastered</div>
            <div class="text-h6 font-weight-bold text-success">{{ data.objectives_mastered }}/{{ data.objectives_total }}</div>
          </v-card>
        </v-col>
        <v-col v-if="dailyPlan" cols="6" sm="4">
          <v-card class="glass-card kpi-card pa-3 text-center" variant="flat">
            <div class="text-caption text-medium-emphasis">Today's mission</div>
            <div class="text-h6 font-weight-bold">{{ dailyPlan.completed_today }}/{{ dailyPlan.goal }}</div>
          </v-card>
        </v-col>
      </v-row>

      <!-- Level journey -->
      <v-card class="glass-card pa-4 mb-4" variant="flat">
        <div class="d-flex align-center flex-wrap gap-2">
          <template v-for="(lv, i) in data.levels" :key="lv.level">
            <v-chip
              :color="chipColor(lv.status)"
              :variant="lv.status === 'current' ? 'flat' : 'tonal'"
              size="small"
            >
              <v-icon v-if="lv.status === 'done'" start size="16">mdi-check</v-icon>
              <v-icon v-else-if="lv.status === 'locked'" start size="16">mdi-lock</v-icon>
              {{ lv.level }}
            </v-chip>
            <v-icon v-if="i < data.levels.length - 1" size="16" color="medium-emphasis">mdi-chevron-right</v-icon>
          </template>
        </div>

        <div v-if="xp && !xp.is_max_level" class="mt-4">
          <div class="d-flex justify-space-between text-caption mb-1">
            <span class="text-medium-emphasis">
              Earn XP to reach {{ xp.next_level }} — {{ xp.level_xp }} / {{ xp.xp_needed }} XP
            </span>
            <span class="font-weight-bold">{{ xp.percent_to_next }}%</span>
          </div>
          <v-progress-linear
            :model-value="xp.percent_to_next"
            color="secondary"
            height="10"
            rounded
          />
          <div class="text-caption text-medium-emphasis mt-2">
            <v-icon size="14" color="secondary">mdi-star-four-points</v-icon>
            Practise any skill, talk, review words — every win earns XP and fills this bar to level up.
            Total XP: <strong>{{ xp.xp_total }}</strong>
          </div>
        </div>
        <div v-else-if="xp && xp.is_max_level" class="text-caption text-success mt-3">
          ★ Top level (C2) — total XP {{ xp.xp_total }}. Keep practising to stay sharp.
        </div>
      </v-card>

      <v-bottom-sheet v-model="learnOpen" :inset="true" max-width="640">
        <v-card class="pa-4" rounded="t-xl" dir="ltr">
          <div class="d-flex align-center justify-space-between mb-3">
            <span class="text-h6">{{ learnObj?.title || 'Lesson' }}</span>
            <v-btn icon="mdi-close" variant="text" size="small" @click="learnOpen = false" />
          </div>
          <div v-if="learnLoading" class="text-center py-6">
            <v-progress-circular indeterminate color="secondary" />
          </div>
          <template v-else-if="lesson">
            <p v-if="lesson.explanation" class="text-body-1 mb-3" dir="ltr">{{ lesson.explanation }}</p>

            <div v-if="lesson.rule_points?.length" class="mb-3">
              <div class="text-caption font-weight-bold text-medium-emphasis mb-1">The rule</div>
              <ul class="text-body-2 ps-4 mb-0">
                <li v-for="(r, i) in lesson.rule_points" :key="i">{{ r }}</li>
              </ul>
            </div>

            <div v-if="lesson.examples?.length" class="mb-3">
              <div class="text-caption font-weight-bold text-medium-emphasis mb-1">Examples</div>
              <div v-for="(ex, i) in lesson.examples" :key="i" class="ex-box pa-2 rounded-lg mb-1">
                <div class="text-body-2" dir="ltr">{{ ex }}</div>
              </div>
            </div>

            <div v-if="lesson.key_vocab?.length" class="mb-3">
              <div class="text-caption font-weight-bold text-medium-emphasis mb-1">Key words</div>
              <div class="d-flex flex-wrap gap-1">
                <v-chip v-for="(kv, i) in lesson.key_vocab" :key="i" size="small" variant="tonal">
                  {{ kv.word }}<span v-if="kv.meaning" class="ms-1 text-medium-emphasis">· {{ kv.meaning }}</span>
                </v-chip>
              </div>
            </div>

            <div v-if="lesson.common_mistake" class="mistake-box pa-2 rounded-lg mb-3" dir="ltr">
              <span class="text-caption font-weight-bold">Common mistake:</span> {{ lesson.common_mistake }}
            </div>
            <p v-if="lesson.practice_tip" class="text-body-2 text-success mb-3" dir="ltr">{{ lesson.practice_tip }}</p>

            <v-btn color="secondary" variant="flat" prepend-icon="mdi-play" @click="practiceFromLesson">Practice now</v-btn>
          </template>
        </v-card>
      </v-bottom-sheet>

      <!-- Objectives for current level -->
      <section class="section-block">
        <div class="section-block__head" dir="ltr">
          <h3 class="section-block__title">
            Level {{ data.current_level }} —
            {{ allObjectivesMastered ? 'mastered ✓' : 'what to master' }}
          </h3>
          <p class="section-block__subtitle mb-0">
            <template v-if="allObjectivesMastered">
              All {{ data.objectives_total }} objectives mastered — keep earning XP{{ data.next_level ? ` to reach ${data.next_level}` : '' }}.
            </template>
            <template v-else>{{ data.objectives_mastered }}/{{ data.objectives_total }} mastered</template>
          </p>
        </div>
      <v-row dense>
        <v-col v-for="ob in data.objectives" :key="ob.id" cols="12" md="6">
          <v-card class="glass-card pa-4 h-100" variant="flat" dir="ltr">
            <div class="d-flex align-center justify-space-between gap-2 mb-2">
              <span class="text-subtitle-2 font-weight-bold">{{ ob.title }}</span>
              <v-chip size="x-small" :color="featureColor(ob.feature)" variant="tonal">
                <v-icon start size="14">{{ featureIcon(ob.feature) }}</v-icon>{{ ob.feature }}
              </v-chip>
            </div>
            <div v-if="ob.grammar" class="text-caption mb-1"><strong>Grammar:</strong> {{ ob.grammar }}</div>
            <div v-if="ob.vocab" class="text-caption mb-1"><strong>Vocabulary:</strong> {{ ob.vocab }}</div>
            <div v-if="ob.example" class="text-body-2 mt-2 mb-3 example">“{{ ob.example }}”</div>
            <div class="d-flex align-center gap-2 flex-wrap">
              <v-btn
                size="small"
                color="primary"
                variant="flat"
                prepend-icon="mdi-school"
                @click="openLearn(ob)"
              >
                Learn
              </v-btn>
              <v-btn
                size="small"
                color="secondary"
                variant="tonal"
                prepend-icon="mdi-play"
                @click="practice(ob)"
              >
                Practice
              </v-btn>
              <v-chip size="x-small" :color="statusMeta(ob.status).color" variant="tonal">
                <v-icon start size="13">{{ statusMeta(ob.status).icon }}</v-icon>{{ statusMeta(ob.status).label }}
              </v-chip>
            </div>
          </v-card>
        </v-col>
      </v-row>
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
import { useRouter } from 'vue-router'
import PageHeader from '../../../components/common/PageHeader.vue'
import LoadingState from '../../../components/common/LoadingState.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import {
  fetchCurriculum,
  fetchDailyPlan,
  fetchLanguageXp,
  fetchObjectiveLesson,
  markObjectivePracticed,
} from '../../../api/language.js'
import { getErrorMessage } from '../../../api/client.js'
import { ROUTES } from '../../../constants/app.js'
import LevelUpCelebration from '../../../components/language/LevelUpCelebration.vue'
import { levelUpState, syncLevelSeen, dismissLevelUp } from '../../../composables/useLevelUp.js'

const router = useRouter()

// Deep-link a feature, carrying the objective as a focus where it applies.
function navigateToFeature(feature, focus) {
  const q = focus ? { focus } : {}
  if (feature === 'conversation') {
    router.push({ path: ROUTES.STUDENT_LANGUAGES_SPEAKING, query: { mode: 'conversation', ...q } })
  } else if (feature === 'shadowing' || feature === 'pronunciation') {
    router.push({ path: ROUTES.STUDENT_LANGUAGES_SPEAKING, query: { mode: 'shadowing', ...q } })
  } else if (feature === 'writing') {
    router.push({ path: ROUTES.STUDENT_LANGUAGES_WRITING, query: q })
  } else if (feature === 'reading') {
    router.push({ path: ROUTES.STUDENT_LANGUAGES })
  } else if (feature === 'listening') {
    router.push({ path: ROUTES.STUDENT_LANGUAGES_LISTENING })
  } else if (feature === 'vocabulary') {
    router.push({ path: ROUTES.STUDENT_LANGUAGES_VOCABULARY })
  } else {
    router.push({ path: ROUTES.STUDENT_LANGUAGES_SPEAKING, query: { mode: 'conversation', ...q } })
  }
}

async function practice(ob) {
  try {
    const r = await markObjectivePracticed(ob.id)
    ob.status = r.status
    if (data.value) data.value.objectives_mastered = data.value.objectives.filter((o) => o.status === 'mastered').length
  } catch {
    /* tracking is best-effort — never block navigation */
  }
  navigateToFeature(ob.feature, ob.grammar ? `${ob.title} (${ob.grammar})` : ob.title)
}

async function startItem(it) {
  if (it.objective_id) {
    try {
      await markObjectivePracticed(it.objective_id)
    } catch {
      /* best-effort */
    }
  }
  navigateToFeature(it.feature, it.focus || undefined)
}

const data = ref(null)
const dailyPlan = ref(null)
const xp = ref(null)
const loading = ref(true)
const error = ref('')

const allObjectivesMastered = computed(
  () => !!data.value?.objectives_total && data.value.objectives_mastered >= data.value.objectives_total,
)

// --- Micro-lesson (teach before practice) ---
const learnOpen = ref(false)
const learnLoading = ref(false)
const lesson = ref(null)
const learnObj = ref(null)

async function openLearn(ob) {
  learnObj.value = ob
  lesson.value = null
  learnOpen.value = true
  learnLoading.value = true
  try {
    lesson.value = await fetchObjectiveLesson(ob.id)
  } catch (e) {
    error.value = getErrorMessage(e, 'Could not load the lesson')
    learnOpen.value = false
  } finally {
    learnLoading.value = false
  }
}

function practiceFromLesson() {
  learnOpen.value = false
  if (learnObj.value) practice(learnObj.value)
}

const FEATURE_META = {
  conversation: { icon: 'mdi-robot-happy-outline', color: 'secondary' },
  shadowing: { icon: 'mdi-account-voice', color: 'secondary' },
  pronunciation: { icon: 'mdi-waveform', color: 'info' },
  reading: { icon: 'mdi-book-open-variant', color: 'primary' },
  listening: { icon: 'mdi-headphones', color: 'primary' },
  writing: { icon: 'mdi-pencil', color: 'primary' },
  vocabulary: { icon: 'mdi-cards-outline', color: 'primary' },
}

function chipColor(status) {
  return status === 'done' ? 'success' : status === 'current' ? 'secondary' : 'medium-emphasis'
}

const STATUS_META = {
  new: { label: 'New', color: 'medium-emphasis', icon: 'mdi-circle-outline' },
  in_progress: { label: 'In progress', color: 'info', icon: 'mdi-progress-clock' },
  mastered: { label: 'Mastered', color: 'success', icon: 'mdi-check-circle' },
}
function statusMeta(status) {
  return STATUS_META[status] || STATUS_META.new
}
function featureIcon(f) {
  return (FEATURE_META[f] || FEATURE_META.conversation).icon
}
function featureColor(f) {
  return (FEATURE_META[f] || FEATURE_META.conversation).color
}

onMounted(async () => {
  try {
    data.value = await fetchCurriculum()
    // Curriculum can be opened immediately after placement; sync the displayed level without
    // launching a level-up modal that may feel like a second, conflicting placement result.
    syncLevelSeen(data.value?.current_level)
  } catch (e) {
    error.value = getErrorMessage(e, 'Could not load your curriculum')
  } finally {
    loading.value = false
  }
  try {
    dailyPlan.value = await fetchDailyPlan()
  } catch {
    /* daily plan is optional */
  }
  try {
    xp.value = await fetchLanguageXp()
  } catch {
    /* xp bar is optional */
  }
})
</script>

<style scoped>
.example {
  font-style: italic;
  color: rgba(var(--v-theme-on-surface), 0.7);
}
.ex-box {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.mistake-box {
  background: rgba(var(--v-theme-warning), 0.06);
  border: 1px solid rgba(var(--v-theme-warning), 0.18);
}
</style>
