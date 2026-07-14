const SELECTED_STUDENT_KEY = 'eduspark_parent_selected_student'

/** Unwrap a Vue ref (or raw id) without treating null as "missing" (avoid ?? on .value). */
export function resolveParentStudentId(selectedStudentId) {
  if (selectedStudentId != null && typeof selectedStudentId === 'object' && 'value' in selectedStudentId) {
    return selectedStudentId.value ?? null
  }
  return selectedStudentId ?? null
}

export function getSelectedStudentId() {
  try {
    const raw = localStorage.getItem(SELECTED_STUDENT_KEY)
    if (!raw) return null
    const id = Number(raw)
    return Number.isFinite(id) ? id : null
  } catch {
    return null
  }
}

export function setSelectedStudentId(studentId) {
  if (studentId == null) {
    localStorage.removeItem(SELECTED_STUDENT_KEY)
    return
  }
  localStorage.setItem(SELECTED_STUDENT_KEY, String(studentId))
}

export function clearSelectedStudentId() {
  localStorage.removeItem(SELECTED_STUDENT_KEY)
}
