<template>
  <div
    class="spk-package-lesson speaking-runtime"
    role="region"
    :aria-label="t('student.languages.speakingJourney.packageLesson.region')"
  >
    <LoadingState
      v-if="loading && !packageData"
      variant="cards"
      :count="2"
      :label="t('student.languages.speakingJourney.packageLesson.loading')"
      class="mb-4 spk-skeleton-block"
    />

    <v-alert
      v-else-if="error"
      type="error"
      variant="tonal"
      class="mb-4 rounded-lg"
      role="alert"
    >
      {{ error }}
      <template #append>
        <v-btn size="small" variant="text" class="spk-pressable" @click="$emit('retry')">
          {{ t('student.languages.speakingJourney.runtime.retry') }}
        </v-btn>
      </template>
    </v-alert>

    <v-alert
      v-else-if="!packageData"
      type="info"
      variant="tonal"
      class="mb-4 rounded-lg"
      role="status"
    >
      <div class="text-subtitle-2 font-weight-bold mb-1">
        {{ t('student.languages.speakingJourney.packageLesson.emptyTitle') }}
      </div>
      <p class="text-body-2 mb-3">
        {{ t('student.languages.speakingJourney.packageLesson.emptyBody') }}
      </p>
      <v-btn color="primary" class="spk-pressable" :loading="loading" @click="$emit('open-latest')">
        {{ t('student.languages.speakingJourney.packageLesson.openLatest') }}
      </v-btn>
    </v-alert>

    <template v-else>
      <header class="spk-package-header glass-card pa-4 pa-md-5 mb-4">
        <div class="d-flex flex-wrap align-center justify-space-between gap-3 mb-3">
          <div class="min-width-0">
            <div class="text-overline text-medium-emphasis mb-1">
              {{ t('student.languages.speakingJourney.packageLesson.eyebrow') }}
            </div>
            <h2 class="text-h6 font-weight-bold mb-0">
              {{ packageData.input_material?.title || constraintsSummary.learning_focus }}
            </h2>
          </div>
          <div class="spk-package-progress" aria-live="polite">
            <div class="text-caption text-medium-emphasis mb-1">
              {{
                t('student.languages.speakingJourney.packageLesson.progressLabel', {
                  percent: sectionProgress.percent || 0,
                })
              }}
            </div>
            <v-progress-linear
              :model-value="sectionProgress.percent || 0"
              color="primary"
              height="8"
              rounded
              aria-hidden="true"
            />
          </div>
        </div>
        <nav class="spk-section-rail" :aria-label="t('student.languages.speakingJourney.packageLesson.sections')">
          <button
            v-for="sec in railSections"
            :key="sec"
            type="button"
            class="spk-section-chip"
            :class="{
              'is-current': sec === currentSection,
              'is-done': completedSet.has(sec),
            }"
            disabled
            :aria-current="sec === currentSection ? 'step' : undefined"
          >
            {{ t(`student.languages.speakingJourney.packageLesson.section.${sec}`) }}
          </button>
        </nav>
      </header>

      <Transition name="runtime-fade" mode="out-in">
        <SpeakingPackageIntro
          v-if="currentSection === 'introduction'"
          :key="'intro'"
          :constraints="constraintsSummary"
          :package-data="packageData"
          :advancing="advancing"
          @continue="$emit('advance')"
        />
        <SpeakingPackageMaterial
          v-else-if="currentSection === 'reading'"
          :key="'reading'"
          :material="packageData.input_material"
          :story-spine="packageData.story_spine"
          :advancing="advancing"
          @continue="$emit('advance')"
        />
        <SpeakingPackageVocabulary
          v-else-if="currentSection === 'vocabulary'"
          :key="'vocab'"
          :entries="packageData.vocabulary_in_context?.entries || []"
          :viewed-ids="state?.viewed_vocabulary_ids || []"
          :advancing="advancing"
          @view="(id) => $emit('mark-vocab', id)"
          @continue="$emit('advance')"
        />
        <SpeakingPackageTeaching
          v-else-if="currentSection === 'teaching'"
          :key="'teach'"
          :blocks="packageData.teaching_blocks_authored || []"
          :completed-ids="state?.completed_teaching_block_ids || []"
          :advancing="advancing"
          @view="(id) => $emit('mark-block', id)"
          @continue="$emit('advance')"
        />
        <SpeakingPackageMiniPrep
          v-else-if="currentSection === 'mini_practice'"
          :key="'mini'"
          :mini="packageData.mini_practice"
          :story-spine="packageData.story_spine"
          :prep-done="Boolean(state?.mini_practice_prep_done)"
          :advancing="advancing"
          @prep-complete="$emit('mini-prep')"
          @continue="$emit('advance')"
        />
        <SpeakingPackageComplete
          v-else-if="currentSection === 'completed'"
          :key="'done'"
          :ready="readyForDiscussion"
          :title="packageData.input_material?.title"
          @restart="$emit('restart')"
          @start-discussion="$emit('start-discussion')"
        />
      </Transition>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import LoadingState from '../common/LoadingState.vue'
import SpeakingPackageIntro from './SpeakingPackageIntro.vue'
import SpeakingPackageMaterial from './SpeakingPackageMaterial.vue'
import SpeakingPackageVocabulary from './SpeakingPackageVocabulary.vue'
import SpeakingPackageTeaching from './SpeakingPackageTeaching.vue'
import SpeakingPackageMiniPrep from './SpeakingPackageMiniPrep.vue'
import SpeakingPackageComplete from './SpeakingPackageComplete.vue'

const props = defineProps({
  loading: { type: Boolean, default: false },
  advancing: { type: Boolean, default: false },
  error: { type: String, default: '' },
  packageData: { type: Object, default: null },
  constraintsSummary: { type: Object, default: () => ({}) },
  state: { type: Object, default: null },
  sectionProgress: { type: Object, default: () => ({}) },
  currentSection: { type: String, default: 'not_started' },
  readyForDiscussion: { type: Boolean, default: false },
})

defineEmits(['advance', 'mark-vocab', 'mark-block', 'mini-prep', 'open-latest', 'restart', 'retry', 'start-discussion'])

const { t } = useI18n()

const railSections = [
  'introduction',
  'reading',
  'vocabulary',
  'teaching',
  'mini_practice',
  'completed',
]

const completedSet = computed(() => new Set(props.state?.completed_sections || []))
</script>
