<template>
  <div>
    <template v-if="!routine?.onboarding_complete">
      <v-card class="pa-6 text-center" rounded="xl" elevation="0" variant="flat">
        <v-icon icon="mdi-calendar-clock" size="56" color="grey" class="mb-3" />
        <div class="text-h6 font-weight-bold mb-1">{{ t('parent.routine.notSetupTitle') }}</div>
        <div class="text-body-1 text-medium-emphasis">
          {{ t('parent.routine.notSetupHint') }}
        </div>
      </v-card>
    </template>

    <template v-else>
      <v-card class="pa-6 text-center mb-6" rounded="xl" elevation="0" variant="flat">
        <div class="text-h6 font-weight-bold mb-4">{{ t('parent.routine.weeklyCommitment') }}</div>
        <v-progress-circular
          :model-value="routine.weekly_commitment_percent"
          :size="180"
          :width="18"
          :color="commitmentColor"
        >
          <span class="text-h3 font-weight-bold">{{ routine.weekly_commitment_percent }}%</span>
        </v-progress-circular>
        <div class="text-body-1 text-medium-emphasis mt-4">
          {{ commitmentMessage }}
        </div>
      </v-card>

      <v-card class="pa-6 mb-6" rounded="xl" elevation="0" variant="flat">
        <div class="text-h6 font-weight-bold mb-4">{{ t('parent.routine.todayScheduleQuestion', { day: routine.today_label }) }}</div>
        <div v-if="!routine.today_slots?.length" class="text-body-1 text-medium-emphasis text-center py-4">
          {{ t('parent.routine.noScheduleToday') }}
        </div>
        <div v-else class="d-flex flex-column ga-3">
          <div
            v-for="(slot, idx) in routine.today_slots"
            :key="idx"
            class="d-flex align-center justify-space-between pa-4 rounded-lg today-slot"
            :class="`today-slot--${slot.status}`"
          >
            <div class="d-flex align-center ga-3">
              <v-icon :icon="slotIcon(slot.status)" :color="slotIconColor(slot.status)" size="28" />
              <div>
                <div class="text-body-1 font-weight-bold">{{ slot.title }}</div>
                <div v-if="slot.subject" class="text-body-2 text-medium-emphasis">{{ slot.subject }}</div>
              </div>
            </div>
            <div class="text-body-1 font-weight-medium">{{ slot.start }} – {{ slot.end }}</div>
          </div>
        </div>
      </v-card>

      <v-card class="pa-6 mb-6" rounded="xl" elevation="0" variant="flat">
        <div class="text-h6 font-weight-bold mb-4">{{ t('parent.routine.weekDays') }}</div>
        <div class="text-body-2 text-medium-emphasis mb-4">{{ t('parent.routine.tapDayHint') }}</div>
        <div class="d-flex flex-wrap justify-center ga-4">
          <button
            v-for="day in routine.days"
            :key="day.index"
            type="button"
            class="day-button d-flex flex-column align-center"
            style="min-width: 70px"
            @click="toggleDay(day.index)"
          >
            <v-avatar
              :color="dayColor(day.status)"
              size="56"
              class="mb-2"
              :class="{ 'day-avatar--active': expandedDay === day.index }"
            >
              <v-icon :icon="dayIcon(day.status)" color="white" size="28" />
            </v-avatar>
            <span class="text-body-1 font-weight-medium">{{ day.label }}</span>
          </button>
        </div>

        <v-expand-transition>
          <div v-if="expandedDayData" class="mt-6 pa-4 rounded-lg day-detail">
            <div class="text-h6 font-weight-bold mb-3">{{ t('parent.routine.scheduleForDay', { day: expandedDayData.label }) }}</div>
            <div v-if="!expandedDayData.slots?.length" class="text-body-1 text-medium-emphasis text-center py-4">
              {{ t('parent.routine.noScheduleForDay') }}
            </div>
            <div v-else class="d-flex flex-column ga-3">
              <div
                v-for="(slot, idx) in expandedDayData.slots"
                :key="idx"
                class="d-flex align-center justify-space-between pa-4 rounded-lg today-slot"
                :class="`today-slot--${slot.status}`"
              >
                <div class="d-flex align-center ga-3">
                  <v-icon :icon="slotIcon(slot.status)" :color="slotIconColor(slot.status)" size="28" />
                  <div>
                    <div class="text-body-1 font-weight-bold">{{ slot.title }}</div>
                    <div v-if="slot.subject" class="text-body-2 text-medium-emphasis">{{ slot.subject }}</div>
                  </div>
                </div>
                <div class="text-body-1 font-weight-medium">{{ slot.start }} – {{ slot.end }}</div>
              </div>
            </div>
          </div>
        </v-expand-transition>

        <div class="d-flex flex-wrap justify-center ga-6 mt-6">
          <div class="d-flex align-center ga-2">
            <v-avatar color="success" size="20" />
            <span class="text-body-2">{{ t('parent.routine.commitmentFull') }}</span>
          </div>
          <div class="d-flex align-center ga-2">
            <v-avatar color="warning" size="20" />
            <span class="text-body-2">{{ t('parent.routine.commitmentPartial') }}</span>
          </div>
          <div class="d-flex align-center ga-2">
            <v-avatar color="error" size="20" />
            <span class="text-body-2">{{ t('parent.routine.commitmentMissed') }}</span>
          </div>
          <div class="d-flex align-center ga-2">
            <v-avatar color="grey" size="20" />
            <span class="text-body-2">{{ t('parent.routine.noData') }}</span>
          </div>
        </div>
      </v-card>

      <v-card v-if="routine.upcoming_exams?.length" class="pa-6 mb-6" rounded="xl" elevation="0" variant="flat">
        <div class="text-h6 font-weight-bold mb-4">{{ t('parent.routine.upcomingExams') }}</div>
        <v-row>
          <v-col v-for="exam in routine.upcoming_exams" :key="exam.subject" cols="12" sm="6" md="4">
            <v-card color="amber-lighten-4" rounded="lg" class="pa-4 text-center" elevation="0">
              <v-icon icon="mdi-pencil-box-outline" size="36" color="amber-darken-3" class="mb-2" />
              <div class="text-h6 font-weight-bold">{{ exam.subject }}</div>
              <div class="text-body-1 mt-1">
                {{ t('parent.routine.daysUntilExam', { n: exam.days_left }) }}
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-card>

      <v-card v-if="routine.weak_subjects?.length" class="pa-6 mb-6" rounded="xl" elevation="0" variant="flat">
        <div class="text-h6 font-weight-bold mb-4">{{ t('parent.routine.subjectsNeedAttention') }}</div>
        <v-row>
          <v-col v-for="subject in routine.weak_subjects" :key="subject" cols="12" sm="6" md="4">
            <v-card color="red-lighten-5" rounded="lg" class="pa-4 d-flex align-center ga-3" elevation="0">
              <v-icon icon="mdi-alert-circle-outline" size="32" color="error" />
              <div class="text-h6 font-weight-bold">{{ subject }}</div>
            </v-card>
          </v-col>
        </v-row>
      </v-card>
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  routine: {
    type: Object,
    default: () => ({}),
  },
})

