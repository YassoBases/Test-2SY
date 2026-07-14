<template>
  <div class="teacher-profile slide-up-enter-active">
    <PageHeader
      :eyebrow="$t('teacher.profile.eyebrow')"
      eyebrow-icon="mdi-account-cog"
      :title="$t('teacher.profile.title')"
      :subtitle="$t('teacher.profile.subtitle')"
      gradient-title
    />

    <v-alert v-if="error" type="error" variant="tonal" class="mb-5 rounded-lg" closable @click:close="error = ''">
      {{ error }}
    </v-alert>
    <v-alert v-if="success" type="success" variant="tonal" class="mb-5 rounded-lg" closable @click:close="success = ''">
      {{ success }}
    </v-alert>

    <v-skeleton-loader
      v-if="loading"
      type="article"
      class="teacher-profile-basic-skeleton tds-scope mb-5"
    />

    <TeacherWorkspaceCard
      v-else
      class="teacher-profile-basic"
      :title="$t('teacher.profile.basicTitle')"
      :meta="$t('teacher.profile.basicMeta')"
      :aria-label="$t('teacher.profile.basicTitle')"
    >
      <TeacherForm>
        <TeacherFormSection variant="compact" stack>
          <TeacherFormField
            mode="plain"
            :label="$t('teacher.labels.avatar')"
            :helper-before="$t('teacher.profile.avatarHelper')"
          >
            <div class="teacher-profile-basic__avatar-row">
              <TeacherAvatar :name="fullName" :image-url="avatarPreviewUrl" :size="56" />
              <v-file-input
                :label="$t('teacher.labels.changeAvatar')"
                variant="outlined"
                density="compact"
                prepend-icon="mdi-camera"
                accept="image/*"
                hide-details
                class="teacher-profile-basic__avatar-input"
                :loading="uploadingAvatar"
                @update:model-value="onAvatarFile"
              />
            </div>
          </TeacherFormField>

          <TeacherFormField mode="floating" size="hero">
            <v-text-field
              v-model="fullName"
              :label="$t('teacher.labels.fullName')"
              variant="outlined"
              density="comfortable"
              hide-details="auto"
            />
          </TeacherFormField>

          <TeacherFormField mode="floating" size="description">
            <v-textarea
              v-model="bio"
              :label="$t('teacher.labels.bioPublic')"
              variant="outlined"
              rows="3"
              auto-grow
              hide-details
            />
          </TeacherFormField>
        </TeacherFormSection>
      </TeacherForm>
    </TeacherWorkspaceCard>

    <TeacherProfileOnboardingWorkflow />

    <TeacherVoiceProfileSection />

    <v-skeleton-loader v-if="loading" type="article" class="glass-card rounded-lg" />

    <template v-else>
      <div class="teacher-profile__sections">
        <TeacherAiProfileSection />

        <TeacherProfileCvEditor />

        <TeacherWorkspaceCard
          class="teacher-profile-teaching"
          :title="$t('teacher.profile.teachingTitle')"
          :meta="$t('teacher.profile.teachingMeta')"
          :aria-label="$t('teacher.profile.teachingTitle')"
        >
          <TeacherForm>
            <TeacherFormSection
              variant="compact"
              :title="$t('teacher.profile.gradesSection')"
              :description="$t('teacher.profile.gradesTapHint')"
              stack
            >
              <div class="teacher-profile-teaching__grades" role="group" :aria-label="$t('teacher.profile.gradesAria')">
                <button
                  v-for="g in gradeOptions"
                  :key="g"
                  type="button"
                  class="teacher-profile-teaching__chip"
                  :class="{ 'teacher-profile-teaching__chip--active': selectedGrades.includes(g) }"
                  :aria-pressed="selectedGrades.includes(g)"
                  @click="toggleGrade(g)"
                >
                  {{ gradeLabel(g) }}
                </button>
              </div>
            </TeacherFormSection>

            <TeacherFormHint v-if="!selectedGrades.length" variant="info">
              {{ $t('teacher.profile.selectGradeHint') }}
            </TeacherFormHint>

            <template v-else>
              <TeacherFormSection variant="compact" :title="$t('teacher.profile.subjectsByGrade')" stack>
                <div class="teacher-profile-teaching__groups">
                  <article
                    v-for="group in subjectsByGrade"
                    :key="group.grade"
                    class="teacher-profile-teaching__grade-block"
                  >
                    <h4 class="teacher-profile-teaching__grade-title">{{ gradeLabel(group.grade) }}</h4>
                    <div
                      v-if="group.subjects.length"
                      class="teacher-profile-teaching__subjects"
                      role="group"
                      :aria-label="t('teacher.voice.subjectsForGrade', { grade: gradeLabel(group.grade) })"
                    >
                      <button
                        v-for="s in group.subjects"
                        :key="s.id"
                        type="button"
                        class="teacher-profile-teaching__chip teacher-profile-teaching__chip--subject"
                        :class="{ 'teacher-profile-teaching__chip--active': selectedSubjects.includes(s.id) }"
                        :aria-pressed="selectedSubjects.includes(s.id)"
                        @click="toggleSubject(s.id)"
                      >
                        {{ s.name_ar }}
                      </button>
                    </div>
                    <p v-else class="teacher-profile-teaching__empty-grade">
                      {{ $t('teacher.profile.noSubjectsForGrade') }}
                    </p>
                  </article>
                </div>
              </TeacherFormSection>
            </template>
          </TeacherForm>
        </TeacherWorkspaceCard>

        <div class="teacher-profile__footer">
          <TeacherButton variant="ghost" :disabled="saving" @click="loadProfile">
            {{ $t('teacher.actions.discardChanges') }}
          </TeacherButton>
          <TeacherButton variant="primary" size="large" :loading="saving" prepend-icon="mdi-content-save" @click="saveAll">
            {{ $t('teacher.actions.saveChanges') }}
          </TeacherButton>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import PageHeader from '../../components/common/PageHeader.vue'
