<template>
  <section class="glass-card pa-5 pa-md-6 spk-package-panel" aria-labelledby="spk-pkg-intro-title">
    <div class="text-overline text-medium-emphasis mb-2">
      {{ t('student.languages.speakingJourney.packageLesson.section.introduction') }}
    </div>
    <h3 id="spk-pkg-intro-title" class="text-h5 font-weight-bold mb-2">
      {{ caseTitle }}
    </h3>
    <p class="text-body-1 text-medium-emphasis mb-4">
      {{ t('student.languages.speakingJourney.packageLesson.introLead') }}
    </p>

    <dl class="spk-meta-grid mb-5">
      <div>
        <dt>{{ t('student.languages.speakingJourney.packageLesson.mission') }}</dt>
        <dd>{{ constraints.learning_focus || constraints.mission_kind || '—' }}</dd>
      </div>
      <div>
        <dt>{{ t('student.languages.speakingJourney.packageLesson.duration') }}</dt>
        <dd>
          {{
            t('student.languages.speakingJourney.packageLesson.durationValue', {
              band: constraints.lesson_length_band || 'standard',
            })
          }}
        </dd>
      </div>
      <div>
        <dt>{{ t('student.languages.speakingJourney.packageLesson.cefr') }}</dt>
        <dd>{{ constraints.official_cefr || '—' }}</dd>
      </div>
      <div>
        <dt>{{ t('student.languages.speakingJourney.packageLesson.scenario') }}</dt>
        <dd>{{ constraints.scenario_type || '—' }}</dd>
      </div>
      <div v-if="worldTeaser">
        <dt>{{ t('student.languages.speakingJourney.packageLesson.world') }}</dt>
        <dd>{{ worldTeaser }}</dd>
      </div>
      <div v-if="conflictTeaser">
        <dt>{{ t('student.languages.speakingJourney.packageLesson.conflict') }}</dt>
        <dd>{{ conflictTeaser }}</dd>
      </div>
    </dl>

    <div v-if="(constraints.objectives || []).length" class="mb-5">
      <h4 class="text-subtitle-2 font-weight-bold mb-2">
        {{ t('student.languages.speakingJourney.packageLesson.objectives') }}
      </h4>
      <ul class="spk-objective-list">
        <li v-for="(obj, i) in constraints.objectives" :key="i">{{ obj }}</li>
      </ul>
    </div>

    <v-alert type="info" variant="tonal" class="mb-5 rounded-lg" role="status">
      {{ t('student.languages.speakingJourney.packageLesson.readinessMessage') }}
    </v-alert>

    <v-btn color="primary" size="large" class="spk-pressable" :loading="advancing" @click="$emit('continue')">
      {{ t('student.languages.speakingJourney.packageLesson.continue') }}
    </v-btn>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  constraints: { type: Object, default: () => ({}) },
  packageData: { type: Object, default: null },
  advancing: { type: Boolean, default: false },
})
defineEmits(['continue'])
const { t } = useI18n()

const caseTitle = computed(
  () =>
    props.packageData?.story_spine?.title
    || props.packageData?.input_material?.title
    || props.constraints.story_title_hint
    || props.constraints.learning_focus
    || '—',
)

const worldTeaser = computed(() => {
  const world = props.constraints.story_world || props.packageData?.story_spine?.setting || ''
  if (!world) return ''
  return world.length > 140 ? `${world.slice(0, 137)}…` : world
})

const conflictTeaser = computed(() => {
  const conflict =
    props.packageData?.story_spine?.conflict
    || props.packageData?.story_spine?.problem
    || ''
  if (!conflict) return ''
  return conflict.length > 140 ? `${conflict.slice(0, 137)}…` : conflict
})
</script>
