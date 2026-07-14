<template>
  <div class="onboarding-page">
    <OnboardingStepper current="subjects" />
    <h1 class="text-h5 font-weight-bold mb-2 text-center">{{ t('auth.onboarding.subjects.title') }}</h1>
    <p class="text-body-2 text-medium-emphasis mb-6 text-center">
      {{ t('auth.onboarding.subjects.subtitle') }}
    </p>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{ error }}</v-alert>

    <div v-if="loading" class="text-center py-8">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <div v-else class="subjects-list d-flex flex-column gap-4">
      <v-card
        v-for="s in subjects"
        :key="s.id"
        class="subject-block glass-card pa-4"
        :class="{ 'subject-block--selected': selectedIds.includes(s.id) }"
        variant="flat"
        @click="toggle(s.id)"
      >
        <div class="d-flex align-center gap-3 mb-3">
          <v-icon :color="selectedIds.includes(s.id) ? 'secondary' : 'grey'">
            {{ selectedIds.includes(s.id) ? 'mdi-check-circle' : 'mdi-book-outline' }}
          </v-icon>
          <div class="text-subtitle-1 font-weight-bold flex-grow-1">{{ subjectName(s) }}</div>
          <v-chip size="x-small" variant="tonal" color="primary">
            {{ t('auth.onboarding.subjects.teacherCount', { count: (teachersBySubject[s.id] || []).length }) }}
          </v-chip>
        </div>

        <div v-if="teachersBySubject[s.id]?.length" class="teachers-preview">
          <div
            v-for="teacher in teachersBySubject[s.id]"
            :key="teacher.id"
            class="teacher-chip"
          >
            <TeacherAvatar :name="teacher.full_name" :image-url="teacher.image_url" :size="36" />
            <div class="teacher-chip__info min-width-0">
              <div class="text-caption font-weight-bold text-truncate">{{ teacher.full_name }}</div>
              <div class="d-flex align-center gap-1">
                <v-icon size="12" color="warning">mdi-star</v-icon>
                <span class="text-caption">{{ Number(teacher.rating).toFixed(1) }}</span>
              </div>
            </div>
          </div>
        </div>
        <p v-else class="text-caption text-medium-emphasis mb-0">
          {{ t('auth.onboarding.subjects.noTeachers') }}
        </p>
      </v-card>
    </div>

    <OnboardingNavFooter :back-to="ROUTES.ONBOARDING_PERSONALIZE">
      <v-btn
        class="btn-glow"
        size="large"
        rounded="lg"
        :disabled="!selectedIds.length || saving"
        :loading="saving"
        @click="continueNext"
      >
        {{ t('auth.onboarding.subjects.continue') }}
      </v-btn>
    </OnboardingNavFooter>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useLocalizedLabels } from '../../composables/useLocalizedLabels.js'
import OnboardingNavFooter from '../../components/onboarding/OnboardingNavFooter.vue'
import OnboardingStepper from '../../components/onboarding/OnboardingStepper.vue'
import TeacherAvatar from '../../components/onboarding/TeacherAvatar.vue'
import { fetchSubjects, fetchTeachers } from '../../api/catalog.js'
import { fetchOnboardingStatus, saveOnboardingSubjects } from '../../api/onboarding.js'
import { getErrorMessage } from '../../api/client.js'
import { ROUTES } from '../../constants/app.js'
import { getSession, setSession } from '../../utils/session.js'
import { mergeUserIntoSession } from '../../utils/studentFlow.js'

const { t } = useI18n()
const { subjectName } = useLocalizedLabels()
const router = useRouter()
const subjects = ref([])
const teachersBySubject = reactive({})
const selectedIds = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')

function toggle(id) {
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter((x) => x !== id)
  } else {
    selectedIds.value = [...selectedIds.value, id]
  }
}

onMounted(async () => {
  const grade = getSession()?.grade
  if (!grade) {
    await router.replace(ROUTES.ONBOARDING_GRADE)
    return
  }
  try {
    const [list, status] = await Promise.all([
      fetchSubjects(grade),
      fetchOnboardingStatus(),
    ])
    subjects.value = list
    selectedIds.value = [...(status.selected_subject_ids || [])]

    await Promise.all(
      list.map(async (s) => {
        teachersBySubject[s.id] = await fetchTeachers(s.id, grade)
      }),
    )
  } catch (e) {
    error.value = getErrorMessage(e, t('auth.onboarding.errors.loadSubjects'))
  } finally {
    loading.value = false
  }
})

async function continueNext() {
  saving.value = true
  error.value = ''
  try {
    const status = await saveOnboardingSubjects(selectedIds.value)
    setSession(mergeUserIntoSession(getSession(), {
      onboarding_step: status.step,
      onboarding_complete: status.onboarding_complete,
    }))
    await router.push(ROUTES.ONBOARDING_TEACHERS)
  } catch (e) {
    error.value = getErrorMessage(e, t('auth.onboarding.errors.saveSubjects'))
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.subject-block {
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  transition: all 0.25s ease;
}

.subject-block:hover {
  border-color: rgba(124, 108, 240, 0.35) !important;
}

.subject-block--selected {
  border-color: rgba(34, 211, 238, 0.45) !important;
  box-shadow: 0 0 28px rgba(34, 211, 238, 0.12) !important;
}

.teachers-preview {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.teacher-chip {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.35rem 0.5rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.min-width-0 {
  min-width: 0;
}
</style>
