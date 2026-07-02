import { useI18n } from 'vue-i18n'
import { dateLocaleTag, pickLocalizedField, translateEnum } from '../utils/localizedApiLabel.js'

export function useLocalizedLabels() {
  const { t, te, locale } = useI18n()

  function gradeLabel(grade) {
    const value = grade?.value ?? grade
    return translateEnum(t, te, 'auth.onboarding.gradeLabels', value, grade?.label_ar)
  }

  function subjectName(subject) {
    const slug = subject?.slug
    if (slug && te(`auth.onboarding.catalog.subjects.${slug}`)) {
      return t(`auth.onboarding.catalog.subjects.${slug}`)
    }
    return subject?.name_ar || ''
  }

  function noteCategory(value, apiFallback = '') {
    return translateEnum(t, te, 'parent.notes.categories', value, apiFallback)
  }

  function noteStatus(value, apiFallback = '') {
    return translateEnum(t, te, 'parent.notes.statuses', value, apiFallback)
  }

  function notePriority(value, apiFallback = '') {
    return translateEnum(t, te, 'parent.notes.priorities', value, apiFallback)
  }

  function localizeOptionTitle(group, value, fallback = '') {
    return translateEnum(t, te, `auth.onboarding.personalize.options.${group}`, value, fallback)
  }

  function personalizePreview(group, value) {
    if (!value) return null
    const key = `auth.onboarding.personalize.previews.${group}.${value}`
    return te(key) ? t(key) : null
  }

  return {
    locale,
    t,
    te,
    dateLocale: () => dateLocaleTag(locale.value),
    pickLocalizedField: (item, base = 'label') => pickLocalizedField(item, base, locale.value),
    gradeLabel,
    subjectName,
    noteCategory,
    noteStatus,
    notePriority,
    localizeOptionTitle,
    personalizePreview,
  }
}
