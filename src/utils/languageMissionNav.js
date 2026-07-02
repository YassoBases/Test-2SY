import { markObjectivePracticed } from '../api/language.js'
import { ROUTES } from '../constants/app.js'

export function navigateToLanguageFeature(router, feature, focus) {
  const q = focus ? { focus } : {}
  if (feature === 'conversation') {
    router.push({ path: ROUTES.STUDENT_LANGUAGES_SPEAKING, query: { mode: 'conversation', ...q } })
  } else if (feature === 'speaking') {
    router.push({ path: ROUTES.STUDENT_LANGUAGES_SPEAKING, query: { mode: 'exercises', ...q } })
  } else if (feature === 'writing') {
    router.push({ path: ROUTES.STUDENT_LANGUAGES_WRITING, query: q })
  } else if (feature === 'reading') {
    router.push(ROUTES.STUDENT_LANGUAGES_READING)
  } else if (feature === 'listening') {
    router.push(ROUTES.STUDENT_LANGUAGES_LISTENING)
  } else if (feature === 'vocabulary') {
    router.push(ROUTES.STUDENT_LANGUAGES_VOCABULARY)
  } else {
    router.push({ path: ROUTES.STUDENT_LANGUAGES_SPEAKING, query: { mode: 'conversation', ...q } })
  }
}

export async function startDailyPlanItem(router, item) {
  if (item?.objective_id) {
    try {
      await markObjectivePracticed(item.objective_id)
    } catch {
      /* best-effort */
    }
  }
  navigateToLanguageFeature(router, item.feature, item.focus || undefined)
}
