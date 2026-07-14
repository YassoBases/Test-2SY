<template>
  <div>
    <v-card class="glass-card pa-5 pa-md-6 mb-5" variant="flat">
      <h3 class="text-h6 font-weight-bold mb-2">{{ $t('teacher.portfolio.impact') }}</h3>
      <p class="text-caption text-medium-emphasis mb-4">{{ $t('teacher.portfolio.impactHint') }}</p>
      <v-row dense>
        <v-col cols="12" sm="6">
          <v-text-field v-model.number="impact.total_students_taught" :label="$t('teacher.portfolio.totalStudents')" type="number" variant="outlined" density="comfortable" />
        </v-col>
        <v-col cols="12" sm="6">
          <v-text-field v-model.number="impact.grade12_students_taught" :label="$t('teacher.portfolio.grade12Students')" type="number" variant="outlined" density="comfortable" />
        </v-col>
        <v-col cols="12" sm="6">
          <v-text-field v-model.number="impact.students_completed_subject" :label="$t('teacher.portfolio.completedSubject')" type="number" variant="outlined" density="comfortable" />
        </v-col>
        <v-col cols="12" sm="6">
          <v-text-field v-model.number="impact.students_excellent_grades" :label="$t('teacher.portfolio.excellentGrades')" type="number" variant="outlined" density="comfortable" />
        </v-col>
        <v-col cols="12" sm="6">
          <v-text-field v-model.number="impact.years_teaching_subject" :label="$t('teacher.portfolio.yearsTeaching')" type="number" variant="outlined" density="comfortable" />
        </v-col>
      </v-row>
      <div class="d-flex justify-end">
        <v-btn color="primary" variant="tonal" :loading="savingImpact" @click="saveImpact">{{ $t('teacher.actions.saveImpact') }}</v-btn>
      </div>
    </v-card>

    <v-card class="glass-card pa-5 pa-md-6 mb-5" variant="flat">
      <h3 class="text-h6 font-weight-bold mb-2">{{ $t('teacher.portfolio.methodology') }}</h3>
      <v-textarea v-model="philosophy.teaching_style" :label="$t('teacher.portfolio.teachingStyle')" variant="outlined" rows="2" auto-grow class="mb-3" />
      <v-textarea v-model="philosophy.lesson_approach" :label="$t('teacher.portfolio.lessonApproach')" variant="outlined" rows="2" auto-grow class="mb-3" />
      <v-textarea v-model="philosophy.exam_preparation_strategy" :label="$t('teacher.portfolio.examStrategy')" variant="outlined" rows="2" auto-grow class="mb-3" />
      <div class="d-flex justify-end">
        <v-btn color="primary" variant="tonal" :loading="savingPhilosophy" @click="savePhilosophy">{{ $t('teacher.actions.savePhilosophy') }}</v-btn>
      </div>
    </v-card>

    <TeacherProfileEntryList
      :title="$t('teacher.portfolio.whyChoose')"
      icon="mdi-star-check-outline"
      icon-color="success"
      :empty-text="$t('teacher.portfolio.whyEmpty')"
      section="why"
      :items="whyPoints"
      :on-create="onCreateWhy"
      :on-update="onUpdateWhy"
      :on-delete="onDeleteWhy"
      @error="onError"
    />

    <v-card class="glass-card pa-5 pa-md-6 mb-5" variant="flat">
      <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
        <div class="d-flex align-center gap-2">
          <v-icon color="info">mdi-chart-box-outline</v-icon>
          <h3 class="text-h6 font-weight-bold mb-0">{{ $t('teacher.portfolio.academicStats') }}</h3>
        </div>
        <v-chip size="x-small" variant="tonal">{{ $t('teacher.portfolio.fromPlatform') }}</v-chip>
      </div>
      <v-row dense v-if="stats">
        <v-col v-for="item in statItems" :key="item.label" cols="6" sm="4">
          <div class="stat-box text-center pa-3 rounded-lg">
            <div class="text-h6 font-weight-bold">{{ item.value }}</div>
            <div class="text-caption text-medium-emphasis">{{ item.label }}</div>
          </div>
        </v-col>
      </v-row>
    </v-card>

    <v-card class="glass-card pa-5 pa-md-6 mb-5" variant="flat">
      <div class="d-flex align-center justify-space-between mb-4 flex-wrap gap-2">
        <h3 class="text-h6 font-weight-bold mb-0">{{ $t('teacher.portfolio.proDocuments') }}</h3>
        <v-btn size="small" variant="tonal" prepend-icon="mdi-upload" @click="docDialog = true">{{ $t('teacher.actions.uploadDocument') }}</v-btn>
      </div>
      <v-list v-if="documents.length" class="bg-transparent pa-0">
        <v-list-item v-for="doc in documents" :key="doc.id" class="entry-item rounded-lg mb-2 pa-3">
          <v-list-item-title>{{ doc.title }}</v-list-item-title>
          <v-list-item-subtitle>{{ docTypeLabel(doc.document_type) }}</v-list-item-subtitle>
          <template #append>
            <v-btn icon size="small" variant="text" color="error" :loading="deletingDocId === doc.id" @click="removeDoc(doc.id)">
              <v-icon>mdi-delete-outline</v-icon>
            </v-btn>
          </template>
        </v-list-item>
      </v-list>
      <p v-else class="text-body-2 text-medium-emphasis mb-0">{{ $t('teacher.portfolio.uploadCerts') }}</p>
    </v-card>

    <v-dialog v-model="docDialog" max-width="480" persistent>
      <v-card class="pa-5 rounded-xl">
        <h4 class="text-h6 font-weight-bold mb-4">{{ $t('teacher.actions.uploadProfessionalDoc') }}</h4>
        <v-text-field v-model="docForm.title" :label="$t('teacher.labels.documentTitleAsterisk')" variant="outlined" class="mb-3" />
        <v-select
          v-model="docForm.document_type"
          :items="docTypes"
          item-title="label"
          item-value="value"
          :label="$t('teacher.labels.documentType')"
          variant="outlined"
          class="mb-3"
        />
        <v-file-input v-model="docForm.file" :label="$t('teacher.portfolio.fileOrImage')" accept=".pdf,image/*" variant="outlined" class="mb-4" />
        <p class="text-caption text-medium-emphasis mb-4">{{ $t('teacher.portfolio.pdfUploadFormats') }}</p>
        <div class="d-flex justify-end gap-2">
          <v-btn variant="text" @click="docDialog = false">{{ $t('common.cancel') }}</v-btn>
          <v-btn color="primary" :loading="uploadingDoc" @click="submitDoc">{{ $t('common.add') }}</v-btn>
        </div>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import TeacherProfileEntryList from './TeacherProfileEntryList.vue'
