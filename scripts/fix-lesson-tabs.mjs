import { readFileSync, writeFileSync } from 'node:fs'

const p = 'src/views/student/StudentLessonView.vue'
let c = readFileSync(p, 'utf8')
c = c.replace(/اسأل المعل[\u0645\uFEEF\uFEEA\u064E\u0651]+/g, "{{ t('student.lesson.tabs.askTeacher') }}")
writeFileSync(p, c)
console.log('fixed ask teacher tab')
