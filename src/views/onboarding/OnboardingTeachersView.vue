<template>
  <div class="onboarding-page">
    <OnboardingStepper current="teachers" />
    <h1 class="text-h5 font-weight-bold mb-2 text-center">{{ t('auth.onboarding.teachers.title') }}</h1>
    <p class="text-body-2 text-medium-emphasis mb-6 text-center">
      {{ t('auth.onboarding.teachers.subtitle') }}
    </p>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{ error }}</v-alert>
    <div v-if="loading" class="text-center py-8"><v-progress-circular indeterminate color="primary" /></div>

    <div v-else>
      <section v-for="subj in subjectBlocks" :key="subj.id" class="mb-6">
        <h3 class="text-subtitle-1 font-weight-bold mb-3">{{ subj.name_ar }}</h3>
        <div class="d-flex flex-column gap-3">
          <TeacherPickCard
            v-for="teacher in subj.teachers"
            :key="teacher.id"
            :teacher="teacher"
            :selected="picks[subj.id] === teacher.id"
            @select="picks[subj.id] = teacher.id"
          />
        </div>
      </section>
    </div>

    <OnboardingNavFooter :back-to="ROUTES.ONBOARDING_SUBJECTS">
      <v-btn
        class="btn-glow"
        size="large"
        rounded="lg"
        :disabled="!allPicked || saving"
        :loading="saving"
        @click="finish"
      >
        {{ t('auth.onboarding.teachers.startLearning') }}
      </v-btn>
    </OnboardingNavFooter>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import OnboardingNavFooter from '../../components/onboarding/OnboardingNavFooter.vue'
import OnboardingStepper from '../../components/onboarding/OnboardingStepper.vue'
import TeacherPickCard from '../../components/onboarding/TeacherPickCard.vue'
import { fetchSubjects, fetchTeachers } from '../../api/catalog.js'
import {
  completeOnboarding,
  fetchOnboardingStatus,
  saveOnboardingTeachers,
} from '../../api/onboarding.js'
import { getErrorMessage } from '../../api/client.js'
import { ROUTES } from '../../constants/app.js'
import { getSession, setSession } from '../../utils/session.js'
import { mergeUserIntoSession } from '../../utils/studentFlow.js'

const { t } = useI18n()
const router = useRouter()
const subjectBlocks = ref([])
const picks = reactive({})
const loading = ref(true)
const saving = ref(false)
const error = ref('')

const allPicked = computed(() => {
  if (!subjectBlocks.value.length) return false
  return subjectBlocks.value.every((s) => picks[s.id])
})

onMounted(async () => {
  const grade = getSession()?.grade
  if (!grade) {
    await router.replace(ROUTES.ONBOARDING_GRADE)
    return
  }
  try {
    const status = await fetchOnboardingStatus()
    const subjectIds = status.selected_subject_ids || []
    if (!subjectIds.length) {
      await router.replace(ROUTES.ONBOARDING_SUBJECTS)
      return
    }
    for (const choice of status.teacher_choices || []) {
      picks[choice.subject_id] = choice.teacher_profile_id
    }
    const subjects = await fetchSubjects(grade)
    const selected = subjects.filter((s) => subjectIds.includes(s.id))
    const blocks = []
    for (const s of selected) {
      const teachers = await fetchTeachers(s.id, grade)
      blocks.push({ ...s, teachers })
    }
    subjectBlocks.value = blocks
  } catch (e) {
    error.value = getErrorMessage(e, t('auth.onboarding.errors.loadTeachers'))
  } finally {
    loading.value = false
  }
})

async function finish() {
  saving.value = true
  error.value = ''
  try {
    const choices = subjectBlocks.value.map((s) => ({
      subject_id: s.id,
      teacher_profile_id: picks[s.id],
    }))
    const status = await saveOnboardingTeachers(choices)
    await completeOnboarding()
    setSession(
      mergeUserIntoSession(getSession(), {
        onboarding_complete: true,
        needs_payment: false,
        onboarding_step: status.step || 'complete',
      }),
    )
    await router.push(ROUTES.STUDENT_COURSES)
  } catch (e) {
    error.value = getErrorMessage(e, t('auth.onboarding.errors.completeSelection'))
  } finally {
    saving.value = false
  }
}
</script>