import TeacherProfileOnboardingWorkflow from '../../components/teacher/profile/TeacherProfileOnboardingWorkflow.vue'
import TeacherAvatar from '../../components/onboarding/TeacherAvatar.vue'
import {
  TeacherWorkspaceCard,
  TeacherForm,
  TeacherFormSection,
  TeacherFormField,
  TeacherFormHint,
  TeacherButton,
} from '../../components/teacher/design-system/index.js'
import TeacherVoiceProfileSection from '../../components/teacher/TeacherVoiceProfileSection.vue'
import TeacherProfileCvEditor from '../../components/teacher/TeacherProfileCvEditor.vue'
import TeacherAiProfileSection from '../../components/teacher/TeacherAiProfileSection.vue'
import {
  fetchTeacherSetupStatus,
  fetchTeacherSetupSubjects,
  updateTeacherProfile,
  updateTeacherTeaching,
  uploadTeacherAvatar,
} from '../../api/teacherSetup.js'
import { getErrorMessage } from '../../api/client.js'
import { refreshTeacherProfileCache, invalidateTeacherProfileCache } from '../../composables/useTeacherProfile.js'
import { ACADEMIC_GRADES, gradeLabel } from '../../constants/app.js'
import { pickFirstFile } from '../../utils/fileInput.js'

const gradeOptions = ACADEMIC_GRADES

const loading = ref(true)
const saving = ref(false)
const uploadingAvatar = ref(false)
const error = ref('')
const success = ref('')
const fullName = ref('')
const bio = ref('')
const avatarFile = ref(null)
const savedAvatarUrl = ref(null)
const selectedGrades = ref([])
const selectedSubjects = ref([])
const subjectOptions = ref([])

const avatarPreviewUrl = computed(() => {
  if (avatarFile.value) return URL.createObjectURL(avatarFile.value)
  return savedAvatarUrl.value
})

