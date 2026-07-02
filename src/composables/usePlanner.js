import { ref } from 'vue'
import {
  completePlannerSessionApi,
  fetchPlannerStateApi,
  generatePlannerPlanApi,
  sendPlannerChatApi,
} from '../api/planner.js'
import { getErrorMessage } from '../api/client.js'
import { isApiMode } from '../utils/session.js'

const EMPTY_PROFILE = {
  weak_subjects: [],
  preferred_period: 'evening',
  max_daily_minutes: 120,
}

const EMPTY_STREAK = {
  current_streak_days: 0,
  longest_streak_days: 0,
  task_streak_days: 0,
}

function applyPlannerPayload(data) {
  return {
    profile: data.profile || EMPTY_PROFILE,
    lifeEvents: data.life_events || [],
    schedule: data.schedule || [],
    chatHistory: data.chat_history || [],
    reasoning: data.reasoning || [],
    insights: data.insights || [],
    weeklyPlan: data.weekly_plan || [],
    subjectAnalytics: data.subject_analytics || [],
    recommendations: data.recommendations || [],
    streak: data.streak || EMPTY_STREAK,
    dashboardSnapshot: data.dashboard_snapshot || {},
    planStats: data.plan_stats || { planned_count: 0, completed_count: 0, missed_count: 0 },
  }
}

export function usePlanner() {
  const loading = ref(true)
  const generating = ref(false)
  const chatting = ref(false)
  const loadError = ref('')
  const profile = ref({ ...EMPTY_PROFILE })
  const lifeEvents = ref([])
  const schedule = ref([])
  const chatHistory = ref([])
  const reasoning = ref([])
  const insights = ref([])
  const weeklyPlan = ref([])
  const subjectAnalytics = ref([])
  const recommendations = ref([])
  const streak = ref({ ...EMPTY_STREAK })
  const dashboardSnapshot = ref({})
  const planStats = ref({ planned_count: 0, completed_count: 0, missed_count: 0 })

  function assignPayload(payload) {
    profile.value = payload.profile
    lifeEvents.value = payload.lifeEvents
    schedule.value = payload.schedule
    chatHistory.value = payload.chatHistory
    reasoning.value = payload.reasoning
    insights.value = payload.insights
    weeklyPlan.value = payload.weeklyPlan
    subjectAnalytics.value = payload.subjectAnalytics
    recommendations.value = payload.recommendations
    streak.value = payload.streak
    dashboardSnapshot.value = payload.dashboardSnapshot
    planStats.value = payload.planStats
  }

  function clearPlannerState() {
    assignPayload(applyPlannerPayload({}))
  }

  async function load() {
    loading.value = true
    loadError.value = ''
    try {
      if (!isApiMode()) {
        clearPlannerState()
        return
      }
      const data = await fetchPlannerStateApi()
      assignPayload(applyPlannerPayload(data))
    } catch (err) {
      loadError.value = getErrorMessage(err, 'تعذر تحميل المخطط الدراسي')
      clearPlannerState()
    } finally {
      loading.value = false
    }
  }

  async function generatePlan() {
    generating.value = true
    loadError.value = ''
    try {
      if (!isApiMode()) {
        loadError.value = 'المخطط الذكي يتطلب اتصالاً بالخادم'
        return
      }
      const data = await generatePlannerPlanApi()
      assignPayload(applyPlannerPayload(data))
    } catch (err) {
      loadError.value = getErrorMessage(err, 'تعذر توليد الخطة الأسبوعية')
    } finally {
      generating.value = false
    }
  }

  async function sendMessage(message) {
    chatting.value = true
    chatHistory.value.push({ id: Date.now(), role: 'user', content: message })
    try {
      if (!isApiMode()) {
        loadError.value = 'المخطط الذكي يتطلب اتصالاً بالخادم'
        return { reply: '', schedule: [], reasoning: [] }
      }
      const data = await sendPlannerChatApi(message)
      chatHistory.value.push({ id: Date.now() + 1, role: 'ai', content: data.reply })
      if (data.schedule?.length || data.profile || data.reasoning?.length) {
        assignPayload(
          applyPlannerPayload({
            ...data,
            schedule: data.schedule,
            profile: data.profile,
            reasoning: data.reasoning,
          }),
        )
      }
      if (data.profile) profile.value = data.profile
      if (data.reasoning?.length) reasoning.value = data.reasoning
      return data
    } catch (err) {
      loadError.value = getErrorMessage(err, 'تعذر إرسال الرسالة للمخطط')
      throw err
    } finally {
      chatting.value = false
    }
  }

  async function completeSession(slotId) {
    try {
      if (!isApiMode()) {
        loadError.value = 'المخطط الذكي يتطلب اتصالاً بالخادم'
        return
      }
      const data = await completePlannerSessionApi(slotId)
      assignPayload(applyPlannerPayload(data))
    } catch (err) {
      loadError.value = getErrorMessage(err, 'تعذر إكمال الجلسة')
      throw err
    }
  }

  return {
    loading,
    generating,
    chatting,
    loadError,
    profile,
    lifeEvents,
    schedule,
    chatHistory,
    reasoning,
    insights,
    weeklyPlan,
    subjectAnalytics,
    recommendations,
    streak,
    dashboardSnapshot,
    planStats,
    load,
    generatePlan,
    sendMessage,
    completeSession,
  }
}
