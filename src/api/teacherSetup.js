import { api } from './client.js'

export async function fetchTeacherSetupStatus() {
  const { data } = await api.get('/teacher/setup/status')
  return data
}

export async function updateTeacherProfile({ fullName, bio }) {
  const { data } = await api.put('/teacher/setup/profile', {
    full_name: fullName,
    bio: bio || null,
  })
  return data
}

export async function uploadTeacherAvatar(file) {
  if (!file || !(file instanceof File)) {
    throw new Error('لم يتم اختيار ملف صورة صالح')
  }
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/teacher/setup/avatar', form)
  return data
}

export async function updateTeacherTeaching({ subjectIds, grades }) {
  const { data } = await api.put('/teacher/setup/teaching', {
    subject_ids: subjectIds,
    grades,
  })
  return data
}

export async function fetchTeacherAiProfile() {
  const { data } = await api.get('/teacher/setup/ai-profile')
  return data
}

export async function updateTeacherAiProfile({
  teacherTeachingStyle,
  teacherTone,
  teacherQuestionStyle,
  teacherMotivationLevel,
  teacherDisplayName,
  teacherBio,
  teacherSignaturePhrase,
}) {
  const { data } = await api.put('/teacher/setup/ai-profile', {
    teacher_teaching_style: teacherTeachingStyle,
    teacher_tone: teacherTone,
    teacher_question_style: teacherQuestionStyle,
    teacher_motivation_level: teacherMotivationLevel,
    teacher_display_name: teacherDisplayName,
    teacher_bio: teacherBio,
    teacher_signature_phrase: teacherSignaturePhrase,
  })
  return data
}

export async function fetchTeacherSetupSubjects(grade) {
  const { data } = await api.get('/teacher/setup/subjects', { params: { grade } })
  return data
}

export async function createTeacherCourse(payload) {
  const { data } = await api.post('/teacher/setup/courses', {
    title: payload.title,
    subject_id: payload.subjectId,
    grade: payload.grade,
    price: payload.price,
  })
  return data
}

export async function completeTeacherSetup() {
  const { data } = await api.post('/teacher/setup/complete')
  return data
}
