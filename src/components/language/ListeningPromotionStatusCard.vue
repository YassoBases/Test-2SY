<template>
  <div>
    <v-card class="promo-status pa-6 mb-4" variant="flat">
      <div class="d-flex align-start gap-3 mb-4">
        <v-avatar color="secondary" variant="tonal" size="52" class="flex-shrink-0">
          <v-icon size="28">{{ canStart ? 'mdi-rocket-launch' : 'mdi-stairs-up' }}</v-icon>
        </v-avatar>
        <div class="flex-grow-1 min-width-0">
          <div class="text-overline text-medium-emphasis">{{ t('student.languages.listeningJourney.tabs.promotion') }}</div>
          <h3 class="text-h5 font-weight-bold mb-2">{{ headline }}</h3>
          <p class="text-body-1 text-medium-emphasis mb-0">{{ summary }}</p>
        </div>
      </div>

      <ListeningGatePanel
        v-if="!canStart && !hasActiveSession"
        :journey="journey"
        :can-start-test="canStart"
        class="gate-inline mb-0"
      />

      <div v-if="canStart || hasActiveSession" class="friendly-progress mt-2">
        <p class="text-body-1 font-weight-medium mb-0">{{ friendlyProgress }}</p>
      </div>
    </v-card>

    <div class="d-flex flex-wrap gap-3">
      <v-btn
        v-if="canStart"
        color="secondary"
        variant="flat"
        size="x-large"
        :loading="sessionLoading"
        prepend-icon="mdi-rocket-launch"
        class="px-8"
        @click="$emit('start')"
      >
        {{ t('student.languages.listeningPromotion.actions.startTest', { level: targetLevel }) }}
      </v-btn>
      <v-btn
        v-else-if="hasActiveSession"
        color="secondary"
        variant="flat"
        size="x-large"
        :loading="sessionLoading"
        prepend-icon="mdi-play-circle-outline"
        class="px-8"
        @click="$emit('resume')"
      >
        {{ t('student.languages.listeningPromotion.actions.resumeTest') }}
      </v-btn>
      <v-btn
        v-else
        color="secondary"
        variant="tonal"
        size="x-large"
        prepend-icon="mdi-headphones"
        class="px-8"
        :to="ROUTES.STUDENT_LANGUAGES_LISTENING"
      >
        {{ t('student.languages.listeningPromotion.actions.keepPracticing') }}
      </v-btn>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ListeningGatePanel from './ListeningGatePanel.vue'
import { ROUTES } from '../../constants/app.js'

const props = defineProps({
  journey: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  canStart: { type: Boolean, default: false },
  hasActiveSession: { type: Boolean, default: false },
  sessionLoading: { type: Boolean, default: false },
})

defineEmits(['start', 'resume'])

const { t } = useI18n()

const targetLevel = computed(() => props.journey?.journey_target?.level || '')
const narrative = computed(() => props.journey?.narrative || {})

const headline = computed(() => {
  if (props.hasActiveSession) return t('student.languages.coach.promotionStatus.sessionActive')
  if (props.canStart) return t('student.languages.coach.promotion.unlockedTitle')
  return t('student.languages.coach.promotion.blockedTitle')
})

const summary = computed(() => {
  if (props.hasActiveSession) return t('student.languages.coach.promotionStatus.resumeHint')
  if (props.canStart) return t('student.languages.coach.promotion.unlockedBody')
  return narrative.value.promotion_progress_message || ''
})

const friendlyProgress = computed(() => narrative.value.promotion_progress_message || '')
</script>

<style scoped>
.promo-status {
  border-radius: 24px;
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-secondary), 0.1) 0%,
    rgba(var(--v-theme-surface), 1) 60%
  );
  border: 1px solid rgba(var(--v-theme-on-surface), 0.06);
}
.gate-inline :deep(.unlock-card) {
  padding: 0 !important;
  border: none;
  background: transparent;
  margin-bottom: 0 !important;
}
.min-width-0 {
  min-width: 0;
}
</style>
