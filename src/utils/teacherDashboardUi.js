/** TEACHER-UI-1.1 — Dashboard presentation helpers (no API changes). */

export function parseActivityLine(line) {
  if (!line || typeof line !== 'string') return { title: String(line || ''), time: '' }
  const parts = line.split(' — ')
  if (parts.length >= 2) {
    return { title: parts[0].trim(), time: parts.slice(1).join(' — ').trim() }
  }
  return { title: line.trim(), time: '' }
}

export function enrichActivityItem(line, idx) {
  const { title, time } = parseActivityLine(line)
  const lower = `${title} ${time}`.toLowerCase()

  let icon = 'mdi-circle-small'
  if (title.includes('إكمال') || lower.includes('complete')) {
    icon = 'mdi-check-circle-outline'
  } else if (title.includes('كويز') || title.includes('اختبار') || lower.includes('quiz')) {
    icon = 'mdi-clipboard-text-outline'
  } else if (title.includes('نشر') || title.includes('منشور')) {
    icon = 'mdi-book-check-outline'
  } else if (title.includes('تعديل') || title.includes('تحديث')) {
    icon = 'mdi-pencil-outline'
  } else if (title.includes('انضم') || title.includes('طالب')) {
    icon = 'mdi-account-plus-outline'
  } else if (title.includes('ذكاء') || title.includes('معالجة')) {
    icon = 'mdi-robot-outline'
  }

  return {
    id: `activity-${idx}`,
    title,
    time,
    icon,
  }
}

export function workspaceLatestActivity(course) {
  if (course.most_viewed_lesson_title) {
    return `آخر تفاعل: «${course.most_viewed_lesson_title}»`
  }
  if (course.lesson_count === 0) {
    return 'لم يُرفع درس منشور بعد'
  }
  if (!course.is_published) {
    return 'الصف مسودة — انشره للطلاب'
  }
  if (course.subscribed_students > 0 && course.completion_percent > 0) {
    return `${course.completion_percent}% من الدروس مكتملة`
  }
  if (course.subscribed_students > 0) {
    return `${course.subscribed_students} طالب مسجّل`
  }
  return 'جاهز لاستقبال الطلاب'
}
