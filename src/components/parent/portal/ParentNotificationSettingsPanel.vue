<template>
  <v-card class="glass-card pa-5 mb-6" variant="flat">
    <div class="d-flex align-center gap-2 mb-4">
      <v-icon color="primary">mdi-cog-outline</v-icon>
      <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.notifications.settings.title') }}</h3>
      <v-chip size="x-small" variant="tonal" color="info" class="ms-auto">{{ t('parent.notifications.settings.inApp') }}</v-chip>
    </div>

    <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mb-4 rounded-lg">
      {{ error }}
    </v-alert>

    <v-skeleton-loader v-if="loading && !local" type="list-item@7" />

    <template v-else-if="local">
      <v-row dense>
        <v-col cols="12" sm="6">
          <v-switch v-model="local.login_alerts" :label="t('parent.notifications.settings.loginAlerts')" color="primary" hide-details />
        </v-col>
        <v-col cols="12" sm="6">
          <v-switch v-model="local.logout_alerts" :label="t('parent.notifications.settings.logoutAlerts')" color="primary" hide-details />
        </v-col>
        <v-col cols="12" sm="6">
          <v-switch v-model="local.lesson_alerts" :label="t('parent.notifications.settings.lessonAlerts')" color="primary" hide-details />
        </v-col>
        <v-col cols="12" sm="6">
          <v-switch v-model="local.quiz_alerts" :label="t('parent.notifications.settings.quizAlerts')" color="primary" hide-details />
        </v-col>
        <v-col cols="12" sm="6">
          <v-switch v-model="local.low_score_alerts" :label="t('parent.notifications.settings.lowScoreAlerts')" color="primary" hide-details />
        </v-col>
        <v-col cols="12" sm="6">
          <v-switch v-model="local.inactivity_alerts" :label="t('parent.notifications.settings.inactivityAlerts')" color="primary" hide-details />
        </v-col>
        <v-col cols="12" sm="6">
          <v-switch v-model="local.planner_alerts" :label="t('parent.notifications.settings.plannerAlerts')" color="primary" hide-details />
        </v-col>
      </v-row>

      <v-divider class="my-4" />

      <v-row dense>
        <v-col cols="12" sm="6">
          <v-text-field
            v-model.number="local.inactivity_days"
            type="number"
            min="1"
            max="30"
            :label="t('parent.notifications.settings.inactivityDays')"
            variant="outlined"
            density="compact"
            :disabled="!local.inactivity_alerts"
            hide-details="auto"
          />
        </v-col>
        <v-col cols="12" sm="6">
          <v-text-field
            v-model.number="local.low_score_threshold"
            type="number"
            min="0"
            max="100"
            suffix="%"
            :label="t('parent.notifications.settings.lowScoreThreshold')"
            variant="outlined"
            density="compact"
            :disabled="!local.low_score_alerts"
            hide-details="auto"
          />
        </v-col>
      </v-row>

      <div class="d-flex justify-end mt-4">
        <v-btn
          color="primary"
          variant="flat"
          :loading="saving"
          :disabled="!dirty"
          @click="emitSave"
        >
          {{ t('parent.notifications.settings.save') }}
        </v-btn>
      </div>

      <p class="text-caption text-medium-emphasis mt-3 mb-0">
        {{ t('parent.notifications.settings.futureChannels') }}
      </p>
    </template>
  </v-card>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  settings: { type: Object, default: null },
  loading: { type: Boolean, default: false },
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['save'])

const { t } = useI18n()

const local = ref(null)
const snapshot = ref('')

watch(
  () => props.settings,
  (val) => {
    if (!val) {
      local.value = null
      snapshot.value = ''
      return
    }
    local.value = { ...val }
    snapshot.value = JSON.stringify(val)
  },
  { immediate: true },
)

const dirty = computed(() => local.value && JSON.stringify(local.value) !== snapshot.value)

function emitSave() {
  if (!local.value) return
  emit('save', {
    login_alerts: local.value.login_alerts,
    logout_alerts: local.value.logout_alerts,
    lesson_alerts: local.value.lesson_alerts,
    quiz_alerts: local.value.quiz_alerts,
    low_score_alerts: local.value.low_score_alerts,
    inactivity_alerts: local.value.inactivity_alerts,
    planner_alerts: local.value.planner_alerts,
    inactivity_days: local.value.inactivity_days,
    low_score_threshold: local.value.low_score_threshold,
  })
  snapshot.value = JSON.stringify(local.value)
}
</script>
