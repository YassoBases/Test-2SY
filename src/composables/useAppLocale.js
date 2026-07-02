import { computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocale } from 'vuetify'
import { isRtlLocale, setAppLocale, SUPPORTED_LOCALES } from '../i18n/index.js'

export function useAppLocale() {
  const { locale, t } = useI18n({ useScope: 'global' })
  const vuetifyLocale = useLocale()

  const isRtl = computed(() => isRtlLocale(locale.value))

  function setLocale(next) {
    if (!SUPPORTED_LOCALES.includes(next) || next === locale.value) return
    setAppLocale(next)
    vuetifyLocale.current.value = next
    vuetifyLocale.isRtl.value = isRtlLocale(next)
  }

  watch(
    locale,
    (value) => {
      vuetifyLocale.current.value = value
      vuetifyLocale.isRtl.value = isRtlLocale(value)
    },
    { immediate: true },
  )

  const localeOptions = computed(() => [
    { value: 'ar', label: t('settings.language.arabic') },
    { value: 'en', label: t('settings.language.english') },
  ])

  return {
    locale,
    isRtl,
    setLocale,
    localeOptions,
    SUPPORTED_LOCALES,
  }
}
