import { computed, ref } from 'vue'
import { fetchLinkedStudents, linkParentStudent } from '../api/parent.js'
import { getErrorMessage } from '../api/client.js'
import { getSelectedStudentId, setSelectedStudentId } from '../utils/parentStorage.js'
import { isApiMode } from '../utils/session.js'

export function useParentStudents() {
  const students = ref([])
  const selectedStudentId = ref(getSelectedStudentId())
  const loadingStudents = ref(false)
  const studentsError = ref('')
  const linking = ref(false)
  const linkError = ref('')
  const linkSuccess = ref('')

  const hasStudents = computed(() => students.value.length > 0)
  const selectedStudent = computed(() =>
    students.value.find((s) => s.id === selectedStudentId.value) ?? null,
  )

  function syncSelectionAfterLoad() {
    if (!students.value.length) {
      selectedStudentId.value = null
      setSelectedStudentId(null)
      return
    }
    const stored = getSelectedStudentId()
    const valid = students.value.some((s) => s.id === stored)
    if (valid) {
      selectedStudentId.value = stored
    } else {
      selectedStudentId.value = students.value[0].id
      setSelectedStudentId(selectedStudentId.value)
    }
  }

  async function loadStudents() {
    if (!isApiMode()) {
      studentsError.value = 'ربط الطلاب يتطلب الاتصال بالخادم'
      students.value = []
      return
    }
    loadingStudents.value = true
    studentsError.value = ''
    try {
      students.value = await fetchLinkedStudents()
      syncSelectionAfterLoad()
    } catch (err) {
      studentsError.value = getErrorMessage(err, 'تعذر تحميل قائمة الطلاب')
      students.value = []
      selectedStudentId.value = null
    } finally {
      loadingStudents.value = false
    }
  }

  function selectStudent(studentId) {
    if (!students.value.some((s) => s.id === studentId)) return
    selectedStudentId.value = studentId
    setSelectedStudentId(studentId)
  }

  async function linkStudent(linkCode) {
    const code = String(linkCode || '').trim().toUpperCase()
    if (!code) {
      linkError.value = 'أدخل رمز الربط'
      return false
    }
    linking.value = true
    linkError.value = ''
    linkSuccess.value = ''
    try {
      const result = await linkParentStudent(code)
      await loadStudents()
      if (result?.student_id) {
        selectStudent(result.student_id)
      }
      linkSuccess.value = 'تم ربط الطالب بنجاح'
      return true
    } catch (err) {
      linkError.value = getErrorMessage(err, 'تعذر ربط الطالب — تحقق من الرمز')
      return false
    } finally {
      linking.value = false
    }
  }

  return {
    students,
    selectedStudentId,
    selectedStudent,
    hasStudents,
    loadingStudents,
    studentsError,
    linking,
    linkError,
    linkSuccess,
    loadStudents,
    selectStudent,
    linkStudent,
  }
}
