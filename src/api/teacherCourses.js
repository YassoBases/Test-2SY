import { api } from './client.js'

export async function fetchCourseFormContext(grade) {
  const params = grade != null ? { grade } : {}
  const { data } = await api.get('/teacher/courses/form-context', { params })
  return data
}

export async function fetchTeacherCourses() {
  const { data } = await api.get('/teacher/courses')
  return data
}

export async function createTeacherCourse(form) {
  const body = new FormData()
  body.append('title', form.title)
  body.append('subject_id', String(form.subjectId))
  body.append('grade', String(form.grade))
  body.append('price', String(form.price ?? 0))
  if (form.description) body.append('description', form.description)
  body.append('is_published', form.isPublished ? 'true' : 'false')
  if (form.thumbnail) body.append('thumbnail', form.thumbnail)
  if (form.banner) body.append('banner', form.banner)

  const { data } = await api.post('/teacher/courses/create', body, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function updateTeacherCourse(courseId, payload) {
  const { data } = await api.put(`/teacher/courses/${courseId}`, payload)
  return data
}

export async function fetchCourseLessons(courseId) {
  const { data } = await api.get(`/teacher/courses/${courseId}/lessons`)
  return data
}

export async function fetchTeacherLessonPreview(courseId, lessonId) {
  const { data } = await api.get(`/teacher/courses/${courseId}/lessons/${lessonId}`)
  return data
}

export async function updateTeacherLesson(courseId, lessonId, payload) {
  const { data } = await api.patch(`/teacher/courses/${courseId}/lessons/${lessonId}`, payload)
  return data
}

export async function updateTeacherLessonContent(
  courseId,
  lessonId,
  {
    title,
    description,
    isVisible = true,
    removeVideo = false,
    removePdf = false,
    removeAudio = false,
    video = null,
    pdf = null,
    audio = null,
  },
  onProgress,
) {
  const form = new FormData()
  form.append('title', title)
  if (description) form.append('description', description)
  form.append('is_visible', isVisible ? 'true' : 'false')
  form.append('remove_video', removeVideo ? 'true' : 'false')
  form.append('remove_pdf', removePdf ? 'true' : 'false')
  form.append('remove_audio', removeAudio ? 'true' : 'false')
  if (video) form.append('video', video)
  if (pdf) form.append('pdf', pdf)
  if (audio) form.append('audio', audio)

  const { data } = await api.post(
    `/teacher/courses/${courseId}/lessons/${lessonId}/update-content`,
    form,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 10 * 60 * 1000,
      onUploadProgress: (event) => {
        if (onProgress && event.total) {
          onProgress(Math.round((event.loaded / event.total) * 100))
        }
      },
    },
  )
  return data
}

function lessonFormData({ title, description, sortOrder, file, lessonId }) {
  const form = new FormData()
  form.append('title', title)
  if (description) form.append('description', description)
  form.append('sort_order', String(sortOrder ?? 0))
  if (lessonId) form.append('lesson_id', String(lessonId))
  if (file) form.append('file', file)
  return form
}

export async function createCourseLesson(
  courseId,
  { title, description, video, pdf, videoUrl, sortOrder = 0 },
  onProgress,
) {
  const form = new FormData()
  form.append('title', title)
  if (description) form.append('description', description)
  form.append('sort_order', String(sortOrder))
  if (video) form.append('video', video)
  if (pdf) form.append('pdf', pdf)
  if (videoUrl) form.append('video_url', videoUrl)
  const { data } = await api.post(`/teacher/courses/${courseId}/lessons`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 10 * 60 * 1000,
    onUploadProgress: (event) => {
      if (onProgress && event.total) {
        onProgress(Math.round((event.loaded / event.total) * 100))
      }
    },
  })
  return data
}

export async function publishLesson(
  {
    grade,
    subjectId,
    title,
    description,
    sortOrder = 0,
    courseId,
    video,
    pdf,
  },
  onProgress,
) {
  const form = new FormData()
  form.append('grade', String(grade))
  form.append('subject_id', String(subjectId))
  form.append('title', title)
  if (description) form.append('description', description)
  form.append('sort_order', String(sortOrder))
  if (courseId) form.append('course_id', String(courseId))
  if (video) form.append('video', video)
  if (pdf) form.append('pdf', pdf)
  const { data } = await api.post('/teacher/lessons/publish', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 10 * 60 * 1000,
    onUploadProgress: (event) => {
      if (onProgress && event.total) {
        onProgress(Math.round((event.loaded / event.total) * 100))
      }
    },
  })
  return data
}

export async function fetchLessonPublishStatus(lessonId) {
  const { data } = await api.get(`/teacher/lessons/${lessonId}/publish-status`)
  return data
}

export async function uploadFullCourseLesson(courseId, { title, description, sortOrder, video, pdf }) {
  const form = new FormData()
  form.append('title', title)
  if (description) form.append('description', description)
  form.append('sort_order', String(sortOrder ?? 0))
  if (video) form.append('video', video)
  if (pdf) form.append('pdf', pdf)
  const { data } = await api.post(`/teacher/courses/${courseId}/lessons/full`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function uploadCourseVideo(courseId, payload) {
  const { data } = await api.post(
    `/teacher/courses/${courseId}/lessons/video`,
    lessonFormData(payload),
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return data
}

export async function uploadCoursePdf(courseId, payload) {
  const { data } = await api.post(
    `/teacher/courses/${courseId}/lessons/pdf`,
    lessonFormData(payload),
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return data
}

export async function uploadCourseHomework(courseId, payload) {
  const { data } = await api.post(
    `/teacher/courses/${courseId}/lessons/homework`,
    lessonFormData(payload),
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return data
}

export async function processCourseLesson(courseId, lessonId) {
  const { data } = await api.post(`/teacher/courses/${courseId}/lessons/${lessonId}/process`)
  return data
}

export async function regenerateCourseLessonQuiz(courseId, lessonId) {
  const { data } = await api.post(
    `/teacher/courses/${courseId}/lessons/${lessonId}/quiz/regenerate`,
  )
  return data
}
