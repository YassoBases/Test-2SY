<template>
  <ul class="welcome-benefits welcome-enter welcome-enter--benefits" :aria-label="t('auth.welcome.benefitsAria')">
    <li
      v-for="(benefit, i) in benefits"
      :key="benefit"
      class="welcome-benefits__chip"
      :style="{ animationDelay: `${760 + i * 70}ms` }"
    >
      <v-icon size="14" class="welcome-benefits__icon">mdi-check-circle</v-icon>
      <span>{{ benefit }}</span>
    </li>
  </ul>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, tm } = useI18n()

const benefits = computed(() => tm('auth.welcome.benefits'))
</script>