const subjectsByGrade = computed(() =>
  selectedGrades.value
    .slice()
    .sort((a, b) => a - b)
    .map((grade) => ({
      grade,
      subjects: subjectOptions.value
        .filter((subject) => subject.grade === grade)
        .sort((a, b) => a.name_ar.localeCompare(b.name_ar, 'ar')),
    })),
)

function toggleGrade(g) {
  if (selectedGrades.value.includes(g)) {
    selectedGrades.value = selectedGrades.value.filter((x) => x !== g)
  } else {
    selectedGrades.value = [...selectedGrades.value, g].sort((a, b) => a - b)
  }
}

function toggleSubject(id) {
  if (selectedSubjects.value.includes(id)) {
    selectedSubjects.value = selectedSubjects.value.filter((x) => x !== id)
  } else {
    selectedSubjects.value = [...selectedSubjects.value, id]
  }
}

function applyAvatarStatus(status) {
  const url = status?.avatar_url || status?.image_url || null
  savedAvatarUrl.value = url
  refreshTeacherProfileCache(status)
  return url
}

async function onAvatarFile(value) {
  const file = pickFirstFile(value)
  avatarFile.value = file
  if (!file) return

  uploadingAvatar.value = true
  error.value = ''
  try {
    const status = await uploadTeacherAvatar(file)
    const url = applyAvatarStatus(status)
    avatarFile.value = null
    if (!url) {
      error.value = t('teacher.success.avatarUploadPartial')
      return
    }
    success.value = t('teacher.success.avatarSaved')
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.uploadAvatar'))
  } finally {
    uploadingAvatar.value = false
  }
}

async function loadSubjectsForGrades(grades) {
  if (!grades.length) {
    subjectOptions.value = []
    selectedSubjects.value = []
    return
  }
  try {
    const lists = await Promise.all(grades.map((g) => fetchTeacherSetupSubjects(g)))
    const map = new Map()
    lists.flat().forEach((s) => map.set(s.id, s))
    subjectOptions.value = [...map.values()].sort(
      (a, b) => a.grade - b.grade || a.name_ar.localeCompare(b.name_ar, 'ar'),
    )
    const allowed = new Set(subjectOptions.value.map((s) => s.id))
    selectedSubjects.value = selectedSubjects.value.filter((id) => allowed.has(id))
  } catch {
    subjectOptions.value = []
  }
}

watch(selectedGrades, (grades) => {
  loadSubjectsForGrades(grades)
})

async function loadProfile() {
  loading.value = true
  error.value = ''
  try {
    const status = await fetchTeacherSetupStatus()
    fullName.value = status.full_name || ''
    bio.value = status.bio || ''
    savedAvatarUrl.value = status.avatar_url || status.image_url || null
    selectedGrades.value = [...(status.grades || [])].sort((a, b) => a - b)
    selectedSubjects.value = [...(status.subject_ids || [])]
    avatarFile.value = null
    await loadSubjectsForGrades(selectedGrades.value)
    refreshTeacherProfileCache(status)
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadProfile'))
  } finally {
    loading.value = false
  }
}

async function saveAll() {
  if (!fullName.value.trim()) {
    error.value = t('teacher.validation.enterFullName')
    return
  }
  if (!selectedGrades.value.length) {
    error.value = t('teacher.validation.selectGrade')
    return
  }
  if (!selectedSubjects.value.length) {
    error.value = t('teacher.validation.selectSubject')
    return
  }

  saving.value = true
  error.value = ''
  success.value = ''
  try {
    let status = await updateTeacherProfile({ fullName: fullName.value.trim(), bio: bio.value.trim() || null })
    if (avatarFile.value) {
      status = await uploadTeacherAvatar(avatarFile.value)
      avatarFile.value = null
    }
    applyAvatarStatus(status)
    status = await updateTeacherTeaching({
      subjectIds: selectedSubjects.value,
      grades: selectedGrades.value,
    })
    applyAvatarStatus(status)
    invalidateTeacherProfileCache()
    await ensureTeacherProfileFromServer()
    success.value = t('teacher.success.profileSaved')
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.saveChanges'))
  } finally {
    saving.value = false
  }
}

