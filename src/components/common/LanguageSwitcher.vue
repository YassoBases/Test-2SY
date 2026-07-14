<template>
  <v-menu location="bottom end" :close-on-content-click="true">
    <template #activator="{ props: menuProps }">
      <v-btn
        v-bind="menuProps"
        icon
        variant="text"
        size="small"
        class="language-switcher"
        :aria-label="t('common.languageSwitcher.aria')"
      >
        <v-icon size="20">mdi-web</v-icon>
      </v-btn>
    </template>
    <v-list class="language-switcher__menu glass-card glass-card--solid" density="compact">
      <v-list-subheader>{{ t('settings.language.title') }}</v-list-subheader>
      <v-list-item
        v-for="opt in localeOptions"
        :key="opt.value"
        :title="opt.label"
        :active="locale === opt.value"
        @click="setLocale(opt.value)"
      >
        <template #prepend>
          <v-icon v-if="locale === opt.value" size="18" color="primary">mdi-check</v-icon>
          <span v-else class="language-switcher__spacer" aria-hidden="true" />
        </template>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { useAppLocale } from '../../composables/useAppLocale.js'

const { t } = useI18n()
const { locale, localeOptions, setLocale } = useAppLocale()
</script>

<style scoped>
.language-switcher {
  color: var(--em-text-muted);
}

.language-switcher__menu {
  min-width: 180px;
  border-radius: var(--em-radius-md) !important;
}

.language-switcher__spacer {
  display: inline-block;
  width: 18px;
}
</style>
