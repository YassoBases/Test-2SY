<template>

  <div class="onboarding-page onboarding-personalize student-identity">

    <OnboardingStepper current="personalize" />



    <div v-if="showComplete" class="personalize-complete">

      <span class="personalize-complete__emoji" aria-hidden="true">🎉</span>

      <h1 class="personalize-complete__title">{{ t('auth.onboarding.personalize.completeTitle') }}</h1>

      <p class="personalize-complete__desc personalize-complete__desc--pre-line">

        {{ t('auth.onboarding.personalize.completeDesc') }}

      </p>

      <v-btn

        class="btn-glow personalize-complete__cta"

        size="large"

        rounded="lg"

        color="secondary"

        variant="flat"

        @click="goToSubjects"

      >

        {{ t('auth.onboarding.personalize.completeCta') }}

      </v-btn>

    </div>



    <div v-else-if="showIntro" class="personalize-intro">

      <h1 class="text-h5 font-weight-bold mb-3">{{ t('auth.onboarding.personalize.introTitle') }}</h1>

      <p class="personalize-intro__body text-body-2 text-medium-emphasis mb-2">

        {{ t('auth.onboarding.personalize.introBody') }}

      </p>

      <p class="personalize-intro__hint text-caption text-medium-emphasis mb-6">

        {{ t('auth.onboarding.personalize.introHint') }}

      </p>

      <button type="button" class="personalize-skip" @click="skipAll">

        {{ t('auth.onboarding.skip') }}

      </button>

      <OnboardingNavFooter :back-to="ROUTES.ONBOARDING_GRADE">

        <v-btn class="btn-glow" size="large" rounded="lg" @click="startPersonalize">

          {{ t('auth.onboarding.personalize.start') }}

        </v-btn>

      </OnboardingNavFooter>

    </div>



    <template v-else>

      <PersonalizeProgress :step="stepIndex + 1" :total="stepTotal" />



      <Transition name="personalize-step" mode="out-in">

        <div :key="stepIndex">

          <h1 class="text-h5 font-weight-bold mb-2">{{ currentStep.title }}</h1>

          <p class="personalize-why text-body-2 text-medium-emphasis mb-5">{{ currentStep.why }}</p>



          <div class="student-identity__section-body mb-2">

            <!-- Step 1: Goal -->

            <template v-if="currentStep.key === 'goal'">

              <v-row dense>

                <v-col

                  v-for="goal in localizedGoalOptions"

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

                      <v-icon

                        :color="prefs.future_goal === goal.value ? 'secondary' : undefined"

                        size="22"

                      >

                        {{ goal.icon }}

                      </v-icon>

                      <span class="text-body-2 font-weight-medium">{{ goal.title }}</span>

                    </div>

                  </button>

                </v-col>

              </v-row>

            </template>



            <!-- Step 2: Learning style -->

            <template v-else-if="currentStep.key === 'learning'">

              <div class="student-identity__learn-group">

                <p class="student-identity__learn-label">{{ t('auth.onboarding.personalize.labels.pickWhatFits') }}</p>

                <div class="student-identity__chip-grid">

                  <button

                    v-for="opt in localizedLearningStyleOptions"

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

                <p class="student-identity__learn-label">{{ t('auth.onboarding.personalize.labels.challengeLevel') }}</p>

                <div class="student-identity__chip-grid">

                  <button

                    v-for="opt in localizedDifficultyOptions"

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

            </template>



            <!-- Step 3: Teacher style -->

            <template v-else-if="currentStep.key === 'ai'">

              <div class="student-identity__learn-group">

                <p class="student-identity__learn-label">{{ t('auth.onboarding.personalize.labels.explanationDepth') }}</p>

                <div class="student-identity__chip-grid">

                  <button

                    v-for="opt in localizedExplanationOptions"

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

                <p class="student-identity__learn-label">{{ t('auth.onboarding.personalize.labels.teacherPersonality') }}</p>

                <div class="student-identity__chip-grid">

                  <button

                    v-for="opt in localizedPersonalityOptions"

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

            </template>



            <!-- Step 4: Interests -->

            <template v-else-if="currentStep.key === 'interests'">

              <div class="student-identity__chip-grid">

                <button

                  v-for="opt in allInterestOptions"

                  :key="`${opt.kind}-${opt.value}`"

                  type="button"

                  class="student-identity__chip"

                  :class="{ 'student-identity__chip--active': isInterestSelected(opt) }"

                  @click="toggleInterest(opt)"

                >

                  <v-icon size="16">{{ opt.icon }}</v-icon>

                  {{ opt.title }}

                </button>

              </div>

            </template>



            <!-- Step 5: Age -->

            <template v-else-if="currentStep.key === 'age'">

              <div class="student-identity__chip-grid">

                <button

                  v-for="band in localizedAgeBandOptions"

                  :key="band.label"

                  type="button"

                  class="student-identity__chip"

                  :class="{ 'student-identity__chip--active': isAgeBandActive(band) }"

                  @click="prefs.age = band.value"

                >

                  {{ band.label }}

                </button>

              </div>

            </template>

          </div>



          <div v-if="stepPreview" class="personalize-preview text-start mt-4">

            <p class="personalize-preview__text">{{ stepPreview }}</p>

          </div>

        </div>

      </Transition>



      <v-alert v-if="error" type="error" variant="tonal" class="mt-4 text-start">{{ error }}</v-alert>



      <button type="button" class="personalize-skip" :disabled="saving" @click="skipAll">

        {{ t('auth.onboarding.skip') }}

      </button>



      <OnboardingNavFooter :show-back="stepIndex === 0" :back-to="ROUTES.ONBOARDING_GRADE">

        <div v-if="stepIndex > 0" class="personalize-nav-actions">

          <v-btn variant="text" size="small" class="onboarding-back-btn" prepend-icon="mdi-arrow-right" @click="prevStep">

            {{ t('auth.onboarding.back') }}

          </v-btn>

          <v-btn

            class="btn-glow"

            size="large"

            rounded="lg"

            :loading="saving"

            @click="onPrimaryAction"

          >

            {{ primaryLabel }}

          </v-btn>

        </div>

        <v-btn

          v-else

          class="btn-glow"

          size="large"

          rounded="lg"

          :loading="saving"

          @click="onPrimaryAction"

        >

          {{ primaryLabel }}

        </v-btn>

      </OnboardingNavFooter>

    </template>

  </div>