async function ensureTeacherProfileFromServer() {
  const status = await fetchTeacherSetupStatus()
  applyAvatarStatus(status)
}

onMounted(loadProfile)
</script>

<style scoped>
.teacher-profile-basic {
  max-width: 52rem;
  margin-bottom: var(--em-space-lg);
  border: 1px solid var(--em-border-bright);
  box-shadow: none;
}

.teacher-profile-basic :deep(.tds-workspace__toolbar) {
  padding: var(--em-space-md) var(--em-space-md) var(--em-space-xs);
}

.teacher-profile-basic :deep(.tds-workspace__body) {
  padding: var(--em-space-xs) var(--em-space-md) var(--em-space-md);
}

.teacher-profile-basic :deep(.tds-form__section--compact) {
  padding-bottom: 0;
}

.teacher-profile-basic :deep(.tds-form__field-stack) {
  gap: var(--em-space-md);
}

.teacher-profile-basic__avatar-row {
  display: flex;
  align-items: center;
  gap: var(--em-space-md);
}

.teacher-profile-basic__avatar-input {
  flex: 1;
  min-width: 0;
}

.teacher-profile-basic-skeleton {
  max-width: 52rem;
  border-radius: var(--em-radius-lg);
}

.teacher-profile__sections {
  max-width: 52rem;
}

.teacher-profile-teaching {
  margin-bottom: var(--em-space-lg);
  border: 1px solid var(--em-border-bright);
  box-shadow: none;
}

.teacher-profile-teaching__grades,
.teacher-profile-teaching__subjects {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.teacher-profile-teaching__groups {
  display: flex;
  flex-direction: column;
  gap: var(--em-space-md);
}

.teacher-profile-teaching__grade-block {
  padding: 12px 14px;
  border-radius: var(--em-radius-sm, 8px);
  border: 1px solid var(--em-border-subtle);
  background: rgba(var(--v-theme-on-surface), 0.02);
}

.teacher-profile-teaching__grade-title {
  margin: 0 0 10px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--em-text);
}

.teacher-profile-teaching__empty-grade {
  margin: 0;
  font-size: 0.75rem;
  line-height: 1.5;
  color: rgb(var(--v-theme-warning));
}

.teacher-profile-teaching__chip {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid var(--em-border-subtle);
  background: var(--em-surface-control, rgba(var(--v-theme-on-surface), 0.02));
  color: var(--em-text);
  font-size: 0.8125rem;
  line-height: 1.35;
  cursor: pointer;
  transition:
    border-color var(--em-duration-fast, 0.15s) ease,
    background var(--em-duration-fast, 0.15s) ease;
}

.teacher-profile-teaching__chip:hover {
  border-color: var(--em-border-bright);
}

.teacher-profile-teaching__chip--active {
  border-color: var(--em-primary);
  background: color-mix(in srgb, var(--em-primary) 10%, transparent);
}

.teacher-profile-teaching__chip--subject.teacher-profile-teaching__chip--active {
  border-color: rgb(var(--v-theme-secondary));
  background: color-mix(in srgb, rgb(var(--v-theme-secondary)) 10%, transparent);
}

.teacher-profile__footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
  gap: var(--em-space-sm);
  margin-top: var(--em-space-md);
  padding-top: var(--em-space-md);
  padding-bottom: var(--em-space-xl);
  border-top: 1px solid var(--em-border-subtle);
}

:global([data-theme='morning']) .teacher-profile-teaching.tds-workspace {
  border-color: var(--em-border-bright);
  box-shadow: none;
}

:global([data-theme='morning']) .teacher-profile-basic.tds-workspace {
  border-color: var(--em-border-bright);
  box-shadow: none;
}
</style>
