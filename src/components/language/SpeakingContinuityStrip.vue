<template>
  <section
    class="spk-continuity"
    :aria-label="t('student.languages.speakingJourney.runtime.continuityLabel')"
  >
    <template v-for="(step, idx) in steps" :key="step.key">
      <div
        class="spk-continuity__step"
        :class="{
          'is-active': step.key === active,
          'is-done': stepOrder(step.key) < activeOrder,
        }"
        :aria-current="step.key === active ? 'step' : undefined"
      >
        <v-icon size="14" aria-hidden="true">{{ step.icon }}</v-icon>
        <span>{{ step.label }}</span>
      </div>
      <span
        v-if="idx < steps.length - 1"
        class="spk-continuity__sep"
        aria-hidden="true"
      />
    </template>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  /** home | lesson | alex | reflection */
  active: { type: String, default: 'home' },
})

const { t } = useI18n()

const order = ['home', 'lesson', 'alex', 'reflection']

const steps = computed(() => [
  {
    key: 'home',
    icon: 'mdi-home-outline',
    label: t('student.languages.speakingJourney.runtime.continuity.home'),
  },
  {
    key: 'lesson',
    icon: 'mdi-book-open-page-variant',
    label: t('student.languages.speakingJourney.runtime.continuity.lesson'),
  },
  {
    key: 'alex',
    icon: 'mdi-account-voice',
    label: t('student.languages.speakingJourney.runtime.continuity.alex'),
  },
  {
    key: 'reflection',
    icon: 'mdi-check-decagram-outline',
    label: t('student.languages.speakingJourney.runtime.continuity.reflection'),
  },
])

const activeOrder = computed(() => stepOrder(props.active))

function stepOrder(key) {
  const idx = order.indexOf(key)
  return idx < 0 ? 0 : idx
}
</script>
