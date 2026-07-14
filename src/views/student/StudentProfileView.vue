<template>
  <div class="slide-up-enter-active student-identity">
    <PageHeader
      :eyebrow="t('student.profile.header.eyebrow')"
      :title="t('student.profile.header.title')"
      :subtitle="t('student.profile.header.subtitle')"
    />

    <section class="student-identity__section">
      <v-card class="student-identity__hero glass-card" variant="flat">
        <div class="d-flex flex-column flex-sm-row align-sm-center gap-4">
          <v-avatar size="88" class="student-identity__avatar eduspark-gradient flex-shrink-0">
            <span class="text-h4 text-white font-weight-bold">{{ initials }}</span>
          </v-avatar>
          <div class="flex-grow-1 min-width-0">
            <span class="student-identity__role mb-2">
              <v-icon size="14">mdi-school</v-icon>
              {{ t('student.common.roleStudent') }}
            </span>
            <h2 class="text-h5 font-weight-bold mb-1">{{ displayName }}</h2>
            <p v-if="joinDateLabel" class="text-caption text-medium-emphasis mb-2">
              {{ t('student.profile.hero.joinedSince', { date: joinDateLabel }) }}
            </p>
            <v-chip size="small" color="success" variant="tonal" prepend-icon="mdi-heart-pulse">
              {{ t('student.profile.hero.activeLearner') }}
            </v-chip>
          </div>
          <div v-if="statsLoaded" class="d-flex gap-2 flex-shrink-0">
            <div class="student-identity__stat">
              <strong>{{ enrolledCoursesCount }}</strong>
              <span>{{ t('student.profile.hero.enrolledCourses') }}</span>
            </div>
            <div class="student-identity__stat">
              <strong>{{ activeSubjectsCount }}</strong>
              <span>{{ t('student.profile.hero.activeSubjects') }}</span>
            </div>
          </div>
        </div>
      </v-card>
    </section>

    <section class="student-identity__section">
      <h3 class="student-identity__section-title">
        <span aria-hidden="true">🎯</span>
        {{ t('student.profile.sections.goal.title') }}
      </h3>
      <div class="student-identity__section-body">
        <p class="text-body-2 text-medium-emphasis mb-3 mb-md-4">
          {{ t('student.profile.sections.goal.subtitle') }}
        </p>
        <v-row dense>
          <v-col
            v-for="goal in futureGoalIdentityOptions"
            :key="goal.value"
            cols="12"
            sm="6"
          >
            <button
              type="button"
              class="student-identity__goal-card w-100 text-start"
              :class="{ 'student-identity__goal-card--active': prefs.future_goal === goal.value }"
              @click="prefs.future_goal = goal.value"
            >
              <div class="d-flex align-center gap-2">
                <v-icon :color="prefs.future_goal === goal.value ? 'secondary' : undefined" size="22">
                  {{ goal.icon }}
                </v-icon>
                <span class="text-body-2 font-weight-medium">{{ goal.title }}</span>
              </div>
            </button>
          </v-col>
        </v-row>
      </div>
    </section>

    <section class="student-identity__section">
      <h3 class="student-identity__section-title">
        <span aria-hidden="true">🧠</span>
        {{ t('student.profile.sections.learn.title') }}
      </h3>
      <div class="student-identity__section-body">
        <div class="student-identity__learn-group">
          <p class="student-identity__learn-label">{{ t('student.profile.sections.learn.explanationLength') }}</p>
          <div class="student-identity__chip-grid">
            <button
              v-for="opt in explanationIdentityOptions"
              :key="opt.value"
              type="button"
              class="student-identity__chip"
              :class="{ 'student-identity__chip--active': prefs.preferred_explanation_style === opt.value }"
              @click="prefs.preferred_explanation_style = opt.value"
            >
              <span>{{ opt.emoji }}</span>
              {{ opt.title }}
            </button>
          </div>
        </div>

        <div class="student-identity__learn-group">
          <p class="student-identity__learn-label">{{ t('student.profile.sections.learn.challengeLevel') }}</p>
          <div class="student-identity__chip-grid">
            <button
              v-for="opt in difficultyIdentityOptions"
              :key="opt.value"
              type="button"
              class="student-identity__chip"
              :class="{ 'student-identity__chip--active': prefs.difficulty === opt.value }"
              @click="prefs.difficulty = opt.value"
            >
              <v-icon size="16">{{ opt.icon }}</v-icon>
              {{ opt.title }}
            </button>
          </div>
        </div>

        <div class="student-identity__learn-group">
          <p class="student-identity__learn-label">{{ t('student.profile.sections.learn.understandingStyle') }}</p>
          <div class="student-identity__chip-grid">
            <button
              v-for="opt in learningStyleIdentityOptions"
              :key="opt.value"
              type="button"
              class="student-identity__chip"
              :class="{ 'student-identity__chip--active': prefs.learning_style === opt.value }"
              @click="prefs.learning_style = opt.value"
            >
              <span>{{ opt.emoji }}</span>
              {{ opt.title }}
            </button>
          </div>
        </div>

        <div class="student-identity__learn-group">
          <p class="student-identity__learn-label">{{ t('student.profile.sections.learn.teacherStyle') }}</p>
          <div class="student-identity__chip-grid">
            <button
              v-for="opt in personalityIdentityOptions"
              :key="opt.value"
              type="button"
              class="student-identity__chip"
              :class="{ 'student-identity__chip--active': prefs.personality_mode === opt.value }"
              @click="prefs.personality_mode = opt.value"
            >
              <span>{{ opt.emoji }}</span>
              {{ opt.title }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <section class="student-identity__section">
      <h3 class="student-identity__section-title">
        <span aria-hidden="true">✨</span>
        {{ t('student.profile.sections.adaptation.title') }}
      </h3>
      <div class="student-identity__section-body student-identity__adaptation">
        <p class="student-identity__adaptation-intro mb-2">
          {{ t('student.profile.sections.adaptation.subtitle') }}
        </p>
        <ul v-if="adaptationBullets.length" class="student-identity__adaptation-list mb-0">
          <li v-for="(bullet, idx) in adaptationBullets" :key="idx">{{ bullet }}</li>
        </ul>
        <p v-else class="text-body-2 text-medium-emphasis mb-0 text-center py-2">
          {{ t('student.profile.sections.adaptation.empty') }}
        </p>
      </div>
    </section>

    <section class="student-identity__section">
      <h3 class="student-identity__section-title">
        <span aria-hidden="true">❤️</span>
        {{ t('student.profile.sections.interests.title') }}
      </h3>
      <div class="student-identity__section-body">
        <p class="text-body-2 text-medium-emphasis mb-3">
          {{ t('student.profile.sections.interests.subtitle') }}
        </p>
        <div class="student-identity__chip-grid">
          <button
            v-for="opt in allInterestOptions"
            :key="opt.value"
            type="button"
            class="student-identity__chip"
            :class="{ 'student-identity__chip--active': isInterestSelected(opt) }"
            @click="toggleInterest(opt)"
          >
            <v-icon size="16">{{ opt.icon }}</v-icon>
            {{ opt.title }}
          </button>
        </div>
      </div>
    </section>

    <section class="student-identity__section">
      <h3 class="student-identity__section-title">
        <span aria-hidden="true">🎂</span>
        {{ t('student.profile.sections.age.title') }}
      </h3>
      <div class="student-identity__section-body">
        <p v-if="ageBandDisplay" class="student-identity__age-band mb-1">{{ ageBandDisplay }}</p>
        <p v-else class="student-identity__age-band mb-1 text-medium-emphasis">{{ t('student.profile.sections.age.placeholder') }}</p>
        <p class="text-caption text-medium-emphasis mb-3">
          {{ t('student.profile.sections.age.help') }}
        </p>
        <div class="student-identity__chip-grid">
          <button
            v-for="band in ageBandOptions"
            :key="band.label"
            type="button"
            class="student-identity__chip"
            :class="{ 'student-identity__chip--active': isAgeBandActive(band) }"
            @click="prefs.age = band.value"
          >
            {{ band.label }}
          </button>
        </div>
      </div>
    </section>

    <section class="student-identity__section student-identity__family">
      <h3 class="student-identity__section-title">
        <span aria-hidden="true">👨‍👩‍👧‍👦</span>
        {{ t('student.profile.sections.family.title') }}
      </h3>
      <StudentLinkedParentsSection />
      <StudentParentLinkCodeCard />
    </section>

    <v-alert
      v-if="saveSuccess"
      type="success"
      variant="tonal"
      class="mb-4 rounded-lg"
      closable
      @click:close="saveSuccess = false"
    >
      {{ t('student.profile.saveSuccess') }}
    </v-alert>

    <v-btn
      size="large"
      block
      rounded="lg"
      color="secondary"
      variant="flat"
      class="student-identity__save"
      :loading="saving"
      prepend-icon="mdi-check"
      @click="save"
    >
      {{ t('student.profile.saveCta') }}
    </v-btn>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import PageHeader from '../../components/common/PageHeader.vue'
import StudentLinkedParentsSection from '../../components/student/StudentLinkedParentsSection.vue'
import { useProfileAdaptationPreview } from '../../composables/useProfileAdaptationPreview.js'
import StudentParentLinkCodeCard from '../../components/parent/StudentParentLinkCodeCard.vue'
import { useAuth } from '../../composables/useAuth.js'
import { fetchAccountSecurity } from '../../api/auth.js'
import { getProfileApi, updateProfileApi } from '../../api/student.js'
import { fetchStudentDashboard } from '../../api/studentCourses.js'
import { getErrorMessage } from '../../api/client.js'
import { getStudentProfilePrefs, setStudentProfilePrefs, isApiMode } from '../../utils/session.js'
import {
  interestOptions,
  hobbyOptions,
  futureGoalIdentityOptions,
  explanationIdentityOptions,
  learningStyleIdentityOptions,
  personalityIdentityOptions,
  difficultyIdentityOptions,
  ageBandOptions,
  ageBandLabel,
  defaultProfilePrefs,
} from '../../data/profileOptions.js'
import { applyProfileData, buildProfilePayload } from '../../utils/profilePrefs.js'
import '../../assets/styles/student-identity-profile.css'

const { user } = useAuth()
const { t } = useI18n()

const prefs = reactive({
  interests: [...defaultProfilePrefs.interests],
  hobbies: [...defaultProfilePrefs.hobbies],
  difficulty: defaultProfilePrefs.difficulty,
  age: defaultProfilePrefs.age,
  learning_style: defaultProfilePrefs.learning_style,
  future_goal: defaultProfilePrefs.future_goal,
  preferred_explanation_style: defaultProfilePrefs.preferred_explanation_style,
  personality_mode: defaultProfilePrefs.personality_mode,
})

const saving = ref(false)
const saveSuccess = ref(false)
const joinDateLabel = ref('')
const enrolledCoursesCount = ref(0)
const activeSubjectsCount = ref(0)
const statsLoaded = ref(false)

const displayName = computed(() => user.value?.name || t('student.common.defaultStudentName'))
const initials = computed(() => {
  const n = displayName.value.trim()
  return n ? n.charAt(0) : t('student.profile.hero.defaultInitial')
})

const allInterestOptions = computed(() => [
  ...interestOptions.map((o) => ({ ...o, kind: 'academic' })),
  ...hobbyOptions.map((o) => ({ ...o, kind: 'hobby' })),
])

const ageBandDisplay = computed(() => ageBandLabel(prefs.age))
const adaptationBullets = useProfileAdaptationPreview(prefs)

function isInterestSelected(opt) {
  if (opt.kind === 'hobby') return prefs.hobbies.includes(opt.value)
  return prefs.interests.includes(opt.value)
}

function toggleInterest(opt) {
  const list = opt.kind === 'hobby' ? prefs.hobbies : prefs.interests
  const i = list.indexOf(opt.value)
  if (i >= 0) list.splice(i, 1)
  else list.push(opt.value)
}

function isAgeBandActive(band) {
  const age = Number(prefs.age)
  if (Number.isNaN(age)) return false
  return age >= band.min && age <= band.max
}

function formatJoinDate(iso) {
  if (!iso) return ''
  try {
    return new Intl.DateTimeFormat('ar', { month: 'long', year: 'numeric' }).format(new Date(iso))
  } catch {
    return ''
  }
}


async function loadHeroMeta() {
  if (isApiMode()) {
    try {
      const account = await fetchAccountSecurity()
      joinDateLabel.value = formatJoinDate(account?.created_at)
    } catch {
      joinDateLabel.value = ''
    }
    try {
      const dashboard = await fetchStudentDashboard()
      const courses = dashboard?.courses || []
      enrolledCoursesCount.value = courses.length
      const subjects = new Set(courses.map((c) => c.subjectName || c.subject).filter(Boolean))
      activeSubjectsCount.value = subjects.size
      statsLoaded.value = true
    } catch {
      statsLoaded.value = false
    }
  } else {
    joinDateLabel.value = formatJoinDate(user.value?.loggedInAt)
    statsLoaded.value = false
  }
}

onMounted(async () => {
  loadHeroMeta()
  if (isApiMode()) {
    try {
      applyProfileData(prefs, await getProfileApi())
      return
    } catch {
      /* fallback */
    }
  }
  const saved = getStudentProfilePrefs()
  if (saved) applyProfileData(prefs, saved)
})

async function save() {
  saving.value = true
  try {
    const payload = buildProfilePayload(prefs)
    if (isApiMode()) {
      await updateProfileApi(payload)
    }
    setStudentProfilePrefs(payload)
    saveSuccess.value = true
  } catch (err) {
    saveSuccess.value = false
    alert(getErrorMessage(err, t('student.profile.errors.save')))
  } finally {
    saving.value = false
  }
}
</script>
