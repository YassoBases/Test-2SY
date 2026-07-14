<template>
  <div class="setup-page" dir="rtl">
    <v-container class="py-8" style="max-width: 640px">
      <h1 class="text-h5 font-weight-bold text-center mb-2">{{ $t('teacher.setup.title') }}</h1>
      <p class="text-body-2 text-medium-emphasis text-center mb-6">
        {{ $t('teacher.setup.subtitle') }}
      </p>

      <v-alert v-if="error" type="error" variant="tonal" class="mb-4">{{ error }}</v-alert>

      <v-card class="glass-card glass-card--solid pa-4 pa-md-5 mb-4" variant="flat">
        <v-text-field v-model="fullName" :label="$t('teacher.labels.fullName')" variant="outlined" class="mb-3" />
        <v-textarea v-model="bio" :label="$t('teacher.labels.bio')" variant="outlined" rows="3" class="mb-3" />
        <div v-if="avatarPreviewUrl" class="d-flex justify-center mb-4">
          <TeacherAvatar :name="fullName" :image-url="avatarPreviewUrl" :size="88" />
        </div>
        <v-file-input
          :label="$t('teacher.labels.avatar')"
          variant="outlined"
          prepend-icon="mdi-camera"
          accept="image/*"
          @update:model-value="onFile"
        />
        <v-btn class="mt-2" variant="tonal" :loading="savingProfile" @click="saveProfile">{{ $t('teacher.actions.saveProfile') }}</v-btn>
      </v-card>

      <v-card class="glass-card glass-card--solid pa-4 pa-md-5 mb-4" variant="flat">
        <p class="text-subtitle-2 font-weight-bold mb-3">{{ $t('teacher.profile.gradesSection') }}</p>
        <div class="d-flex flex-wrap gap-2 mb-4">
          <v-chip
            v-for="g in gradeOptions"
            :key="g"
            :color="selectedGrades.includes(g) ? 'primary' : undefined"
            variant="tonal"
            @click="toggleGrade(g)"
          >
            {{ g }}
          </v-chip>
        </div>
        <p class="text-subtitle-2 font-weight-bold mb-3">{{ $t('teacher.setup.subjectsHint') }}</p>
        <div v-if="!selectedGrades.length" class="text-caption text-medium-emphasis">{{ $t('teacher.setup.selectGradeForSubjects') }}</div>
        <template v-else>
          <div v-for="[grade, subjects] in subjectsByGrade" :key="grade" class="mb-4">
            <p class="text-caption text-medium-emphasis mb-2">{{ $t('teacher.labels.gradeNumber', { grade }) }}</p>
            <div class="d-flex flex-wrap gap-2">
              <v-chip
                v-for="s in subjects"
                :key="s.id"
                :color="selectedSubjects.includes(s.id) ? 'secondary' : undefined"
                variant="tonal"
                @click="toggleSubject(s.id)"
              >
                {{ s.name_ar }}
              </v-chip>
            </div>
          </div>
        </template>
        <v-btn variant="tonal" :loading="savingTeaching" @click="saveTeaching">{{ $t('teacher.actions.saveTeaching') }}</v-btn>
      </v-card>

      <v-card v-if="selectedGrades.length && selectedSubjects.length" class="glass-card glass-card--solid pa-4 pa-md-5 mb-4" variant="flat">
        <p class="text-subtitle-2 font-weight-bold mb-3">{{ $t('teacher.setup.createCourseOptional') }}</p>
        <v-text-field v-model="courseTitle" :label="$t('teacher.labels.courseTitle')" variant="outlined" class="mb-2" />
        <v-text-field v-model.number="coursePrice" :label="$t('teacher.labels.price')" type="number" variant="outlined" class="mb-2" />
        <v-btn variant="outlined" :loading="savingCourse" @click="addCourse">{{ $t('teacher.actions.createCourse') }}</v-btn>
      </v-card>

      <v-btn block size="large" rounded="lg" class="btn-glow" :loading="completing" @click="finish">
        {{ $t('teacher.actions.finishSetup') }}
      </v-btn>
    </v-container>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import TeacherAvatar from '../../components/onboarding/TeacherAvatar.vue'
import { useRouter } from 'vue-router'
import {
  completeTeacherSetup,
  createTeacherCourse,
  fetchTeacherSetupStatus,
  fetchTeacherSetupSubjects,
  updateTeacherProfile,
  updateTeacherTeaching,
  uploadTeacherAvatar,
} from '../../api/teacherSetup.js'
import { getErrorMessage } from '../../api/client.js'
import { ROUTES, ACADEMIC_GRADES } from '../../constants/app.js'
import { refreshTeacherProfileCache } from '../../composables/useTeacherProfile.js'
import { pickFirstFile } from '../../utils/fileInput.js'

