export const LESSON_COMPLETED_EVENT = 'eduspark:lesson-completed'

export function notifyLessonCompleted(detail = {}) {
  window.dispatchEvent(new CustomEvent(LESSON_COMPLETED_EVENT, { detail }))
}
