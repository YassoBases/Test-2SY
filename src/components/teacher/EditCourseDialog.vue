<template>
  <TeacherDialog
    :model-value="modelValue"
    persistent
    scrollable
    :close-disabled="saving"
    @update:model-value="$emit('update:modelValue', $event)"
    @close="close"
  >
    <template #header>
      <TeacherHero
        class="tds-workspace-shell__hero"
        variant="compact"
        :eyebrow="$t('teacher.course.editSpace')"
        :title="$t('teacher.actions.editClass')"
        :subtitle="$t('teacher.course.editDesc')"
      />
    </template>

    <v-alert v-if="error" type="error" variant="tonal" class="rounded-lg">{{ error }}</v-alert>

    <TeacherForm>
      <TeacherFormSection
        animated
        :title="$t('teacher.course.basicInfo')"
        :description="$t('teacher.course.basicDesc')"
      >
        <TeacherFormField
          mode="floating"
          size="hero"
          :hint="$t('teacher.course.nameHint')"
        >
          <v-text-field
            v-model="title"
            :label="$t('teacher.labels.className')"
            :placeholder="$t('teacher.course.namePlaceholder')"
            variant="outlined"
            density="comfortable"
            hide-details="auto"
          />
        </TeacherFormField>

        <TeacherFormField mode="floating" size="description" :hint="$t('teacher.course.descOptional')">
          <v-textarea
            v-model="description"
            :label="$t('teacher.labels.classDescription')"
            :placeholder="$t('teacher.course.descPlaceholder')"
            variant="outlined"
            rows="4"
            auto-grow
            hide-details
          />
        </TeacherFormField>
      </TeacherFormSection>

      <TeacherFormSection
        animated
        :title="$t('teacher.course.teachingDetails')"
        :description="$t('teacher.course.editTeachingDesc')"
        :columns="2"
      >
        <TeacherFormField>
          <v-text-field
            :model-value="gradeLabel"
            :label="$t('teacher.labels.grade')"
            variant="outlined"
            density="comfortable"
            readonly
            hide-details="auto"
          />
        </TeacherFormField>

        <TeacherFormField>
          <v-select
            v-model="subjectId"
            :items="subjectItems"
            item-title="name_ar"
            item-value="id"
            :label="$t('teacher.labels.subject')"
            variant="outlined"
            density="comfortable"
            :loading="loadingContext"
            :no-data-text="$t('teacher.course.noSubjects')"
            hide-details="auto"
          />
        </TeacherFormField>

        <TeacherFormField
          mode="floating"
          size="secondary"
          :hint="$t('teacher.course.freeHint')"
          class="tds-form__field--full"
        >
          <v-text-field
            v-model.number="price"
            :label="$t('teacher.labels.price')"
            type="number"
            min="0"
            variant="outlined"
            density="comfortable"
            hide-details="auto"
          />
        </TeacherFormField>
      </TeacherFormSection>

      <TeacherFormSection
        animated
        :title="$t('teacher.quizzes.publishSection')"
        :description="$t('teacher.course.publishDesc')"
      >
        <TeacherPublishField
          v-model="isPublished"
          mode="stack"
          :label="$t('teacher.course.publishLabel')"
          :description="$t('teacher.course.publishHint')"
        />
      </TeacherFormSection>
    </TeacherForm>

    <template #footer>
      <TeacherButtonGroup align="end">
        <TeacherButton variant="ghost" :disabled="saving" @click="close">
          {{ $t('common.cancel') }}
        </TeacherButton>
        <TeacherButton variant="primary" :loading="saving" @click="submit">
          {{ $t('teacher.actions.saveEdits') }}
          <v-icon end>mdi-arrow-left</v-icon>
        </TeacherButton>
      </TeacherButtonGroup>
    </template>
  </TeacherDialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import {
  TeacherDialog,
  TeacherHero,
  TeacherForm,
  TeacherFormSection,
  TeacherFormField,
  TeacherPublishField,
  TeacherButton,
  TeacherButtonGroup,
} from './design-system/index.js'
import { fetchCourseFormContext, updateTeacherCourse } from '../../api/teacherCourses.js'
import { getErrorMessage } from '../../api/client.js'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  course: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue', 'saved'])

const loadingContext = ref(false)
const saving = ref(false)
const error = ref('')
const subjectItems = ref([])
const subjectId = ref(null)
const title = ref('')
const description = ref('')
const price = ref(0)
const isPublished = ref(true)

const gradeLabel = computed(() => {
  const grade = props.course?.grade
  return grade ? t('teacher.labels.gradeNumber', { grade }) : '—'
})

function close() {
  if (!saving.value) emit('update:modelValue', false)
}

function fillFromCourse() {
  if (!props.course) return
  subjectId.value = props.course.subject_id
  title.value = props.course.title || ''
  description.value = props.course.description || ''
  price.value = Number(props.course.price) || 0
  isPublished.value = props.course.is_published !== false
}

async function loadContext() {
  if (!props.course?.grade) return
  loadingContext.value = true
  try {
    const ctx = await fetchCourseFormContext(props.course.grade)
    subjectItems.value = ctx.subjects || []
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.loadSubjects'))
  } finally {
    loadingContext.value = false
  }
}

async function submit() {
  if (!props.course?.course_id || !subjectId.value || !title.value.trim()) {
    error.value = t('teacher.validation.completeRequired')
    return
  }
  saving.value = true
  error.value = ''
  try {
    await updateTeacherCourse(props.course.course_id, {
      subject_id: subjectId.value,
      title: title.value.trim(),
      description: description.value.trim() || null,
      price: Number(price.value) || 0,
      is_published: isPublished.value,
    })
    emit('saved')
    emit('update:modelValue', false)
  } catch (e) {
    error.value = getErrorMessage(e, t('teacher.errors.saveEdits'))
  } finally {
    saving.value = false
  }
}

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      error.value = ''
      fillFromCourse()
      loadContext()
    }
  },
)

watch(subjectId, (id) => {
  const subj = subjectItems.value.find((s) => s.id === id)
  if (subj && (!title.value.trim() || title.value === props.course?.subject_name)) {
    title.value = subj.name_ar
  }
})
</script>
