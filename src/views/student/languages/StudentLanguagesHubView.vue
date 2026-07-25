<template>
  <div class="hub-page slide-up-enter-active">
    <AuroraBackground />
    <div class="hub-content">
      <LanguageModuleTabs />

      <PageHeader
        compact
        eyebrow="Your English journey"
        eyebrow-icon="mdi-translate"
        title="Welcome back"
        subtitle="Pick a skill and keep going."
      >
        <template v-if="access" #actions>
          <div class="hub-status d-flex flex-wrap gap-2 justify-end">
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
                <div class="text-body-2">
                  A focused 60-minute placement exam sets your reading, listening, writing, and speaking levels.
                </div>
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

          <template v-if="access.placement_completed">
            <!-- Primary next step -->
            <div class="hub-next glass-card mb-5">
              <div class="hub-next__body">
                <div class="hub-next__copy">
                  <p class="hub-next__eyebrow mb-1">
                    {{ showPlacementRec ? 'From your placement' : 'Next step' }}
                  </p>
                  <h2 class="hub-next__title">
                    <template v-if="showPlacementRec">
                      Start here<span v-if="focusLabel">: focus on {{ focusLabel }}</span>
                    </template>
                    <template v-else>
                      Continue your learning path
                    </template>
                  </h2>
                  <p v-if="showPlacementRec && placementRec.topic" class="hub-next__topic mb-0">
                    <v-icon size="16" color="secondary" icon="mdi-lightbulb-on-outline" />
                    {{ placementRec.topic }}
                  </p>
                  <p v-else-if="!showPlacementRec" class="hub-next__topic mb-0">
                    Lessons, practice, and your curriculum in one place.
                  </p>
                </div>
                <v-btn
                  color="secondary"
                  variant="flat"
                  rounded="lg"
                  prepend-icon="mdi-map-marker-path"
                  class="hub-next__cta flex-shrink-0"
                  @click="goLearningPath"
                >
                  Go to my learning path
                </v-btn>
              </div>
              <div v-if="showPlacementRec && placementRec.corrections?.length" class="hub-next__corrections">
                <div class="text-caption text-medium-emphasis mb-1">Common mistakes to fix:</div>
                <LanguageCorrectionList :errors="placementRec.corrections" />
              </div>
            </div>

            <!-- Slim progress strip -->
            <div class="hub-progress glass-card mb-5">
              <div class="hub-progress__item">
                <span class="hub-progress__value">{{ lessonsDoneLabel }}</span>
                <span class="hub-progress__label">Lessons done</span>
              </div>
              <div class="hub-progress__divider" aria-hidden="true" />
              <div class="hub-progress__item">
                <span class="hub-progress__value hub-progress__value--success">{{ goalPercent }}%</span>
                <span class="hub-progress__label">To your goal</span>
              </div>
              <div class="hub-progress__divider" aria-hidden="true" />
              <div class="hub-progress__item">
                <span class="hub-progress__value">{{ overallLevel || '—' }}</span>
                <span class="hub-progress__label">Overall level</span>
              </div>
              <template v-if="goalLevel">
                <div class="hub-progress__divider" aria-hidden="true" />
                <div class="hub-progress__item">
                  <span class="hub-progress__value hub-progress__value--warning">{{ goalLevel }}</span>
                  <span class="hub-progress__label">
                    {{
                      access.estimated_time_to_next_level
                        ? `≈ ${access.estimated_time_to_next_level} to go`
                        : (goalDate ? `by ${goalDate}` : 'Target level')
                    }}
                  </span>
                </div>
              </template>
            </div>

            <!-- Compact skill levels -->
            <section v-if="hasAnyLevel" class="hub-levels mb-6">
              <div class="hub-levels__head">
                <div>
                  <h3 class="hub-section-title">Your levels</h3>
                  <p v-if="strengthLabel || focusLabel" class="hub-section-sub mb-0">
                    <span v-if="strengthLabel">Strength: {{ strengthLabel }}</span>
                    <span v-if="strengthLabel && focusLabel"> · </span>
                    <span v-if="focusLabel">Focus: {{ focusLabel }}</span>
                  </p>
                </div>
                <div class="hub-levels__actions">
                  <v-btn size="small" variant="text" color="secondary" @click="goPlacementResults">Results</v-btn>
                  <v-btn
                    size="small"
                    variant="text"
                    :disabled="retakeBlocked"
                    :to="ROUTES.STUDENT_LANGUAGES_EXAM"
                  >
                    Retake
                  </v-btn>
                </div>
              </div>
              <div class="hub-levels__grid">
                <div v-for="s in skillCards" :key="s.key" class="hub-level-cell glass-card">
                  <v-icon :color="s.color" size="18">{{ s.icon }}</v-icon>
                  <span class="hub-level-cell__level">{{ s.level || '—' }}</span>
                  <span class="hub-level-cell__label">{{ s.label }}</span>
                </div>
              </div>
              <p v-if="growthStats.length" class="hub-growth mb-0">
                <span v-for="(m, idx) in growthStats" :key="m.label">
                  {{ m.label }} {{ m.value }}<template v-if="idx < growthStats.length - 1"> · </template>
                </span>
              </p>
            </section>

            <!-- Continue learning menu -->
            <section class="hub-skills">
              <div class="hub-skills__head mb-3">
                <h3 class="hub-section-title">Continue learning</h3>
                <p class="hub-section-sub mb-0">Open a skill or your path</p>
              </div>
              <div class="hub-skills__grid">
                <router-link
                  v-for="t in featureTiles"
                  :key="t.label"
                  :to="t.to"
                  class="hub-skill-link glass-card"
                >
                  <v-avatar :color="t.color" variant="tonal" size="36" class="flex-shrink-0">
                    <v-icon size="18">{{ t.icon }}</v-icon>
                  </v-avatar>
                  <div class="hub-skill-link__text min-w-0">
                    <div class="hub-skill-link__title">{{ t.label }}</div>
                    <div class="hub-skill-link__sub">{{ t.sub }}</div>
                  </div>
                  <v-icon size="16" class="hub-skill-link__arrow flex-shrink-0">mdi-chevron-right</v-icon>
                </router-link>
              </div>
            </section>
          </template>
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

