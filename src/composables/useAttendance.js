import { onMounted, ref } from 'vue'
import { fetchAttendanceSummaryApi } from '../api/attendance.js'
import { getErrorMessage } from '../api/client.js'
import { isApiMode } from '../utils/session.js'

const EMPTY = {
  attendance_percentage: 0,
  weekly_consistency: 0,
  streak_days: 0,
  inactive_days: 0,
  completed_sessions: 0,
  missed_sessions: 0,
  partial_days: 0,
  total_study_minutes_week: 0,
  weekly_calendar: [],
  monthly_overview: [],
  consistency_bars: [],
  alerts: [],
  ai_insights: [],
  recent_records: [],
  daily: [],
}

export function useAttendance({ autoLoad = true } = {}) {
  const loading = ref(false)
  const error = ref('')
  const summary = ref({ ...EMPTY })

  async function load() {
    loading.value = true
    error.value = ''
    try {
      if (!isApiMode()) {
        summary.value = { ...EMPTY }
        return
      }
      summary.value = await fetchAttendanceSummaryApi()
    } catch (err) {
      error.value = getErrorMessage(err, 'تعذر تحميل بيانات الحضور')
      summary.value = { ...EMPTY }
    } finally {
      loading.value = false
    }
  }

  if (autoLoad) {
    onMounted(() => load())
  }

  return { loading, error, summary, load }
}
