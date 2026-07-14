<template>
  <a
    href="https://www.instagram.com/eduspark_sy"
    target="_blank"
    rel="noopener noreferrer"
    class="instagram-link"
    :class="{
      'instagram-link--compact': compact,
      'instagram-link--card': variant === 'card',
    }"
  >
    <template v-if="variant === 'card'">
      <span class="instagram-link__card-icon" aria-hidden="true">
        <v-icon size="22">mdi-instagram</v-icon>
      </span>
      <span class="instagram-link__card-body">
        <span class="instagram-link__handle">{{ t('auth.welcome.instagram.handle') }}</span>
        <span class="instagram-link__hint">{{ t('auth.welcome.instagram.hintCard') }}</span>
      </span>
      <v-icon size="18" class="instagram-link__arrow">mdi-chevron-left</v-icon>
    </template>
    <template v-else>
      <v-icon size="18" class="instagram-link__icon">mdi-instagram</v-icon>
      <span class="instagram-link__handle">{{ t('auth.welcome.instagram.handle') }}</span>
      <span class="instagram-link__hint">{{ t('auth.welcome.instagram.hintInline') }}</span>
      <v-icon size="14" class="instagram-link__arrow">mdi-open-in-new</v-icon>
    </template>
  </a>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

defineProps({
  compact: { type: Boolean, default: false },
  variant: { type: String, default: 'inline' },
})

const { t } = useI18n()
</script>