const showPlacementRec = computed(() => {
  const rec = placementRec.value
  return Boolean(rec && (rec.topic || rec.corrections?.length))
})

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
    { label: 'Reading', value: `${g.reading?.growth_percent ?? 0}%` },
    { label: 'Listening', value: `${g.listening?.growth_percent ?? 0}%` },
    { label: 'Vocabulary', value: `${g.vocabulary?.growth_percent ?? 0}%` },
  ]
})

const featureTiles = [
  { label: 'Reading', sub: 'AI-guided practice path', icon: 'mdi-book-open-page-variant', to: ROUTES.STUDENT_LANGUAGES_READING, color: 'blue' },
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
  max-width: 960px;
  margin: 0 auto;
  position: relative;
}

.hub-content {
  position: relative;
  z-index: 1;
}

.hub-section-title {
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 2px;
  color: rgb(var(--v-theme-on-surface));
}

.hub-section-sub {
  font-size: 0.8125rem;
  color: rgba(var(--v-theme-on-surface), 0.55);
}

/* —— Next step —— */
.hub-next {
  padding: 1.1rem 1.25rem;
}

.hub-next__body {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.hub-next__eyebrow {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: rgba(var(--v-theme-on-surface), 0.5);
}

.hub-next__title {
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 0.35rem;
  line-height: 1.3;
}

.hub-next__topic {
  font-size: 0.875rem;
  color: rgba(var(--v-theme-on-surface), 0.65);
  display: flex;
  align-items: flex-start;
  gap: 0.35rem;
}

.hub-next__corrections {
  margin-top: 0.85rem;
  padding-top: 0.85rem;
  border-top: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}

/* —— Progress strip —— */
.hub-progress {
  display: flex;
  flex-wrap: wrap;
  align-items: stretch;
  gap: 0;
  padding: 0.85rem 0.5rem;
}

.hub-progress__item {
  flex: 1 1 120px;
  min-width: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 0.35rem 0.75rem;
  gap: 0.15rem;
}

.hub-progress__value {
  font-size: 1.25rem;
  font-weight: 750;
  letter-spacing: -0.03em;
  line-height: 1.2;
}

.hub-progress__value--success {
  color: rgb(var(--v-theme-success));
}

.hub-progress__value--warning {
  color: rgb(var(--v-theme-warning));
}

.hub-progress__label {
  font-size: 0.7rem;
  font-weight: 500;
  color: rgba(var(--v-theme-on-surface), 0.5);
  line-height: 1.25;
}

.hub-progress__divider {
  width: 1px;
  align-self: stretch;
  margin: 0.35rem 0;
  background: rgba(var(--v-theme-on-surface), 0.1);
  flex: 0 0 1px;
}

@media (max-width: 600px) {
  .hub-progress__divider {
    display: none;
  }

  .hub-progress {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
    padding: 0.75rem;
  }

  .hub-progress__item {
    min-width: 0;
  }
}

/* —— Levels —— */
.hub-levels__head {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.5rem 1rem;
  margin-bottom: 0.75rem;
}

.hub-levels__grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.65rem;
}

@media (max-width: 600px) {
  .hub-levels__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.hub-level-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  padding: 0.7rem 0.5rem;
  text-align: center;
}

.hub-level-cell__level {
  font-size: 1.15rem;
  font-weight: 750;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.hub-level-cell__label {
  font-size: 0.7rem;
  color: rgba(var(--v-theme-on-surface), 0.55);
}

.hub-growth {
  margin-top: 0.65rem;
  font-size: 0.75rem;
  color: rgba(var(--v-theme-on-surface), 0.45);
}

/* —— Skill links —— */
.hub-skills__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem;
}

@media (min-width: 960px) {
  .hub-skills__grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 600px) {
  .hub-skills__grid {
    grid-template-columns: 1fr;
  }
}

.hub-skill-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 0.85rem;
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.hub-skill-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 22px -10px rgba(var(--v-theme-secondary), 0.4);
}

.hub-skill-link__title {
  font-weight: 650;
  font-size: 0.9375rem;
  line-height: 1.25;
}

.hub-skill-link__sub {
  font-size: 0.72rem;
  color: rgba(var(--v-theme-on-surface), 0.5);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hub-skill-link__arrow {
  margin-inline-start: auto;
  opacity: 0.45;
}

@media (prefers-reduced-motion: reduce) {
  .hub-skill-link {
    transition: none;
  }

  .hub-skill-link:hover {
    transform: none;
  }
}
</style>
