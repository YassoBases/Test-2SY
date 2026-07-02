<template>
  <v-card class="glass-card pa-6 mb-6" variant="flat" max-width="700" style="margin:auto">
    <div v-if="step === 1">
      <h2 class="text-h5 font-weight-bold mb-1">{{ t('common.routine.onboarding.welcomeTitle') }}</h2>
      <p class="text-body-2 text-medium-emphasis mb-6">{{ t('common.routine.onboarding.welcomeSubtitle') }}</p>

      <p class="text-subtitle-2 mb-2">{{ t('common.routine.onboarding.gradeQuestion') }}</p>
      <div class="d-flex flex-wrap gap-2 mb-5">
        <v-chip v-for="g in grades" :key="g.value"
          :color="form.grade === g.value ? 'primary' : 'default'"
          :variant="form.grade === g.value ? 'elevated' : 'tonal'"
          size="large" class="cursor-pointer" @click="form.grade = g.value">
          {{ g.label }}
        </v-chip>
      </div>

      <p class="text-subtitle-2 mb-2">{{ t('common.routine.onboarding.schoolTimeQuestion') }}</p>
      <div class="d-flex gap-3 mb-5">
        <v-text-field v-model="form.schoolStart" :label="t('common.from')" type="time" density="compact" variant="outlined" style="max-width:130px" />
        <v-text-field v-model="form.schoolEnd" :label="t('common.to')" type="time" density="compact" variant="outlined" style="max-width:130px" />
      </div>

      <p class="text-subtitle-2 mb-2">{{ t('common.routine.onboarding.wakeSleepQuestion') }}</p>
      <div class="d-flex gap-3 mb-5">
        <v-text-field v-model="form.wakeTime" :label="t('common.routine.onboarding.wakeTime')" type="time" density="compact" variant="outlined" style="max-width:130px" />
        <v-text-field v-model="form.sleepTime" :label="t('common.routine.onboarding.sleepTime')" type="time" density="compact" variant="outlined" style="max-width:130px" />
      </div>

      <p class="text-subtitle-2 mb-2">{{ t('common.routine.onboarding.activitiesQuestion') }}</p>
      <div class="d-flex flex-wrap gap-2 mb-6">
        <v-chip v-for="a in activityOptions" :key="a.value"
          :color="form.activities.includes(a.value) ? 'secondary' : 'default'"
          :variant="form.activities.includes(a.value) ? 'elevated' : 'tonal'"
          class="cursor-pointer" @click="toggleActivity(a.value)">
          {{ a.label }}
        </v-chip>
      </div>

      <v-btn block color="primary" size="large" :disabled="!form.grade" @click="step = 2">
        {{ t('common.routine.onboarding.nextDetailDays') }}
        <v-icon end>mdi-arrow-left</v-icon>
      </v-btn>
    </div>

    <div v-if="step === 2">
      <h2 class="text-h5 font-weight-bold mb-1">{{ t('common.routine.onboarding.detailTitle') }}</h2>
      <p class="text-body-2 text-medium-emphasis mb-4">{{ t('common.routine.onboarding.detailSubtitle') }}</p>

      <div v-for="day in weekDays" :key="day.key" class="mb-4">
        <p class="text-subtitle-2 mb-2 text-primary">{{ day.label }}</p>
        <div class="d-flex flex-wrap gap-2">
          <v-chip v-for="opt in dayOptions" :key="opt.value" size="small"
            :color="isDaySelected(day.key, opt.value) ? opt.color : 'default'"
            :variant="isDaySelected(day.key, opt.value) ? 'elevated' : 'tonal'"
            class="cursor-pointer" @click="toggleDayActivity(day.key, opt.value)">
            {{ opt.label }}
          </v-chip>
          <v-text-field v-if="isDaySelected(day.key, 'school')"
            v-model="dayTimes[day.key]" :placeholder="t('common.routine.onboarding.schoolHoursPlaceholder')"
            density="compact" variant="outlined" style="max-width:120px; font-size:0.8rem" />
        </div>
      </div>

      <div class="d-flex gap-3 mt-6">
        <v-btn variant="tonal" @click="step = 1">{{ t('common.back') }}</v-btn>
        <v-btn block color="primary" size="large" :loading="saving" @click="submit">
          {{ t('common.routine.onboarding.buildProgram') }}
        </v-btn>
      </div>
    </div>
  </v-card>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { saveOnboarding, chatWithRoutine, confirmSchedule } from '../../api/routine.js'