</template>



<script setup>

import { computed, onMounted, reactive, ref } from 'vue'

import { useRouter } from 'vue-router'

import { useI18n } from 'vue-i18n'

import { useLocalizedLabels } from '../../composables/useLocalizedLabels.js'

import OnboardingNavFooter from '../../components/onboarding/OnboardingNavFooter.vue'

import OnboardingStepper from '../../components/onboarding/OnboardingStepper.vue'

import PersonalizeProgress from '../../components/onboarding/personalization/PersonalizeProgress.vue'

import { getProfileApi, updateProfileApi } from '../../api/student.js'

import { getErrorMessage } from '../../api/client.js'

import { ROUTES } from '../../constants/app.js'

import {

  interestOptions,

  hobbyOptions,

  futureGoalIdentityOptions,

  explanationIdentityOptions,

  learningStyleIdentityOptions,

  personalityIdentityOptions,

  difficultyIdentityOptions,

  ageBandOptions,

  labelForOption,

} from '../../data/profileOptions.js'

import {

  applyProfileData,

  buildProfilePayload,

  createDefaultProfilePrefs,

} from '../../utils/profilePrefs.js'

import {

  isPersonalizationSetupComplete,

  markPersonalizationSetupComplete,

} from '../../utils/personalizationSetup.js'

import { getSession, setStudentProfilePrefs, isApiMode } from '../../utils/session.js'

import '../../assets/styles/student-identity-profile.css'

import '../../assets/styles/onboarding-personalize.css'



const { t } = useI18n()

const { localizeOptionTitle, personalizePreview } = useLocalizedLabels()

const router = useRouter()



const STEP_KEYS = ['goal', 'learning', 'ai', 'interests', 'age']

const STEPS = computed(() =>
  STEP_KEYS.map((key) => ({
    key,
    title: t(`auth.onboarding.personalize.steps.${key}.title`),
    why: t(`auth.onboarding.personalize.steps.${key}.why`),
  })),
)



const showIntro = ref(true)

const stepIndex = ref(0)

const stepTotal = STEP_KEYS.length

const showComplete = ref(false)

const saving = ref(false)

const error = ref('')



const prefs = reactive(createDefaultProfilePrefs())



const currentStep = computed(() => STEPS.value[stepIndex.value])

const isLastStep = computed(() => stepIndex.value >= stepTotal - 1)

const primaryLabel = computed(() =>
  isLastStep.value ? t('auth.onboarding.personalize.finish') : t('auth.onboarding.personalize.next'),
)



function startPersonalize() {

  showIntro.value = false

}



function prevStep() {

  if (stepIndex.value > 0) stepIndex.value -= 1

}



const allInterestOptions = computed(() => [

  ...interestOptions.map((o) => ({
    ...o,
    kind: 'academic',
    title: localizeOptionTitle('interests', o.value, o.title),
  })),

  ...hobbyOptions.map((o) => ({
    ...o,
    kind: 'hobby',
    title: localizeOptionTitle('hobbies', o.value, o.title),
  })),

])



