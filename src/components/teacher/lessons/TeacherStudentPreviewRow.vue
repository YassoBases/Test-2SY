<template>

  <router-link :to="profileTo" class="student-preview-row">

    <span class="student-preview-row__avatar" aria-hidden="true">{{ initials }}</span>

    <span class="student-preview-row__main">

      <span class="student-preview-row__name">{{ student.full_name }}</span>

      <span class="student-preview-row__activity">

        {{ activityLabel }}

      </span>

    </span>

    <span

      class="student-preview-row__status"

      :class="`student-preview-row__status--${student.subscription_status}`"

    >

      {{ subscriptionStatusLabel(student.subscription_status) }}

    </span>

  </router-link>

</template>



<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

import { computed } from 'vue'

import { subscriptionStatusLabel } from '../../../utils/subscriptionStatus.js'

import { formatLessonRelativeDate } from '../../../utils/lessonWorkspaceDisplay.js'



const props = defineProps({

  student: { type: Object, required: true },

})



const profileTo = computed(() => ({

  name: 'teacher-student-profile',

  params: { studentId: props.student.student_id },

}))



const activityLabel = computed(() => {

  const relative = formatLessonRelativeDate(props.student.last_activity_at)

  return relative ? t('teacher.studentPreview.lastActivityRelative', { relative }) : t('teacher.studentPreview.noActivity')

})



const initials = computed(() => {

  const n = String(props.student.full_name || '').trim()

  if (!n) return t('teacher.labels.studentInitial')

  const parts = n.split(/\s+/).filter(Boolean)

  if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`

  return n.slice(0, 2)

})

</script>