const emit = defineEmits(['done'])

const { t } = useI18n()

const step = ref(1)
const saving = ref(false)

const form = reactive({
  grade: '',
  schoolStart: '07:30',
  schoolEnd: '13:00',
  wakeTime: '06:30',
  sleepTime: '22:00',
  activities: [],
})

const dayActivities = reactive({})
const dayTimes = reactive({})

const gradeKeys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'bac']

const grades = computed(() =>
  gradeKeys.map((value) => ({ value, label: t(`common.routine.grades.${value}`) })),
)

const activityOptions = computed(() => [
  { value: 'sport', label: t('common.routine.activityTypes.sport') },
  { value: 'private_lesson', label: t('common.routine.activityTypes.private_lesson') },
  { value: 'religious', label: t('common.routine.activityTypes.religious') },
  { value: 'family', label: t('common.routine.activityTypes.family') },
])

const weekDays = computed(() => [
  { key: 0, label: t('common.days.monday') },
  { key: 1, label: t('common.days.tuesday') },
  { key: 2, label: t('common.days.wednesday') },
  { key: 3, label: t('common.days.thursday') },
  { key: 4, label: t('common.days.friday') },
  { key: 5, label: t('common.days.saturday') },
  { key: 6, label: t('common.days.sunday') },
])

const dayOptions = computed(() => [
  { value: 'school', label: t('common.routine.activityTypes.school'), color: 'primary' },
  { value: 'sport', label: t('common.routine.activityTypes.sport'), color: 'success' },
  { value: 'private_lesson', label: t('common.routine.activityTypes.private_lesson'), color: 'secondary' },
  { value: 'religious', label: t('common.routine.activityTypes.religious'), color: 'warning' },
  { value: 'free', label: t('common.routine.activityTypes.free'), color: 'info' },
])

function toggleActivity(val) {
  const idx = form.activities.indexOf(val)
  if (idx >= 0) form.activities.splice(idx, 1)
  else form.activities.push(val)
}

function isDaySelected(dayKey, actVal) {
  return (dayActivities[dayKey] || []).includes(actVal)
}

function toggleDayActivity(dayKey, actVal) {
  if (!dayActivities[dayKey]) dayActivities[dayKey] = []
  const idx = dayActivities[dayKey].indexOf(actVal)
  if (idx >= 0) dayActivities[dayKey].splice(idx, 1)
  else dayActivities[dayKey].push(actVal)
}

async function submit() {
  saving.value = true
  try {
    await saveOnboarding({
      grade_level: form.grade,
      school_start: form.schoolStart,
      school_end: form.schoolEnd,
      wake_time: form.wakeTime,
      sleep_time: form.sleepTime,
      school_days: weekDays.value.filter((d) => isDaySelected(d.key, 'school')).map((d) => d.key),
      activities: dayActivities,
    })

    const summary = buildSummary()
    const { data } = await chatWithRoutine(summary)

    if (data.schedule && data.ready_to_confirm) {
      await confirmSchedule(data.schedule)
    }

    emit('done')
  } catch (e) {
    console.error(e)
  } finally {
    saving.value = false
  }
}

function buildSummary() {
  const days = weekDays.value.map((d) => {
    const acts = (dayActivities[d.key] || []).join(', ')
    const time = dayTimes[d.key] || ''
    return `${d.label}: ${acts || t('common.routine.onboarding.none')} ${time}`
  }).join('\n')
  return t('common.routine.onboarding.promptTemplate', {
    grade: form.grade,
    wake: form.wakeTime,
    sleep: form.sleepTime,
    schoolStart: form.schoolStart,
    schoolEnd: form.schoolEnd,
    days,
  })
}
</script>

<style scoped>
.cursor-pointer { cursor: pointer; }
</style>
