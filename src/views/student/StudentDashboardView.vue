<template>
  <div class="student-home slide-up-enter-active">
    <v-alert v-if="loadError" type="error" variant="tonal" class="mb-5 rounded-lg">{{ loadError }}</v-alert>

    <LoadingState v-if="loading" variant="cards" :count="3" class="mb-6" />

    <template v-else>
      <div class="student-home__section student-home__section--hero">
        <JourneyHero
          :name="displayName"
          :mission="nextMission"
        />
      </div>

      <div class="student-home__section student-home__section--courses">
        <MySubjectsSection
          :courses="courses"
          :grade="dashboard.grade"
        />
      </div>

      <div class="student-home__section student-home__section--continue">
        <ContinueLearningSection :items="continueItems" />
      </div>

      <div class="student-home__section student-home__section--achievements">
        <HomeAchievementsSection :recent="recentBadge" :next="nextBadge" />
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, onActivated, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LoadingState from '../../components/common/LoadingState.vue'
import JourneyHero from '../../components/student/home/JourneyHero.vue'
import MySubjectsSection from '../../components/student/home/MySubjectsSection.vue'
import ContinueLearningSection from '../../components/student/home/ContinueLearningSection.vue'
import HomeAchievementsSection from '../../components/student/home/HomeAchievementsSection.vue'
import { useStudentHome } from '../../composables/useStudentHome.js'
import { useAuth } from '../../composables/useAuth.js'
import { isApiMode } from '../../utils/session.js'
import { LESSON_COMPLETED_EVENT } from '../../utils/lessonCompletionEvents.js'
import '../../assets/styles/student-home.css'

const { t } = useI18n()
const { user } = useAuth()
const route = useRoute()

const {
  loading,
  loadError,
  dashboard,
  courses,
  continueItems,
  recentBadge,
  nextBadge,
  nextMission,
  load,
} = useStudentHome()

const displayName = computed(() => user.value?.name || t('student.common.defaultStudentName'))

function scrollToNavHash() {
  let id = route.hash?.replace(/^#/, '')
  if (!id) return
  if (id === 'courses' || id === 'journey') id = 'my-subjects'
  nextTick(() => {
    requestAnimationFrame(() => {
      document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  })
}

watch(() => route.hash, scrollToNavHash)

function onLessonCompleted() {
  load().then(scrollToNavHash)
}

onMounted(() => {
  if (!isApiMode()) {
    scrollToNavHash()
    return
  }
  load().then(scrollToNavHash)
  window.addEventListener(LESSON_COMPLETED_EVENT, onLessonCompleted)
})

onActivated(() => {
  if (isApiMode()) load().then(scrollToNavHash)
})

onUnmounted(() => {
  window.removeEventListener(LESSON_COMPLETED_EVENT, onLessonCompleted)
})
</script>
