<template>
  <div class="hub-page slide-up-enter-active">
    <AuroraBackground />
    <div class="hub-content">
    <LanguageModuleTabs />

    <PageHeader
      eyebrow="Your English journey"
      eyebrow-icon="mdi-translate"
      title="Welcome back"
      subtitle="A personal path, tuned in real time to how you learn."
    >
      <template v-if="access" #actions>
        <div class="d-flex flex-wrap gap-2 justify-end">
          <v-chip :color="statusColor" variant="tonal" size="small" prepend-icon="mdi-shield-check">
            {{ statusLabel }}
          </v-chip>
          <v-chip v-if="overallLevel" color="secondary" variant="flat" size="small">
            Overall: {{ overallLevel }}
          </v-chip>
          <v-chip v-if="access.expires_at" variant="outlined" size="small">
            Renews {{ formatDate(access.expires_at) }}
          </v-chip>
        </div>
      </template>
    </PageHeader>

    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-5 rounded-lg">{{ loadError }}</v-alert>
    <LoadingState v-if="loading" variant="cards" :count="3" class="mb-6" />

    <template v-else-if="access">
      <LanguagePaywallCard
        v-if="!access.subscribed"
        class="mb-6"
        :product="access.product"
        :status="access.status"
        @subscribe="goSubscribe"
      />

      <template v-else>
        <v-alert
          v-if="!access.placement_completed"
          type="warning"
          variant="tonal"
          icon="mdi-flag-checkered"
          class="mb-6 rounded-lg"
        >
          <div class="d-flex align-center flex-wrap gap-3 justify-space-between">
            <div>
              <div class="font-weight-bold">One step before you begin</div>
              <div class="text-body-2">A quick 3-5 minute AI interview sets your starting level.</div>
            </div>
            <v-btn
              color="secondary"
              variant="flat"
              rounded="lg"
              :to="ROUTES.STUDENT_LANGUAGES_EXAM"
            >
              Take the AI level exam
            </v-btn>
          </div>
        </v-alert>

        <v-row v-if="access.placement_completed" class="mb-6">
          <v-col cols="6" sm="3">
            <v-card class="glass-card kpi-card pa-4 text-center" variant="flat">
              <v-icon class="kpi-card__icon" color="secondary" size="22">mdi-school-outline</v-icon>
              <div class="text-h5 font-weight-bold">{{ overallLevel || '—' }}</div>
              <div class="text-caption text-medium-emphasis">Overall level</div>
            </v-card>
          </v-col>
          <v-col cols="6" sm="3">
            <v-card class="glass-card kpi-card kpi-card--success pa-4 text-center" variant="flat">
              <v-icon class="kpi-card__icon" color="success" size="22">mdi-target</v-icon>
              <div class="text-h5 font-weight-bold text-success">{{ goalPercent }}%</div>
              <div class="text-caption text-medium-emphasis">To your goal</div>
            </v-card>
          </v-col>
          <v-col v-if="goalLevel" cols="6" sm="3">
            <v-card class="glass-card kpi-card kpi-card--warning pa-4 text-center" variant="flat">
              <v-icon class="kpi-card__icon" color="warning" size="22">mdi-flag-outline</v-icon>
              <div class="text-h5 font-weight-bold text-warning">{{ goalLevel }}</div>
              <div class="text-caption text-medium-emphasis">
                {{ access.estimated_time_to_next_level ? `≈ ${access.estimated_time_to_next_level} to go` : (goalDate ? `by ${goalDate}` : 'Target level') }}
              </div>
            </v-card>
          </v-col>
          <v-col v-if="hub" cols="6" sm="3">
            <v-card class="glass-card kpi-card pa-4 text-center" variant="flat">
              <v-icon class="kpi-card__icon" color="primary" size="22">mdi-book-check-outline</v-icon>
              <div class="text-h5 font-weight-bold">{{ lessonsDoneLabel }}</div>
              <div class="text-caption text-medium-emphasis">Lessons done</div>
            </v-card>
          </v-col>
        </v-row>

        <v-card
          v-if="access.placement_completed && placementRec && (placementRec.topic || placementRec.corrections?.length)"
          class="glass-card pa-4 mb-6 placement-rec"
          variant="flat"
        >
          <div class="d-flex align-center flex-wrap gap-3 justify-space-between mb-2">
            <div>
              <div class="text-caption text-medium-emphasis">From your placement</div>
              <h3 class="text-subtitle-1 font-weight-bold mb-0">
                Start here<span v-if="focusLabel">: focus on {{ focusLabel }}</span>
              </h3>
            </div>
            <v-btn color="secondary" variant="flat" rounded="lg" prepend-icon="mdi-map-marker-path" @click="goLearningPath">
              Go to my learning path
            </v-btn>
          </div>
          <p v-if="placementRec.topic" class="text-body-2 mb-2">
            <v-icon size="16" color="secondary" icon="mdi-lightbulb-on-outline" /> {{ placementRec.topic }}
          </p>
          <div v-if="placementRec.corrections?.length">
            <div class="text-caption text-medium-emphasis mb-1">Common mistakes to fix:</div>
            <LanguageCorrectionList :errors="placementRec.corrections" />
          </div>
        </v-card>

        <section v-if="access.placement_completed && hasAnyLevel" class="section-block">
          <div class="section-block__head d-flex align-center justify-space-between flex-wrap gap-2">
            <div>
              <h3 class="section-block__title">Your levels</h3>
              <p v-if="strengthLabel || focusLabel" class="section-block__subtitle mb-0">
                <span v-if="strengthLabel">Strength: {{ strengthLabel }}</span>
                <span v-if="strengthLabel && focusLabel"> · </span>
                <span v-if="focusLabel">Focus: {{ focusLabel }}</span>
              </p>
            </div>
            <div>
              <v-btn size="small" variant="text" color="secondary" @click="goPlacementResults">Results</v-btn>
              <v-btn size="small" variant="text" :disabled="retakeBlocked" :to="ROUTES.STUDENT_LANGUAGES_EXAM">Retake</v-btn>
            </div>
          </div>
          <v-row>
            <v-col v-for="s in skillCards" :key="s.key" cols="6" sm="3">
              <v-card class="glass-card kpi-card pa-4 text-center" variant="flat">
                <v-icon class="kpi-card__icon" :color="s.color" size="22">{{ s.icon }}</v-icon>
                <div class="text-h5 font-weight-bold">{{ s.level || '—' }}</div>
                <div class="text-caption text-medium-emphasis">{{ s.label }}</div>
              </v-card>
            </v-col>
          </v-row>
          <div v-if="growthStats.length" class="d-flex flex-wrap gap-2 mt-3">
            <v-chip v-for="m in growthStats" :key="m.label" size="small" variant="tonal" color="secondary">
              {{ m.label }}: {{ m.value }}
            </v-chip>
          </div>
        </section>

        <section v-if="access.placement_completed" class="section-block">
          <div class="section-block__head">
            <h3 class="section-block__title">Continue learning</h3>
            <p class="section-block__subtitle mb-0">Pick up where you left off, or explore a new skill</p>
          </div>
          <v-row>
            <v-col v-for="t in featureTiles" :key="t.label" cols="12" sm="6" md="4">
              <v-card class="glass-card pa-4 tile-card" variant="flat" :to="t.to">
                <div class="d-flex align-center gap-3">
                  <v-avatar :color="t.color" variant="tonal" size="44">
                    <v-icon size="22">{{ t.icon }}</v-icon>
                  </v-avatar>
                  <div>
                    <div class="font-weight-bold">{{ t.label }}</div>
                    <div class="text-caption text-medium-emphasis">{{ t.sub }}</div>
                  </div>
                  <v-spacer />
                  <v-icon size="18" color="secondary">mdi-arrow-top-right</v-icon>
                </div>
              </v-card>
            </v-col>
          </v-row>
        </section>
      </template>
    </template>
    </div>

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
import LanguagePaywallCard from '../../../components/language/LanguagePaywallCard.vue'
import LanguageModuleTabs from '../../../components/language/LanguageModuleTabs.vue'
import LanguageCorrectionList from '../../../components/language/LanguageCorrectionList.vue'
import AuroraBackground from '../../../components/common/AuroraBackground.vue'
import LevelUpCelebration from '../../../components/language/LevelUpCelebration.vue'
import { levelUpState, checkLevelUp, dismissLevelUp } from '../../../composables/useLevelUp.js'
import { useLanguageAccess } from '../../../composables/useLanguageAccess.js'
import { getErrorMessage } from '../../../api/client.js'
import { fetchLanguageHub } from '../../../api/language.js'
import { ROUTES } from '../../../constants/app.js'

