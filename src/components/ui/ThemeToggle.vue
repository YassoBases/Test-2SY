<template>
  <v-tooltip :text="tooltip" location="bottom">
    <template #activator="{ props: tipProps }">
      <v-btn
        v-bind="tipProps"
        icon
        variant="text"
        class="theme-toggle em-press"
        :aria-label="tooltip"
        @click="toggle"
      >
        <v-icon :icon="icon" size="22" />
      </v-btn>
    </template>
  </v-tooltip>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useThemeMode } from '../../composables/useThemeMode.js'

const { isMorning, toggle } = useThemeMode()
const { t } = useI18n()

const icon = computed(() => (isMorning.value ? 'mdi-weather-night' : 'mdi-white-balance-sunny'))
const tooltip = computed(() =>
  isMorning.value ? t('common.themeToggle.nightMode') : t('common.themeToggle.morningMode'),
)
</script>

<style scoped>
.theme-toggle {
  color: var(--em-text-muted) !important;
  transition: color var(--em-duration-fast) var(--em-ease-out);
}

.theme-toggle:hover {
  color: var(--em-primary-hover) !important;
}
</style>
