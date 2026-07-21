<template>
  <div class="page-container grammar-preview-page">
    <v-alert type="info" variant="tonal" class="mb-4 rounded-lg" dir="rtl" lang="ar">
      هذه معاينة محلية للمراجعة فقط. لا يتم إنشاء جلسة طالب ولا حفظ تقدم.
    </v-alert>

    <template v-if="loading">
      <v-skeleton-loader type="article, article, article" />
    </template>

    <AppEmptyState
      v-else-if="error || !lesson"
      icon="mdi-book-open-page-variant-outline"
      title="تعذّر تحميل معاينة الدرس"
      :description="error"
      action-label="العودة إلى القواعد"
      :action-to="homeTo"
    />

    <GrammarLessonPage
      v-else
      :lesson="lesson"
      :cefr="lesson.cefr_level"
      :preview-revision-id="revisionId"
      preview-mode
      @back="goHome"
      @retry="loadPreview"
      @finish="noop"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchGrammarLessonPreview } from '../../../api/grammar.js'
import GrammarLessonPage from '../../../components/grammar-lesson-v4/GrammarLessonPage.vue'
import AppEmptyState from '../../../components/ui/AppEmptyState.vue'
import { ROUTES } from '../../../constants/app.js'

const route = useRoute()
const router = useRouter()
const homeTo = ROUTES.STUDENT_GRAMMAR
const lesson = ref(null)
const loading = ref(false)
const error = ref('')
const revisionId = computed(() => String(route.query.revision_id || '').trim())

async function loadPreview() {
  lesson.value = null
  error.value = ''
  if (!revisionId.value) {
    error.value = 'افتح رابط معاينة يحتوي على رقم النسخة المطلوبة.'
    return
  }

  loading.value = true
  try {
    lesson.value = await fetchGrammarLessonPreview(revisionId.value)
  } catch {
    error.value = 'تعذّر تجهيز المعاينة الآمنة. تأكد أن preview مفعّل محليًا وأن النسخة جاهزة للمراجعة.'
  } finally {
    loading.value = false
  }
}

function goHome() {
  router.push(ROUTES.STUDENT_GRAMMAR)
}

function noop() {}

onMounted(loadPreview)
watch(revisionId, loadPreview)
</script>

<style scoped>
.grammar-preview-page {
  padding-top: 24px;
  padding-bottom: 48px;
}
</style>
