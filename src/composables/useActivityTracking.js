/**
 * Real study-time tracking — page navigation and lesson engagement pings.
 * Only meaningful platform actions are sent; idle browser time is never counted.
 */

import { recordActivityEvent } from '../api/activity.js'
import { getSession } from '../utils/session.js'

const NAV_DEBOUNCE_MS = 3000
const LESSON_VIEW_DEBOUNCE_MS = 60_000

let lastNavPath = ''
let lastNavAt = 0
let lastLessonViewId = null
let lastLessonViewAt = 0

function isStudentSession() {
  const session = getSession()
  return session?.role === 'student' && !session?.viewerMode
}

function safeRecord(payload) {
  if (!isStudentSession()) return
  recordActivityEvent(payload).catch(() => {})
}

export function trackPageNavigation(path) {
  if (!path || !isStudentSession()) return
  const now = Date.now()
  if (path === lastNavPath && now - lastNavAt < NAV_DEBOUNCE_MS) return
  lastNavPath = path
  lastNavAt = now
  safeRecord({
    event_type: 'page_navigation',
    path,
    resource_type: 'route',
  })
}

export function trackLessonViewed(lessonId) {
  if (!lessonId || !isStudentSession()) return
  const now = Date.now()
  if (lessonId === lastLessonViewId && now - lastLessonViewAt < LESSON_VIEW_DEBOUNCE_MS) return
  lastLessonViewId = lessonId
  lastLessonViewAt = now
  safeRecord({
    event_type: 'lesson_viewed',
    resource_type: 'lesson',
    resource_id: Number(lessonId),
  })
}

export function trackQuizStarted(lessonId) {
  if (!lessonId) return
  safeRecord({
    event_type: 'quiz_started',
    resource_type: 'lesson',
    resource_id: Number(lessonId),
  })
}

export function installActivityTracking(router) {
  router.afterEach((to) => {
    trackPageNavigation(to.fullPath)
  })
}
