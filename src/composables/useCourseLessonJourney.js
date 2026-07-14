/**
 * Derives journey states for course lessons (UI-4.3.5).
 * Uses existing lesson fields only — no new backend logic.
 */
export function deriveLessonJourneyState(lessons, courseUnlocked = true) {
  if (!Array.isArray(lessons) || !lessons.length) return []

  let currentIndex = lessons.findIndex((lesson) => !lesson.completed)
  if (currentIndex === -1) currentIndex = -1

  return lessons.map((lesson, index) => {
    let state = 'upcoming'

    if (!courseUnlocked) {
      state = 'locked'
    } else if (lesson.completed) {
      state = 'completed'
    } else if (currentIndex === -1) {
      state = 'completed'
    } else if (index === currentIndex) {
      state = 'current'
    } else if (index < currentIndex) {
      state = 'completed'
    } else {
      state = 'upcoming'
    }

    return {
      ...lesson,
      journeyIndex: index + 1,
      journeyState: state,
    }
  })
}

export function findNextLesson(lessons) {
  if (!Array.isArray(lessons) || !lessons.length) return null
  const incomplete = lessons.find((lesson) => !lesson.completed)
  return incomplete || lessons[lessons.length - 1]
}

export function findCurrentLesson(lessons) {
  if (!Array.isArray(lessons) || !lessons.length) return null
  const incomplete = lessons.find((lesson) => !lesson.completed)
  if (incomplete) return incomplete
  return lessons[lessons.length - 1]
}

export const JOURNEY_STATE_LABELS = {
  completed: 'مكتمل',
  current: 'الدرس الحالي',
  upcoming: 'قادم',
  locked: 'مقفل',
}

export const JOURNEY_STATE_ICONS = {
  completed: 'mdi-check',
  current: 'mdi-play-circle',
  upcoming: 'mdi-circle-outline',
  locked: 'mdi-lock',
}