const router = useRouter()
const { access, loading, loadAccess } = useLanguageAccess()
const loadError = ref('')
const hub = ref(null)

const statusLabel = computed(() => {
  const map = {
    active: 'Active subscription',
    expiring_soon: 'Ends soon',
    expired: 'Finished',
    pending: 'Inactive',
  }
  return map[access.value?.status] || access.value?.status
})

const statusColor = computed(() => {
  const map = {
    active: 'success',
    expiring_soon: 'warning',
    expired: 'error',
    pending: 'grey',
  }
  return map[access.value?.status] || 'grey'
})

const skillCards = computed(() => {
  const lv = access.value?.levels || {}
  return [
    { key: 'reading', label: 'Reading', level: lv.reading, icon: 'mdi-book-open-page-variant', color: 'blue' },
    { key: 'listening', label: 'Listening', level: lv.listening, icon: 'mdi-headphones', color: 'deep-purple' },
    { key: 'writing', label: 'Writing', level: lv.writing, icon: 'mdi-pencil-outline', color: 'orange' },
    { key: 'speaking', label: 'Speaking', level: lv.speaking, icon: 'mdi-microphone-outline', color: 'pink' },
  ]
})

const hasAnyLevel = computed(() => skillCards.value.some((s) => s.level))
const overallLevel = computed(() => hub.value?.levels?.overall || null)
const goalPercent = computed(() => Math.max(0, Math.min(100, access.value?.target_progress_percent ?? 0)))
const goalLevel = computed(() => hub.value?.target_level || access.value?.target_level || null)
const goalDate = computed(() => hub.value?.target_date || access.value?.target_date || null)
const focusLabel = computed(() => access.value?.levels?.primary_focus_label_ar || null)
const strengthLabel = computed(() => access.value?.levels?.strength_label_ar || null)
const placementRec = computed(() => access.value?.placement_recommendation || null)

