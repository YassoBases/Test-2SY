<template>
  <v-dialog
    :model-value="modelValue"
    max-width="760"
    persistent
    scrollable
    transition="dialog-bottom-transition"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <v-card class="create-course-dialog" variant="flat">
      <header class="create-course-dialog__header">
        <div>
          <p class="create-course-dialog__eyebrow">{{ $t('teacher.course.newSpace') }}</p>
          <h2 class="create-course-dialog__title">{{ $t('teacher.actions.createNewClass') }}</h2>
          <p class="create-course-dialog__intro">
            {{ $t('teacher.course.createIntro') }}
          </p>
        </div>
        <v-btn icon variant="text" :disabled="saving" :aria-label="$t('common.close')" @click="close">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </header>

      <v-card-text class="create-course-dialog__body pa-0">
        <v-alert v-if="error" type="error" variant="tonal" class="rounded-lg">{{ error }}</v-alert>

        <section class="create-course-section" aria-labelledby="create-course-basic">
          <div class="create-course-section__head">
            <h3 id="create-course-basic" class="create-course-section__title">{{ $t('teacher.course.basicInfo') }}</h3>
            <p class="create-course-section__desc">{{ $t('teacher.course.basicDesc') }}</p>
          </div>

          <div class="create-course-section__grid">
            <div>
              <v-text-field
                v-model="title"
                :label="$t('teacher.labels.className')"
                :placeholder="$t('teacher.course.namePlaceholder')"
                variant="outlined"
                density="comfortable"
                class="create-course-field create-course-field--hero"
                :rules="[rules.required]"
                hide-details="auto"
              />
              <p class="create-course-field-hint">{{ $t('teacher.course.nameHint') }}</p>
            </div>

            <div>
              <v-textarea
                v-model="description"
                :label="$t('teacher.labels.classDescription')"
                :placeholder="$t('teacher.course.descPlaceholder')"
                variant="outlined"
                rows="4"
                auto-grow
                class="create-course-field create-course-field--description"
                hide-details
              />
              <p class="create-course-field-hint">{{ $t('teacher.course.descOptional') }}</p>
            </div>
          </div>
        </section>

        <section class="create-course-section" aria-labelledby="create-course-teaching">
          <div class="create-course-section__head">
            <h3 id="create-course-teaching" class="create-course-section__title">{{ $t('teacher.course.teachingDetails') }}</h3>
            <p class="create-course-section__desc">{{ $t('teacher.course.teachingDesc') }}</p>
          </div>

          <div class="create-course-section__grid create-course-section__grid--2">
            <v-select
              v-model="grade"
              :items="gradeItems"
              item-title="label"
              item-value="value"
              :label="$t('teacher.labels.grade')"
              variant="outlined"
              density="comfortable"
              class="create-course-field"
              :loading="loadingContext"
              hide-details="auto"
              @update:model-value="onGradeChange"
            />
            <v-select
              v-model="subjectId"
              :items="subjectItems"
              item-title="name_ar"
              item-value="id"
              :label="$t('teacher.labels.subject')"
              variant="outlined"
              density="comfortable"
              class="create-course-field"
              :loading="loadingContext"
              :disabled="!subjectItems.length"
              :no-data-text="$t('teacher.course.noSubjects')"
              hide-details="auto"
            />
          </div>

          <div class="mt-4">
            <v-text-field
              v-model.number="price"
              :label="$t('teacher.labels.price')"
              type="number"
              min="0"
              variant="outlined"
              density="comfortable"
              class="create-course-field create-course-field--secondary"
              hide-details="auto"
            />
            <p class="create-course-field-hint">{{ $t('teacher.course.freeHint') }}</p>
          </div>
        </section>

        <section class="create-course-section" aria-labelledby="create-course-appearance">
          <div class="create-course-section__head">
            <h3 id="create-course-appearance" class="create-course-section__title">{{ $t('teacher.course.appearance') }}</h3>
            <p class="create-course-section__desc">{{ $t('teacher.course.appearanceDesc') }}</p>
          </div>

          <div class="create-course-section__grid create-course-section__grid--uploads">
            <CourseImageUploadCard
              v-model="thumbnailFile"
              :label="$t('teacher.labels.coverImage')"
              :hint="$t('teacher.course.coverHint')"
              icon="mdi-image-outline"
            />
            <CourseImageUploadCard
              v-model="bannerFile"
              :label="$t('teacher.labels.bannerImage')"
              :hint="$t('teacher.course.bannerHint')"
              icon="mdi-panorama-outline"
            />
          </div>
        </section>

        <section class="create-course-section" aria-labelledby="create-course-publishing">
          <div class="create-course-section__head">
            <h3 id="create-course-publishing" class="create-course-section__title">{{ $t('teacher.quizzes.publishSection') }}</h3>
            <p class="create-course-section__desc">{{ $t('teacher.course.publishDesc') }}</p>
          </div>

          <div class="create-course-publish">
            <p class="create-course-publish__label">{{ $t('teacher.course.publishLabel') }}</p>
            <p class="create-course-publish__hint">
              {{ $t('teacher.course.publishHint') }}
            </p>
            <div class="create-course-publish__control">
              <v-switch
                v-model="isPublished"
                color="secondary"
                hide-details
                density="comfortable"
              />
            </div>
          </div>
        </section>
      </v-card-text>

      <footer class="create-course-dialog__footer">
        <v-btn
          class="create-course-dialog__cancel"
          variant="text"
          :disabled="saving"
          @click="close"
        >
          {{ $t('common.cancel') }}
        </v-btn>
        <v-btn
          class="btn-glow create-course-dialog__submit"
          rounded="lg"
          :loading="saving"
          @click="submit"
        >
          {{ $t('teacher.course.createClassBtn') }}
          <v-icon end>mdi-arrow-left</v-icon>
        </v-btn>
      </footer>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import CourseImageUploadCard from './classes/CourseImageUploadCard.vue'