const router = useRouter()
const fullName = ref('')
const bio = ref('')
const avatarFile = ref(null)
const savedAvatarUrl = ref(null)
const avatarPreviewUrl = computed(() => {
  if (avatarFile.value) return URL.createObjectURL(avatarFile.value)
  return savedAvatarUrl.value
})
const gradeOptions = ACADEMIC_GRADES
const selectedGrades = ref([])
const selectedSubjects = ref([])
const subjectOptions = ref([])
const courseTitle = ref('')
const coursePrice = ref(12000)
const error = ref('')
const savingProfile = ref(false)
const savingTeaching = ref(false)
const savingCourse = ref(false)
const completing = ref(false)

function toggleGrade(g) {
  if (selectedGrades.value.includes(g)) {
    selectedGrades.value = selectedGrades.value.filter((x) => x !== g)
  } else {
    selectedGrades.value = [...selectedGrades.value, g]
  }
}

function toggleSubject(id) {
  if (selectedSubjects.value.includes(id)) {
    selectedSubjects.value = selectedSubjects.value.filter((x) => x !== id)
  } else {
    selectedSubjects.value = [...selectedSubjects.value, id]
  }
}

const subjectsByGrade = computed(() => {
  const groups = new Map()
  for (const s of subjectOptions.value) {
    if (!groups.has(s.grade)) groups.set(s.grade, [])
    groups.get(s.grade).push(s)
  }
  return [...groups.entries()].sort((a, b) => a[0] - b[0])
})

function onFile(value) {
  avatarFile.value = pickFirstFile(value)
}

watch(selectedGrades, async (grades) => {
  if (!grades.length) {
    subjectOptions.value = []
    selectedSubjects.value = []
    return
  }
  try {
    const lists = await Promise.all(grades.map((g) => fetchTeacherSetupSubjects(g)))
    const map = new Map()
    lists.flat().forEach((s) => map.set(s.id, s))
    subjectOptions.value = [...map.values()]
    const allowed = new Set(subjectOptions.value.map((s) => s.id))
    selectedSubjects.value = selectedSubjects.value.filter((id) => allowed.has(id))
  } catch {
    subjectOptions.value = []
  }
})

onMounted(async () => {
  try {
    const status = await fetchTeacherSetupStatus()
    if (status.setup_complete) {
      await router.replace(ROUTES.TEACHER_DASHBOARD)
      return
    }
    fullName.value = status.full_name || ''
    bio.value = status.bio || ''
    savedAvatarUrl.value = status.image_url || null
    selectedGrades.value = [...(status.grades || [])]
    selectedSubjects.value = [...(status.subject_ids || [])]
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadSetup'))
  }
})

async function saveProfile() {
  savingProfile.value = true
  error.value = ''
  try {
    let status = await updateTeacherProfile({ fullName: fullName.value, bio: bio.value })
    if (avatarFile.value) {
      status = await uploadTeacherAvatar(avatarFile.value)
      savedAvatarUrl.value = status.image_url || savedAvatarUrl.value
      avatarFile.value = null
    }
    refreshTeacherProfileCache(status)
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.saveProfile'))
  } finally {
    savingProfile.value = false
  }
}

async function saveTeaching() {
  if (!selectedGrades.value.length) {
    error.value = t('teacher.validation.selectGrade')
    return
  }
  if (!selectedSubjects.value.length) {
    error.value = t('teacher.validation.selectSubject')
    return
  }
  savingTeaching.value = true
  error.value = ''
  try {
    await updateTeacherTeaching({
      subjectIds: selectedSubjects.value,
      grades: selectedGrades.value,
    })
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.saveTeaching'))
  } finally {
    savingTeaching.value = false
  }
}

async function addCourse() {
  if (!selectedSubjects.value.length || !selectedGrades.value.length) return
  savingCourse.value = true
  try {
    await createTeacherCourse({
      title: courseTitle.value || t('teacher.setup.newCourse'),
      subjectId: selectedSubjects.value[0],
      grade: selectedGrades.value[0],
      price: coursePrice.value,
    })
    courseTitle.value = ''
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.createCourseSetup'))
  } finally {
    savingCourse.value = false
  }
}

async function finish() {
  completing.value = true
  error.value = ''
  try {
    await saveProfile()
    await saveTeaching()
    await completeTeacherSetup()
    await router.push(ROUTES.TEACHER_DASHBOARD)
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.validation.completeRequired'))
  } finally {
    completing.value = false
  }
}
</script>

<style scoped>
.setup-page {
  min-height: 100dvh;
}
</style>