import * as portfolioApi from '../../api/teacherPortfolio.js'
import { getErrorMessage } from '../../api/client.js'
import { pickFirstFile } from '../../utils/fileInput.js'
import { MAX_PDF_SIZE_BYTES, MAX_PDF_SIZE_LABEL } from '../../constants/app.js'

const emit = defineEmits(['error'])

const impact = reactive({
  total_students_taught: null,
  grade12_students_taught: null,
  students_completed_subject: null,
  students_excellent_grades: null,
  years_teaching_subject: null,
})
const philosophy = reactive({
  teaching_style: '',
  lesson_approach: '',
  exam_preparation_strategy: '',
})
const whyPoints = ref([])
const documents = ref([])
const stats = ref(null)
const savingImpact = ref(false)
const savingPhilosophy = ref(false)
const docDialog = ref(false)
const uploadingDoc = ref(false)
const deletingDocId = ref(null)
const docForm = reactive({ title: '', document_type: 'certificate', file: null })
const docTypes = [
  { value: 'certificate', label: t('teacher.portfolio.certificate') },
  { value: 'degree', label: t('teacher.portfolio.degree') },
  { value: 'training', label: t('teacher.portfolio.training') },
]

const statItems = computed(() => {
  const s = stats.value
  if (!s) return []
  return [
    { label: t('teacher.portfolio.activeStudents'), value: s.active_students },
    { label: t('teacher.portfolio.totalStudents'), value: s.total_students },
    { label: t('teacher.portfolio.courses'), value: s.courses_published },
    { label: t('teacher.analytics.kpiLessons'), value: s.lessons_published },
    { label: t('teacher.analytics.lessonCompletion'), value: `${s.average_lesson_completion_rate}%` },
    { label: t('teacher.portfolio.avgTests'), value: s.average_quiz_score != null ? `${s.average_quiz_score}%` : '—' },
  ]
})