import { createTeacherCourse, fetchCourseFormContext } from '../../api/teacherCourses.js'
import { getErrorMessage } from '../../api/client.js'
import { ACADEMIC_GRADES } from '../../constants/app.js'
import '../../assets/styles/create-course-dialog.css'
import '../../assets/styles/teacher-typography.css'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue', 'created'])

const loadingContext = ref(false)
const saving = ref(false)
const error = ref('')
const grades = ref([...ACADEMIC_GRADES])
const subjects = ref([])

const grade = ref(ACADEMIC_GRADES[0])
const subjectId = ref(null)
const title = ref('')
const description = ref('')
const price = ref(0)
const isPublished = ref(true)
const thumbnailFile = ref(null)
const bannerFile = ref(null)

const rules = { required: (v) => !!String(v || '').trim() || t('teacher.labels.required') }

const gradeItems = computed(() =>
  grades.value.map((g) => ({ label: t('teacher.labels.gradeNumber', { grade: g }), value: g })),
)
const subjectItems = computed(() => subjects.value)

function pickFile(input) {
  if (!input) return null
  return Array.isArray(input) ? input[0] : input
}

async function loadContext(g) {
  loadingContext.value = true
  error.value = ''
  try {
    const ctx = await fetchCourseFormContext(g)
    grades.value = ctx.grades?.length ? ctx.grades : [...ACADEMIC_GRADES]
    subjects.value = ctx.subjects || []
    if (!grades.value.includes(grade.value)) {
      grade.value = grades.value[0]
    }
    if (!subjects.value.find((s) => s.id === subjectId.value)) {
      subjectId.value = subjects.value[0]?.id ?? null
    }
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadSubjects'))
  } finally {
    loadingContext.value = false
  }
}

function onGradeChange(g) {
  loadContext(g)
}

function close() {
  if (!saving.value) emit('update:modelValue', false)
}

function resetForm() {
  title.value = ''
  description.value = ''
  price.value = 0
  isPublished.value = true
  thumbnailFile.value = null
  bannerFile.value = null
  error.value = ''
}

async function submit() {
  if (!title.value.trim() || !subjectId.value || !grade.value) {
    error.value = t('teacher.validation.completeRequired')
    return
  }
  saving.value = true
  error.value = ''
  try {
    const course = await createTeacherCourse({
      title: title.value.trim(),
      description: description.value.trim() || null,
      subjectId: subjectId.value,
      grade: grade.value,
      price: Number(price.value) || 0,
      isPublished: isPublished.value,
      thumbnail: pickFile(thumbnailFile.value),
      banner: pickFile(bannerFile.value),
    })
    emit('created', course)
    resetForm()
    emit('update:modelValue', false)
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.createCourse'))
  } finally {
    saving.value = false
  }
}

watch(subjectId, (id) => {
  const subj = subjects.value.find((s) => s.id === id)
  if (subj) title.value = subj.name_ar
})

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      resetForm()
      loadContext(grade.value)
    }
  },
)
</script>
