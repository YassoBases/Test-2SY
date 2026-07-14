<template>
  <div class="onboarding-page text-center">
    <OnboardingStepper current="grade" />
    <h1 class="text-h5 font-weight-bold mb-2">{{ t('auth.onboarding.grade.title') }}</h1>
    <p class="text-body-2 text-medium-emphasis mb-6">{{ t('auth.onboarding.grade.subtitle') }}</p>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{ error }}</v-alert>

    <v-row v-if="loading" justify="center">
      <v-col cols="12"><v-skeleton-loader type="image" /></v-col>
    </v-row>

    <v-row v-else class="grade-grid" justify="center">
      <v-col
        v-for="g in grades"
        :key="g.value"
        cols="6"
        sm="4"
        md="3"
      >
        <v-card
          class="grade-card glass-card pa-4"
          :class="{ 'grade-card--selected': selected === g.value }"
          variant="flat"
          @click="selected = g.value"
        >
          <div class="text-subtitle-2 font-weight-bold">{{ gradeLabel(g) }}</div>
        </v-card>
      </v-col>
    </v-row>

    <OnboardingNavFooter :back-to="ROUTES.WELCOME">
      <v-btn
        class="btn-glow"
        size="large"
        rounded="lg"
        :disabled="!selected || saving"
        :loading="saving"
        @click="continueNext"
      >
        {{ t('auth.onboarding.continue') }}
      </v-btn>
    </OnboardingNavFooter>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useLocalizedLabels } from '../../composables/useLocalizedLabels.js'
import OnboardingNavFooter from '../../components/onboarding/OnboardingNavFooter.vue'
import OnboardingStepper from '../../components/onboarding/OnboardingStepper.vue'
import { fetchGrades } from '../../api/catalog.js'
import { saveOnboardingGrade } from '../../api/onboarding.js'
import { getErrorMessage } from '../../api/client.js'
import { ROUTES } from '../../constants/app.js'
import { getSession, setSession } from '../../utils/session.js'
import { mergeUserIntoSession } from '../../utils/studentFlow.js'

const { t } = useI18n()
const { gradeLabel } = useLocalizedLabels()
const router = useRouter()
const grades = ref([])
const selected = ref(getSession()?.grade || null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    grades.value = await fetchGrades()
  } catch (e) {
    error.value = getErrorMessage(e, t('auth.onboarding.errors.loadGrades'))
  } finally {
    loading.value = false
  }
})

async function continueNext() {
  saving.value = true
  error.value = ''
  try {
    const status = await saveOnboardingGrade(selected.value)
    setSession(mergeUserIntoSession(getSession(), {
      onboarding_complete: status.onboarding_complete,
      needs_payment: status.needs_payment,
      payment_complete: status.payment_complete,
      onboarding_step: status.step,
      grade: status.grade,
    }))
    await router.push(ROUTES.ONBOARDING_PERSONALIZE)
  } catch (e) {
    error.value = getErrorMessage(e, t('auth.onboarding.errors.saveGrade'))
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.grade-card {
  cursor: pointer;
  transition:
    transform var(--em-duration-fast) var(--em-ease-out),
    border-color var(--em-duration-fast) var(--em-ease-out),
    box-shadow var(--em-duration-fast) var(--em-ease-out),
    background var(--em-duration-fast) var(--em-ease-out);
  border: 1px solid var(--em-border) !important;
  background: var(--em-surface-solid);
}

.grade-card:hover {
  transform: translateY(-2px);
  border-color: var(--em-border-bright) !important;
  box-shadow: var(--em-shadow-sm);
}

.grade-card--selected {
  border-color: var(--em-chip-selected-border) !important;
  background: var(--em-chip-selected-bg) !important;
  box-shadow: var(--em-shadow-md) !important;
}

.grade-card--selected :deep(.text-h6) {
  color: var(--em-chip-selected-text);
  font-weight: 700;
}
</style>
