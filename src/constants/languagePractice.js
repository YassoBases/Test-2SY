import { ROUTES } from '../constants/app.js'

/** Practice destinations — skills live under Practice hub, not top-level nav. */
export const LANGUAGE_PRACTICE_SKILLS = [
  {
    key: 'speaking',
    label: '',
    description: '',
    icon: 'mdi-microphone',
    color: 'secondary',
    to: ROUTES.STUDENT_LANGUAGES_SPEAKING,
  },
  {
    key: 'reading',
    label: '',
    description: '',
    icon: 'mdi-book-open-variant',
    color: 'primary',
    to: ROUTES.STUDENT_LANGUAGES_READING,
  },
  {
    key: 'listening',
    label: '',
    description: '',
    icon: 'mdi-headphones',
    color: 'primary',
    to: ROUTES.STUDENT_LANGUAGES_LISTENING,
  },
  {
    key: 'writing',
    label: '',
    description: '',
    icon: 'mdi-pencil',
    color: 'primary',
    to: ROUTES.STUDENT_LANGUAGES_WRITING,
  },
  {
    key: 'vocabulary',
    label: '',
    description: '',
    icon: 'mdi-cards-outline',
    color: 'primary',
    to: ROUTES.STUDENT_LANGUAGES_VOCABULARY,
  },
  {
    key: 'grammar',
    label: '',
    description: '',
    icon: 'mdi-book-education',
    color: 'primary',
    to: ROUTES.STUDENT_LANGUAGES_LESSONS,
  },
]

const PRACTICE_PATH_SEGMENTS = [
  '/practice',
  '/reading',
  '/listening',
  '/vocabulary',
  '/writing',
  '/speaking',
  '/lessons',
  '/scenarios',
]

export function isLanguagePracticeRoute(path) {
  return PRACTICE_PATH_SEGMENTS.some((seg) => path.includes(`/languages${seg}`))
}

export function isLanguageInsightsRoute(path) {
  return path.includes('/languages/progress') || path.includes('/languages/insights')
}