function onError(err) {
  emit('error', typeof err === 'string' ? err : getErrorMessage(err, t('teacher.errors.save')))
}

function docTypeLabel(type) {
  return docTypes.find((d) => d.value === type)?.label || type
}

async function load() {
  const data = await portfolioApi.fetchTeacherPortfolio()
  Object.assign(impact, data.teaching_impact || {})
  Object.assign(philosophy, {
    teaching_style: data.teaching_philosophy?.teaching_style || '',
    lesson_approach: data.teaching_philosophy?.lesson_approach || '',
    exam_preparation_strategy: data.teaching_philosophy?.exam_preparation_strategy || '',
  })
  whyPoints.value = data.why_study_points || []
  documents.value = data.professional_documents || []
  stats.value = data.academic_statistics || null
}

async function saveImpact() {
  savingImpact.value = true
  try {
    await portfolioApi.updateTeachingImpact({ ...impact })
    await load()
  } catch (e) {
    onError(e)
  } finally {
    savingImpact.value = false
  }
}

async function savePhilosophy() {
  savingPhilosophy.value = true
  try {
    await portfolioApi.updateTeachingPhilosophy({ ...philosophy })
    await load()
  } catch (e) {
    onError(e)
  } finally {
    savingPhilosophy.value = false
  }
}

async function onCreateWhy(payload) {
  await portfolioApi.createWhyStudyPoint(payload)
  await load()
}

async function onUpdateWhy(id, payload) {
  await portfolioApi.updateWhyStudyPoint(id, payload)
  await load()
}

async function onDeleteWhy(id) {
  await portfolioApi.deleteWhyStudyPoint(id)
  await load()
}

async function submitDoc() {
  const file = pickFirstFile(docForm.file)
  if (!docForm.title.trim() || !file) {
    onError(t('teacher.validation.enterTitleAndFile'))
    return
  }
  const isPdf =
    file.type === 'application/pdf' || String(file.name || '').toLowerCase().endsWith('.pdf')
  if (isPdf && file.size > MAX_PDF_SIZE_BYTES) {
    onError(t('teacher.lessons.fileTooLarge', { size: MAX_PDF_SIZE_LABEL }))
    return
  }
  uploadingDoc.value = true
  try {
    await portfolioApi.uploadProfessionalDocument({
      title: docForm.title.trim(),
      documentType: docForm.document_type,
      file,
    })
    docDialog.value = false
    docForm.title = ''
    docForm.file = null
    await load()
  } catch (e) {
    onError(e)
  } finally {
    uploadingDoc.value = false
  }
}

async function removeDoc(id) {
  if (!window.confirm(t('teacher.confirm.deleteDocument'))) return
  deletingDocId.value = id
  try {
    await portfolioApi.deleteProfessionalDocument(id)
    await load()
  } catch (e) {
    onError(e)
  } finally {
    deletingDocId.value = null
  }
}

onMounted(load)
</script>

<style scoped>
.stat-box, .entry-item {
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
}
</style>
