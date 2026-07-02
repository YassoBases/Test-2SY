import { onMounted, onUnmounted, ref, watch } from 'vue'
import { exportParentHistoricalReport, fetchParentHistoricalReport } from '../api/parent.js'
import { getErrorMessage, getExportErrorMessage } from '../api/client.js'
import { resolveParentStudentId } from '../utils/parentStorage.js'
import { isApiMode } from '../utils/session.js'

const LOG = '[parent-reports:error-state]'

function traceRef(name, r) {
  return watch(
    r,
    (val, prev) => {
      if (val !== prev) {
        console.log(LOG, `${name}=`, val === '' ? '(empty)' : val)
      }
    },
    { immediate: true },
  )
}

export const REPORT_PERIODS = [
  { value: 'this_week', label: 'هذا الأسبوع' },
  { value: 'last_week', label: 'الأسبوع السابق' },
  { value: 'this_month', label: 'هذا الشهر' },
  { value: 'last_month', label: 'الشهر السابق' },
  { value: 'custom', label: 'فترة مخصصة' },
]

export function useParentHistoricalReports(selectedStudentId) {
  const loading = ref(false)
  const exporting = ref(false)
  const loadError = ref('')
  const exportError = ref('')
  const report = ref(null)
  const period = ref('this_week')
  const customStart = ref('')
  const customEnd = ref('')
  let loadSeq = 0

  if (import.meta.env.DEV) {
    onMounted(() => {
      traceRef('loadError', loadError)
      traceRef('exportError', exportError)
    })
  }

  function setLoadError(value, source) {
    if (import.meta.env.DEV) {
      console.log(LOG, 'setLoadError', { source, value: value || '(empty)' })
    }
    loadError.value = value
  }

  function setExportError(value, source) {
    if (import.meta.env.DEV) {
      console.log(LOG, 'setExportError', { source, value: value || '(empty)' })
    }
    exportError.value = value
  }

  function clearLoadError(source = 'clearLoadError') {
    setLoadError('', source)
  }

  function clearExportError(source = 'clearExportError') {
    setExportError('', source)
  }

  function applySuccess(data) {
    clearLoadError('applySuccess')
    report.value = data
  }

  function applyFailure(err) {
    setLoadError(getErrorMessage(err, 'تعذر تحميل التقرير'), 'applyFailure')
    report.value = null
  }

  async function load() {
    const studentId = resolveParentStudentId(selectedStudentId)
    if (studentId == null) {
      loadSeq += 1
      report.value = null
      clearLoadError('load:no-student')
      loading.value = false
      return
    }
    if (!isApiMode()) {
      setLoadError('التقارير تتطلب الاتصال بالخادم', 'load:mock-mode')
      report.value = null
      return
    }

    const seq = ++loadSeq
    loading.value = true
    clearLoadError('load:start')

    try {
      const opts = { period: period.value }
      if (period.value === 'custom') {
        if (!customStart.value || !customEnd.value) {
          report.value = null
          return
        }
        opts.startDate = customStart.value
        opts.endDate = customEnd.value
      }
      const data = await fetchParentHistoricalReport(studentId, opts)
      if (seq !== loadSeq) return
      applySuccess(data)
    } catch (err) {
      if (seq !== loadSeq) return
      applyFailure(err)
    } finally {
      if (seq === loadSeq) loading.value = false
    }
  }

  async function retryLoad() {
    clearLoadError('retryLoad')
    return load()
  }

  async function exportReport(format) {
    const studentId = resolveParentStudentId(selectedStudentId)
    if (studentId == null) return
    exporting.value = true
    clearExportError('export:start')
    try {
      const opts = { period: period.value }
      if (period.value === 'custom') {
        opts.startDate = customStart.value
        opts.endDate = customEnd.value
      }
      const blob = await exportParentHistoricalReport(studentId, format, opts)
      const ext = format === 'xlsx' ? 'xlsx' : format
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `eduspark-report.${ext}`
      a.click()
      URL.revokeObjectURL(url)
      clearExportError('export:success')
    } catch (err) {
      if (import.meta.env.DEV) {
        console.error(LOG, 'exportReport failed', {
          format,
          code: err?.code,
          message: err?.message,
          status: err?.response?.status,
        })
      }
      setExportError(getExportErrorMessage(err, format), `export:${format}:failure`)
    } finally {
      exporting.value = false
    }
  }

  function setPeriod(value) {
    clearLoadError('setPeriod')
    period.value = value
    if (value !== 'custom') load()
  }

  function resetPeriodAndLoad() {
    clearLoadError('resetPeriodAndLoad')
    period.value = 'this_week'
    customStart.value = ''
    customEnd.value = ''
    return load()
  }

  onMounted(() => {
    clearLoadError('composable:mount')

    const retryIfNeeded = () => {
      if (document.visibilityState !== 'visible') return
      if (!loadError.value || loading.value) return
      retryLoad()
    }
    window.addEventListener('focus', retryIfNeeded)
    document.addEventListener('visibilitychange', retryIfNeeded)
    onUnmounted(() => {
      window.removeEventListener('focus', retryIfNeeded)
      document.removeEventListener('visibilitychange', retryIfNeeded)
    })
  })

  watch(
    () => resolveParentStudentId(selectedStudentId),
    (id, prev) => {
      if (id === prev) return
      clearLoadError('student-change')
    },
  )

  return {
    loading,
    exporting,
    loadError,
    exportError,
    error: loadError,
    report,
    period,
    customStart,
    customEnd,
    load,
    retryLoad,
    setPeriod,
    exportReport,
    resetPeriodAndLoad,
    clearLoadError,
    clearExportError,
  }
}

export function formatChangePercent(pct) {
  if (pct == null) return '—'
  const sign = pct >= 0 ? '+' : ''
  return `${sign}${pct}%`
}

export function barHeight(value, max) {
  if (!max || !value) return '4px'
  return `${Math.max(4, Math.round((value / max) * 100))}%`
}

export function maxTrendValue(points) {
  if (!points?.length) return 1
  return Math.max(...points.map((p) => p.value || 0), 1)
}