function goLearningPath() {
  router.push(ROUTES.STUDENT_LANGUAGES_CURRICULUM)
}

const lessonsDoneLabel = computed(() => {
  const lp = hub.value?.learning_path || {}
  return `${lp.items_completed || 0}/${lp.items_total || 0}`
})

const growthStats = computed(() => {
  const g = hub.value?.skill_growth || {}
  return [
    { label: 'Reading growth', value: `${g.reading?.growth_percent ?? 0}%` },
    { label: 'Listening growth', value: `${g.listening?.growth_percent ?? 0}%` },
    { label: 'Vocabulary growth', value: `${g.vocabulary?.growth_percent ?? 0}%` },
  ]
})

const featureTiles = [
  { label: 'Listening', sub: 'Audio & dialogues', icon: 'mdi-headphones', to: ROUTES.STUDENT_LANGUAGES_LISTENING, color: 'deep-purple' },
  { label: 'Vocabulary', sub: 'Cards & spaced review', icon: 'mdi-cards-outline', to: ROUTES.STUDENT_LANGUAGES_VOCABULARY, color: 'teal' },
  { label: 'Writing', sub: 'Guided prompts', icon: 'mdi-pencil-outline', to: ROUTES.STUDENT_LANGUAGES_WRITING, color: 'orange' },
  { label: 'Speaking', sub: 'Talk with the AI', icon: 'mdi-microphone-outline', to: ROUTES.STUDENT_LANGUAGES_SPEAKING, color: 'pink' },
  { label: 'Curriculum', sub: 'Your learning path', icon: 'mdi-map-marker-path', to: ROUTES.STUDENT_LANGUAGES_CURRICULUM, color: 'light-green' },
  { label: 'Progress', sub: 'Levels & growth', icon: 'mdi-chart-line', to: ROUTES.STUDENT_LANGUAGES_PROGRESS, color: 'cyan' },
]

onMounted(async () => {
  try {
    await loadAccess(true)
    if (access.value?.redirect) {
      router.push(access.value.redirect)
      return
    }
    if (access.value?.placement_completed && access.value?.subscribed) {
      hub.value = await fetchLanguageHub()
      checkLevelUp(hub.value?.levels?.overall || access.value?.levels?.overall)
    }
  } catch (e) {
    loadError.value = getErrorMessage(e, 'Unable to load')
  }
})

function goSubscribe() {
  router.push(ROUTES.STUDENT_LANGUAGES_SUBSCRIBE)
}
function goPlacement() {
  router.push(ROUTES.STUDENT_LANGUAGES_EXAM)
}
function goPlacementResults() {
  router.push(ROUTES.STUDENT_LANGUAGES_PLACEMENT_HISTORY)
}

const retakeBlocked = computed(() => {
  const dt = access.value?.next_allowed_retake_date
  if (!dt) return false
  try {
    return new Date(dt).getTime() > Date.now()
  } catch {
    return false
  }
})

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleDateString('de-DE')
  } catch {
    return iso
  }
}
</script>

<style scoped>
.hub-page {
  max-width: 1100px;
  margin: 0 auto;
  position: relative;
}
.hub-content {
  position: relative;
  z-index: 1;
}

.tile-card {
  transition: transform 0.25s, border-color 0.25s, box-shadow 0.25s;
  cursor: pointer;
}

.tile-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 30px -10px rgba(var(--v-theme-secondary), 0.45);
}
</style>
