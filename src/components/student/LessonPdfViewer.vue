<template>
  <div class="pdf-viewer">
    <div v-if="loading" class="text-center py-8">
      <v-progress-circular indeterminate color="secondary" size="32" />
      <p class="text-caption mt-2">{{ t('student.lesson.pdf.loading') }}</p>
    </div>
    <v-alert v-else-if="error" type="error" variant="tonal" density="compact">{{ error }}</v-alert>
    <template v-else>
      <div class="pdf-toolbar d-flex align-center justify-space-between mb-3 flex-wrap gap-2">
        <div class="d-flex align-center gap-2">
          <v-btn icon="mdi-chevron-right" size="small" variant="tonal" :disabled="page <= 1" @click="go(page - 1)" />
          <span class="text-caption">{{ t('student.lesson.pdf.page', { page, total: totalPages }) }}</span>
          <v-btn
            icon="mdi-chevron-left"
            size="small"
            variant="tonal"
            :disabled="page >= totalPages"
            @click="go(page + 1)"
          />
        </div>
        <v-chip size="small" variant="tonal" color="secondary">{{ t('student.lesson.pdf.percentRead', { n: progressPercent }) }}</v-chip>
      </div>
      <canvas ref="canvasEl" class="pdf-canvas rounded-lg" />
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  url: { type: String, required: true },
})

const emit = defineEmits(['opened', 'progress'])

const loading = ref(true)
const error = ref('')
const page = ref(1)
const totalPages = ref(1)
const canvasEl = ref(null)
let pdfDoc = null

const progressPercent = computed(() => {
  if (totalPages.value <= 0) return 0
  return Math.round((page.value / totalPages.value) * 100)
})

async function getPdfJs() {
  const pdfjs = await import('pdfjs-dist')
  const { default: workerSrc } = await import('pdfjs-dist/build/pdf.worker.min.mjs?url')
  pdfjs.GlobalWorkerOptions.workerSrc = workerSrc
  return pdfjs
}

async function renderPage(num) {
  if (!pdfDoc || !canvasEl.value) return
  const pg = await pdfDoc.getPage(num)
  const viewport = pg.getViewport({ scale: 1.2 })
  const canvas = canvasEl.value
  const ctx = canvas.getContext('2d')
  canvas.height = viewport.height
  canvas.width = viewport.width
  await pg.render({ canvasContext: ctx, viewport }).promise
}

function reportProgress() {
  emit('progress', {
    pdf_percent: progressPercent.value,
    pdf_opened: true,
    on_final_page: page.value >= totalPages.value,
  })
}

async function go(num) {
  if (num < 1 || num > totalPages.value) return
  page.value = num
  await renderPage(num)
  reportProgress()
}

async function loadPdf() {
  loading.value = true
  error.value = ''
  try {
    const pdfjs = await getPdfJs()
    const res = await fetch(props.url)
    const buf = await res.arrayBuffer()
    pdfDoc = await pdfjs.getDocument({ data: buf }).promise
    totalPages.value = pdfDoc.numPages
    page.value = 1
    loading.value = false
    emit('opened')
    await renderPage(1)
    reportProgress()
  } catch (e) {
    error.value = t('student.lesson.pdf.errors.load')
    loading.value = false
  }
}

onMounted(loadPdf)
watch(() => props.url, loadPdf)
</script>

<style scoped>
.pdf-viewer {
  width: 100%;
}

.pdf-canvas {
  width: 100%;
  max-width: 100%;
  background: #fff;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
</style>
