import fs from 'fs'
import path from 'path'

const I18N_IMPORT = "import { useI18n } from 'vue-i18n'\n"
const I18N_SETUP = "const { t, locale } = useI18n()\n"

function walk(dir) {
  const results = []
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) results.push(...walk(p))
    else if (e.name.endsWith('.vue')) results.push(p)
  }
  return results
}

function ensureI18n(content) {
  if (content.includes('useI18n')) return content
  const scriptMatch = content.match(/<script setup>\n/)
  if (!scriptMatch) return content
  let updated = content.replace('<script setup>\n', `<script setup>\n${I18N_IMPORT}${I18N_SETUP}`)
  return updated
}

function addDateLocaleHelper(content) {
  if (content.includes('function dateLocale')) return content
  if (!content.includes('toLocaleDateString') && !content.includes('Intl.DateTimeFormat') && !content.includes('toLocaleString')) {
    return content
  }
  const helper = `
function dateLocale() {
  return locale.value === 'ar' ? 'ar-SY' : 'en-US'
}
`
  return content.replace(I18N_SETUP, `${I18N_SETUP}${helper}`)
}

function replaceAr(content, from, to) {
  if (!content.includes(from)) return content
  return content.split(from).join(to)
}

const skip = new Set([
  'ParentPlannerTaskList.vue',
  'ParentStudentContextBar.vue',
])

const dirs = ['src/views/parent', 'src/components/parent']
const modified = []

for (const d of dirs) {
  for (const file of walk(d)) {
    const base = path.basename(file)
    if (skip.has(base)) continue

    let content = fs.readFileSync(file, 'utf8')
    const original = content

    content = ensureI18n(content)
    content = addDateLocaleHelper(content)

    // ar-SY -> dateLocale()
    content = content.replace(/toLocaleDateString\('ar-SY'/g, "toLocaleDateString(dateLocale()")
    content = content.replace(/toLocaleString\('ar-SY'/g, "toLocaleString(dateLocale()")
    content = content.replace(/toLocaleTimeString\('ar-SY'/g, "toLocaleTimeString(dateLocale()")
    content = content.replace(/new Intl\.DateTimeFormat\('ar-SY'/g, 'new Intl.DateTimeFormat(dateLocale()')
    content = content.replace(/toLocaleDateString\('ar-SA'/g, "toLocaleDateString(dateLocale()")

    if (content !== original) {
      fs.writeFileSync(file, content)
      modified.push(file)
    }
  }
}

console.log(JSON.stringify({ modifiedCount: modified.length, modified }, null, 2))
