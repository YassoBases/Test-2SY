<template>
  <div>
    <v-alert type="info" variant="tonal" density="compact" class="mb-5 rounded-lg">
      <v-icon start>mdi-eye-lock</v-icon>
      {{ t('parent.planner.readOnlyHint') }}
    </v-alert>

    <p v-if="planner.summary" class="text-body-2 text-medium-emphasis mb-5">{{ planner.summary }}</p>

    <v-row v-if="commitment" dense class="mb-6">
      <v-col cols="6" sm="3">
        <div class="metric-card pa-4 rounded-lg text-center h-100">
          <div class="text-h4 font-weight-bold eduspark-gradient-text">{{ commitment.adherence_rate }}%</div>
          <p class="text-caption text-medium-emphasis mb-0">{{ t('parent.planner.adherenceRate') }}</p>
        </div>
      </v-col>
      <v-col cols="6" sm="3">
        <div class="metric-card pa-4 rounded-lg text-center h-100">
          <div class="text-h5 font-weight-bold">
            {{ commitment.completed_count }} / {{ commitment.total_due_count }}
          </div>
          <p class="text-caption text-medium-emphasis mb-0">{{ t('parent.planner.completedTasks') }}</p>
        </div>
      </v-col>
      <v-col cols="6" sm="3">
        <div class="metric-card pa-4 rounded-lg text-center h-100">
          <div class="text-h5 font-weight-bold text-error">{{ commitment.missed_count }}</div>
          <p class="text-caption text-medium-emphasis mb-0">{{ t('parent.planner.missedTasks') }}</p>
        </div>
      </v-col>
      <v-col cols="6" sm="3">
        <div class="metric-card pa-4 rounded-lg text-center h-100">
          <div class="text-h5 font-weight-bold text-warning">{{ consistencyLabel }}</div>
          <p class="text-caption text-medium-emphasis mb-0">{{ t('parent.planner.activeDays') }}</p>
        </div>
      </v-col>
    </v-row>

    <v-card class="glass-card pa-4 pa-md-5 mb-6" variant="flat">
      <div class="d-flex align-center gap-2 mb-4">
        <v-icon color="primary">mdi-calendar-today</v-icon>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.planner.todayPlan') }}</h3>
      </div>
      <ParentPlannerTaskList v-if="planner.today_plan?.length" :tasks="planner.today_plan" />
      <p v-else class="text-body-2 text-medium-emphasis mb-0">{{ t('parent.planner.noTasksToday') }}</p>
    </v-card>

    <v-card v-if="planner.weekly_plan?.length" class="glass-card pa-4 pa-md-5 mb-6" variant="flat">
      <div class="d-flex align-center gap-2 mb-4">
        <v-icon color="secondary">mdi-calendar-week</v-icon>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.planner.weeklyPlan') }}</h3>
      </div>
      <div v-for="day in planner.weekly_plan" :key="day.date" class="mb-4">
        <p class="text-subtitle-2 font-weight-bold mb-2">{{ day.day_name }} — {{ day.date }}</p>
        <ParentPlannerTaskList :tasks="day.tasks" compact />
      </div>
    </v-card>

    <v-card v-if="planner.subject_breakdown?.length" class="glass-card pa-4 pa-md-5 mb-6" variant="flat">
      <div class="d-flex align-center gap-2 mb-4">
        <v-icon color="info">mdi-chart-bar</v-icon>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.planner.subjectAdherence') }}</h3>
      </div>
      <div v-for="subj in planner.subject_breakdown" :key="subj.subject_name" class="mb-3">
        <div class="d-flex justify-space-between mb-1">
          <span class="text-body-2 font-weight-medium">{{ subj.subject_name }}</span>
          <span class="text-body-2 font-weight-bold">{{ subj.adherence_percent }}%</span>
        </div>
        <v-progress-linear
          :model-value="subj.adherence_percent"
          :color="subj.adherence_percent >= 80 ? 'success' : subj.adherence_percent >= 60 ? 'warning' : 'error'"
          rounded
          height="8"
        />
      </div>
    </v-card>

    <v-row class="mb-6">
      <v-col cols="12" md="6">
        <v-card class="glass-card pa-4 h-100" variant="flat">
          <h3 class="text-subtitle-1 font-weight-bold mb-3">{{ t('parent.planner.upcomingTasks') }}</h3>
          <ParentPlannerTaskList v-if="planner.upcoming_tasks?.length" :tasks="planner.upcoming_tasks" compact />
          <p v-else class="text-caption text-medium-emphasis mb-0">{{ t('parent.planner.noUpcomingTasks') }}</p>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card class="glass-card pa-4 h-100" variant="flat">
          <h3 class="text-subtitle-1 font-weight-bold mb-3 text-error">{{ t('parent.planner.overdueTasks') }}</h3>
          <ParentPlannerTaskList v-if="planner.overdue_tasks?.length" :tasks="planner.overdue_tasks" compact />
          <p v-else class="text-caption text-medium-emphasis mb-0">{{ t('parent.planner.noOverdueTasks') }}</p>
        </v-card>
      </v-col>
    </v-row>

    <v-card class="glass-card pa-4 pa-md-5" variant="flat">
      <div class="d-flex align-center gap-2 mb-4">
        <v-icon color="primary">mdi-timeline-clock-outline</v-icon>
        <h3 class="text-h6 font-weight-bold mb-0">{{ t('parent.planner.taskSchedule') }}</h3>
      </div>
      <v-table v-if="planner.task_timeline?.length" density="comfortable" class="timeline-table rounded-lg">
        <thead>
          <tr>
            <th>{{ t('parent.planner.task') }}</th>
            <th>{{ t('parent.planner.plannedDate') }}</th>
            <th>{{ t('parent.planner.completedDate') }}</th>
            <th>{{ t('parent.planner.status') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in planner.task_timeline" :key="task.id">
            <td class="font-weight-medium">{{ task.task_name || task.subject }}</td>
            <td>{{ formatDate(task.planned_at) }}</td>
            <td>{{ task.completed_at ? formatDate(task.completed_at) : t('parent.common.emDash') }}</td>
            <td>
              <v-chip size="x-small" variant="tonal" :color="statusColor(task.status)">
                {{ statusSymbol(task.status) }} {{ task.status_label }}
              </v-chip>
            </td>
          </tr>
        </tbody>
      </v-table>
      <p v-else class="text-body-2 text-medium-emphasis mb-0">{{ t('parent.planner.noTasksRecorded') }}</p>
    </v-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import ParentPlannerTaskList from './ParentPlannerTaskList.vue'

const props = defineProps({
  planner: {
    type: Object,
    default: () => ({}),
  },
})

const { t, locale } = useI18n()

const commitment = computed(() => props.planner?.commitment || null)
const consistencyLabel = computed(
  () => props.planner?.weekly_consistency?.label || t('parent.planner.consistencyFallback'),
)

function dateLocale() {
  return locale.value === 'ar' ? 'ar-SY' : 'en-US'
}

function formatDate(iso) {
  if (!iso) return t('parent.common.emDash')
  try {
    return new Date(iso).toLocaleDateString(dateLocale(), {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

function statusSymbol(status) {
  if (status === 'completed') return '✓'
  if (status === 'missed') return '⚠️'
  if (status === 'overdue') return '⚠️'
  return '⏳'
}

function statusColor(status) {
  if (status === 'completed') return 'success'
  if (status === 'missed' || status === 'overdue') return 'error'
  return 'warning'
}
</script>

<style scoped>
.metric-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.timeline-table {
  background: rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.06);
}
</style>
