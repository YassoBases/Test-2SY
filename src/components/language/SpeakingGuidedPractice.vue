<template>
  <section
    v-if="show"
    class="guided-practice glass-card pa-5 mb-5"
    aria-label="guided practice"
  >
    <div class="text-subtitle-1 font-weight-bold mb-2">
      {{ t('student.languages.speakingJourney.guided.title') }}
    </div>
    <p class="text-body-2 text-medium-emphasis mb-4">
      {{ t('student.languages.speakingJourney.guided.lead') }}
    </p>

    <div class="d-flex flex-wrap gap-2 mb-4">
      <v-chip
        v-for="action in actions"
        :key="action.key"
        :prepend-icon="action.icon"
        :color="action.color"
        variant="tonal"
        size="small"
      >
        {{ action.label }}
      </v-chip>
    </div>

    <div v-if="instruction" class="practice-prompt rounded-lg pa-4 mb-3" dir="auto">
      <div class="text-caption text-medium-emphasis mb-1">
        {{ t('student.languages.speakingJourney.guided.instructions') }}
      </div>
      <div class="text-body-1">{{ instruction }}</div>
    </div>
    <p v-if="context" class="text-body-2 text-medium-emphasis mb-0" dir="auto">{{ context }}</p>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  currentTask: { type: Object, default: null },
  currentActivityKind: { type: String, default: '' },
  activityInstructions: { type: String, default: '' },
})

const { t } = useI18n()

const show = computed(() => {
  const kind = String(props.currentActivityKind || '').toLowerCase()
  const mode = String(props.currentTask?.execution_mode || '').toLowerCase()
  return (
    kind.includes('guided') ||
    mode.includes('controlled') ||
    Boolean(props.currentTask?.controlled_required)
  )
})

const instruction = computed(
  () => props.currentTask?.instruction || props.activityInstructions || '',
)
const context = computed(() => props.currentTask?.context_descriptor || '')

/** Actions are presentational reflections of backend task flags — no evaluation. */
const actions = computed(() => {
  const task = props.currentTask || {}
  const mode = String(task.execution_mode || '').toLowerCase()
  const list = [
    {
      key: 'read',
      icon: 'mdi-book-open-outline',
      color: 'primary',
      label: t('student.languages.speakingJourney.guided.actions.read'),
    },
  ]
  if (mode.includes('study') || mode.includes('controlled') || task.controlled_required) {
    list.push({
      key: 'practice',
      icon: 'mdi-microphone-message',
      color: 'secondary',
      label: t('student.languages.speakingJourney.guided.actions.practice'),
    })
    list.push({
      key: 'respond',
      icon: 'mdi-reply-outline',
      color: 'primary',
      label: t('student.languages.speakingJourney.guided.actions.respond'),
    })
  }
  if (task.recording_required || mode.includes('recorded')) {
    list.push({
      key: 'record',
      icon: 'mdi-microphone',
      color: 'error',
      label: t('student.languages.speakingJourney.guided.actions.record'),
    })
  }
  if (task.uses_alex || mode.includes('live')) {
    list.push({
      key: 'alex',
      icon: 'mdi-account-voice',
      color: 'secondary',
      label: t('student.languages.speakingJourney.guided.actions.alex'),
    })
  }
  return list
})
</script>

<style scoped>
.guided-practice {
  border-radius: var(--em-radius-md, 16px);
}
.practice-prompt {
  background: rgba(var(--v-theme-on-surface), 0.04);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}
</style>
