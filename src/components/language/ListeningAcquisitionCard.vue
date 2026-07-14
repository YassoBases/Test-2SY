<template>
  <v-card class="acquisition-card pa-8 pa-md-10 text-center" variant="flat">
    <div class="acquisition-icon mb-4">{{ icon }}</div>
    <h3 class="text-h5 font-weight-bold mb-2">{{ title }}</h3>
    <p class="text-body-1 text-medium-emphasis mb-6 mx-auto acquisition-body">{{ body }}</p>
    <LearningLoader v-if="showSpinner" :title="title" icon="mdi-headphones" class="mb-4" />
    <div v-if="countdown > 0" class="text-body-2 text-medium-emphasis mb-4">
      {{ t('student.languages.listeningJourney.acquisition.retryIn', { seconds: countdown }) }}
    </div>
    <v-btn
      v-if="showRetry"
      color="secondary"
      variant="flat"
      size="large"
      :disabled="countdown > 0"
      prepend-icon="mdi-refresh"
      @click="$emit('retry')"
    >
      {{ t('student.languages.listeningJourney.acquisition.tryAgain') }}
    </v-btn>
  </v-card>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import LearningLoader from './LearningLoader.vue'

const props = defineProps({
  acquisition: { type: Object, default: null },
  phase: { type: String, default: 'pending' },
})

defineEmits(['retry'])

const { t, te } = useI18n()

const countdown = ref(0)
let countdownTimer = null

const messageKey = computed(() => {
  const key = props.acquisition?.message_key
  if (key && te(`${key}.title`)) return key
  const status = props.acquisition?.status
  const map = {
    generating: 'student.languages.listeningJourney.acquisition.preparing',
    waiting: 'student.languages.listeningJourney.acquisition.almostReady',
    retrying: 'student.languages.listeningJourney.acquisition.stillGenerating',
    temporary_failure: 'student.languages.listeningJourney.acquisition.unavailable',
    no_content: 'student.languages.listeningJourney.acquisition.noContent',
  }
  return map[status] || 'student.languages.listeningJourney.acquisition.preparing'
})

const title = computed(() => t(`${messageKey.value}.title`))
const body = computed(() => t(`${messageKey.value}.body`))

const icon = computed(() => {
  if (props.phase === 'unavailable') return '⏳'
  if (props.acquisition?.status === 'waiting') return '✨'
  return '🎧'
})

const showSpinner = computed(() => props.phase === 'pending' || props.phase === 'loading')
const showRetry = computed(() => props.phase === 'unavailable')

function startCountdown(seconds) {
  if (countdownTimer) clearInterval(countdownTimer)
  countdown.value = Math.max(0, Math.ceil(seconds || 0))
  if (countdown.value <= 0) return
  countdownTimer = setInterval(() => {
    countdown.value = Math.max(0, countdown.value - 1)
    if (countdown.value <= 0 && countdownTimer) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }, 1000)
}

watch(
  () => props.acquisition?.retry_after,
  (v) => startCountdown(v),
  { immediate: true },
)

onMounted(() => startCountdown(props.acquisition?.retry_after))
onBeforeUnmount(() => {
  if (countdownTimer) clearInterval(countdownTimer)
})
</script>

<style scoped>
.acquisition-card {
  border-radius: 24px;
}
.acquisition-icon {
  font-size: 3rem;
  line-height: 1;
}
.acquisition-body {
  max-width: 32rem;
}
</style>