const { t } = useI18n()

const expandedDay = ref(null)

function toggleDay(index) {
  expandedDay.value = expandedDay.value === index ? null : index
}

const expandedDayData = computed(() => {
  if (expandedDay.value === null) return null
  return (props.routine?.days || []).find((d) => d.index === expandedDay.value) || null
})

const commitmentColor = computed(() => {
  const percent = props.routine?.weekly_commitment_percent ?? 0
  if (percent >= 80) return 'success'
  if (percent >= 50) return 'warning'
  return 'error'
})

const commitmentMessage = computed(() => {
  const percent = props.routine?.weekly_commitment_percent ?? 0
  if (percent >= 80) return t('parent.routine.commitmentGreat')
  if (percent >= 50) return t('parent.routine.commitmentGood')
  return t('parent.routine.commitmentWeak')
})

function dayColor(status) {
  if (status === 'completed') return 'success'
  if (status === 'partial') return 'warning'
  if (status === 'missed') return 'error'
  return 'grey'
}

function dayIcon(status) {
  if (status === 'completed') return 'mdi-check'
  if (status === 'partial') return 'mdi-circle-half-full'
  if (status === 'missed') return 'mdi-close'
  return 'mdi-calendar-blank'
}

function slotIcon(status) {
  if (status === 'completed') return 'mdi-check-circle'
  if (status === 'missed') return 'mdi-close-circle'
  return 'mdi-clock-outline'
}

function slotIconColor(status) {
  if (status === 'completed') return 'success'
  if (status === 'missed') return 'error'
  return 'grey'
}
</script>

<style scoped>
.day-button {
  background: none;
  border: none;
  padding: 4px;
  border-radius: 12px;
  cursor: pointer;
  font-family: inherit;
  transition: background 0.15s ease;
}
.day-button:hover {
  background: rgba(255, 255, 255, 0.05);
}
.day-avatar--active {
  outline: 3px solid var(--em-cyan, #22d3ee);
  outline-offset: 2px;
}
.day-detail {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.today-slot {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.today-slot--completed {
  background: rgba(76, 175, 80, 0.06);
  border-color: rgba(76, 175, 80, 0.22);
}
.today-slot--missed {
  background: rgba(244, 67, 54, 0.04);
  border-color: rgba(244, 67, 54, 0.14);
}
</style>
