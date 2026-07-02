<template>

  <AppSection

    class="teacher-home__section teacher-home__section--classes"

    :eyebrow="$t('teacher.grades.title')"

    :title="$t('teacher.dashboard.teachingSpaces')"

    :subtitle="$t('teacher.dashboard.classesDesc')"

    spacing="sm"

    :divider="false"

  >

    <template v-if="courses.length" #actions>

      <v-btn variant="text" size="small" :to="gradesRoute" class="text-none">

        {{ $t('teacher.actions.viewAll') }}

        <v-icon end size="16">mdi-chevron-left</v-icon>

      </v-btn>

    </template>



    <div v-if="courses.length" class="teacher-classes">

      <router-link

        v-for="course in previewCourses"

        :key="course.course_id"

        :to="`/teacher/grades/${course.course_id}`"

        class="teacher-class-card em-hover-lift"

      >

        <div class="teacher-class-card__head">

          <span class="teacher-class-card__subject">{{ course.subject_name }}</span>

          <span class="teacher-class-card__grade">{{ $t('teacher.labels.gradeNumber', { grade: course.grade }) }}</span>

        </div>



        <ul class="teacher-class-card__stats">

          <li>

            <v-icon size="14">mdi-account-group-outline</v-icon>

            {{ $t('teacher.labels.studentCount', { count: course.subscribed_students }) }}

          </li>

          <li>

            <v-icon size="14">mdi-book-open-variant</v-icon>

            {{ $t('teacher.labels.lessonCount', { count: course.lesson_count }) }}

          </li>

          <li>

            <v-icon size="14">mdi-clipboard-text-outline</v-icon>

            {{ $t('teacher.labels.quizCount', { count: course.quiz_count ?? 0 }) }}

          </li>

        </ul>



        <p class="teacher-class-card__latest mb-0">

          {{ latestFor(course) }}

        </p>



        <span class="teacher-class-card__cta">

          {{ $t('teacher.actions.followUp') }}

          <v-icon size="14">mdi-arrow-left</v-icon>

        </span>

      </router-link>

    </div>



    <v-card v-else class="glass-card teacher-class-card__empty pa-5 text-center" variant="flat">

      <v-icon size="36" color="secondary" class="mb-2">mdi-school-outline</v-icon>

      <p class="text-body-2 font-weight-medium mb-1">{{ $t('teacher.dashboard.noClassCreated') }}</p>

      <p class="text-caption text-medium-emphasis mb-3">

        {{ $t('teacher.dashboard.createFirstCourse') }}

      </p>

      <v-btn class="btn-glow" size="small" rounded="lg" :to="gradesRoute" prepend-icon="mdi-plus">

        {{ $t('teacher.actions.createClass') }}

      </v-btn>

    </v-card>

  </AppSection>

</template>



<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()


import { AppSection } from '../../ui/index.js'

import { ROUTES } from '../../../constants/app.js'

import { workspaceLatestActivity } from '../../../utils/teacherDashboardUi.js'



const props = defineProps({

  courses: { type: Array, default: () => [] },

  limit: { type: Number, default: 4 },

})



const gradesRoute = ROUTES.TEACHER_GRADES



const previewCourses = computed(() => props.courses.slice(0, props.limit))



function latestFor(course) {

  return workspaceLatestActivity(course)

}

</script>


