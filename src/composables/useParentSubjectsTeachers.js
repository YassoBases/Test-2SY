import { ref } from 'vue'
import { fetchParentCourseTeacherProfile, fetchParentSubjectsTeachers } from '../api/parent.js'
import { getErrorMessage } from '../api/client.js'
import { resolveParentStudentId } from '../utils/parentStorage.js'
import { isApiMode } from '../utils/session.js'

export function useParentSubjectsTeachers(selectedStudentId) {
  const loading = ref(false)
  const loadError = ref('')
  const profileError = ref('')
  const data = ref(null)
  const profileLoading = ref(false)
  const teacherProfile = ref(null)
  let loadSeq = 0

  async function load() {
    const studentId = resolveParentStudentId(selectedStudentId)
    if (studentId == null) {
      loadSeq += 1
      data.value = null
      loadError.value = ''
      loading.value = false
      return
    }
    if (!isApiMode()) {
      loadError.value = 'عرض المواد يتطلب الاتصال بالخادم'
      return
    }

    const seq = ++loadSeq
    loading.value = true
    loadError.value = ''
    try {
      const result = await fetchParentSubjectsTeachers(studentId)
      if (seq !== loadSeq) return
      data.value = result
      loadError.value = ''
    } catch (err) {
      if (seq !== loadSeq) return
      loadError.value = getErrorMessage(err, 'تعذر تحميل المواد والأساتذة')
      data.value = null
    } finally {
      if (seq === loadSeq) loading.value = false
    }
  }

  async function loadTeacherProfile(courseId) {
    const studentId = resolveParentStudentId(selectedStudentId)
    if (studentId == null || courseId == null) return null

    profileLoading.value = true
    profileError.value = ''
    teacherProfile.value = null
    try {
      teacherProfile.value = await fetchParentCourseTeacherProfile(courseId, studentId)
      return teacherProfile.value
    } catch (err) {
      profileError.value = getErrorMessage(err, 'تعذر تحميل ملف المعلّم')
      return null
    } finally {
      profileLoading.value = false
    }
  }

  return {
    loading,
    loadError,
    profileError,
    data,
    profileLoading,
    teacherProfile,
    load,
    loadTeacherProfile,
  }
}
