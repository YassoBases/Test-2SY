<template>
  <section class="welcome-trust welcome-enter welcome-enter--trust" :aria-label="t('auth.welcome.trustAria')">
    <ul class="welcome-trust__points">
      <li v-for="point in trustPoints" :key="point.text" class="welcome-trust__point">
        <span class="welcome-trust__point-icon" aria-hidden="true">
          <v-icon size="16" :color="point.color">{{ point.icon }}</v-icon>
        </span>
        <span class="welcome-trust__point-text">{{ point.text }}</span>
      </li>
    </ul>
    <WelcomeInstagramCard variant="card" />
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import WelcomeInstagramCard from './WelcomeInstagramCard.vue'

const { t, tm } = useI18n()

const trustPoints = computed(() => tm('auth.welcome.trustPoints'))
</script>