const localizedGoalOptions = computed(() =>
  futureGoalIdentityOptions.map((o) => ({
    ...o,
    title: localizeOptionTitle('goal', o.value, o.title),
  })),
)

const localizedLearningStyleOptions = computed(() =>
  learningStyleIdentityOptions.map((o) => ({
    ...o,
    title: localizeOptionTitle('learningStyle', o.value, o.title),
  })),
)

const localizedDifficultyOptions = computed(() =>
  difficultyIdentityOptions.map((o) => ({
    ...o,
    title: localizeOptionTitle('difficulty', o.value, o.title),
  })),
)

const localizedExplanationOptions = computed(() =>
  explanationIdentityOptions.map((o) => ({
    ...o,
    title: localizeOptionTitle('explanation', o.value, o.title),
  })),
)

const localizedPersonalityOptions = computed(() =>
  personalityIdentityOptions.map((o) => ({
    ...o,
    title: localizeOptionTitle('personality', o.value, o.title),
  })),
)

const localizedAgeBandOptions = computed(() =>
  ageBandOptions.map((band) => ({
    ...band,
    label: localizeOptionTitle('ageBands', String(band.value), band.label),
  })),
)



const stepPreview = computed(() => {

  const key = currentStep.value.key



  if (key === 'goal') {

    return personalizePreview('goal', prefs.future_goal)

  }



  if (key === 'learning') {

    return (

      personalizePreview('learningStyle', prefs.learning_style)

      || personalizePreview('difficulty', prefs.difficulty)

      || null

    )

  }



  if (key === 'ai') {

    return (

      personalizePreview('explanation', prefs.preferred_explanation_style)

      || personalizePreview('personality', prefs.personality_mode)

      || null

    )

  }



  if (key === 'interests') {

    const topics = [...(prefs.interests || []), ...(prefs.hobbies || [])]

      .map((value) => {

        if (prefs.interests.includes(value)) {
          return localizeOptionTitle('interests', value, labelForOption(interestOptions, value))
        }
        return localizeOptionTitle('hobbies', value, labelForOption(hobbyOptions, value))
      })

      .filter(Boolean)

      .slice(0, 2)

    if (!topics.length) return null

    if (topics.length === 1) {
      return t('auth.onboarding.personalize.previews.interestsDefault', { topic: topics[0] })
    }

    return t('auth.onboarding.personalize.previews.interestsTwo', {
      first: topics[0],
      second: topics[1],
    })

  }



  if (key === 'age' && prefs.age != null) {

    return personalizePreview('ageBands', String(prefs.age))

  }



  return null

})



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



onMounted(async () => {

  const grade = getSession()?.grade

  if (!grade) {

    await router.replace(ROUTES.ONBOARDING_GRADE)

    return

  }

  if (isPersonalizationSetupComplete()) {

    await router.replace(ROUTES.ONBOARDING_SUBJECTS)

    return

  }

  if (isApiMode()) {

    try {

      applyProfileData(prefs, await getProfileApi())

    } catch {

      /* defaults */

    }

  }

})



function goToSubjects() {

  router.push(ROUTES.ONBOARDING_SUBJECTS)

}



async function saveProfile() {

  const payload = buildProfilePayload(prefs)

  if (isApiMode()) {

    await updateProfileApi(payload)

  }

  setStudentProfilePrefs(payload)

}



async function finishSetup() {

  saving.value = true

  error.value = ''

  try {

    await saveProfile()

    markPersonalizationSetupComplete()

    showComplete.value = true

  } catch (e) {

    error.value = getErrorMessage(e, t('auth.onboarding.errors.saveAnswers'))

  } finally {

    saving.value = false

  }

}



function skipAll() {

  markPersonalizationSetupComplete()

  router.push(ROUTES.ONBOARDING_SUBJECTS)

}



async function onPrimaryAction() {

  if (!isLastStep.value) {

    stepIndex.value += 1

    return

  }

  await finishSetup()

}

</script>



<style scoped>

.onboarding-personalize :deep(.onboarding-nav-footer) {

  margin-top: 1.25rem;

}



.personalize-nav-actions {

  display: flex;

  align-items: center;

  justify-content: center;

  gap: 0.5rem;

  width: 100%;

  flex-wrap: wrap;

}



.personalize-nav-actions .onboarding-back-btn {

  text-transform: none;

  letter-spacing: 0;

  font-size: 0.85rem;

  min-width: auto;

}

.personalize-complete__desc--pre-line {
  white-space: pre-line;
}

</style>


