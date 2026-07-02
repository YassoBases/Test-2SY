import fs from 'fs'
import path from 'path'
import { entries, commonArMap } from './teacher-i18n-entries.mjs'

const ROOT = path.resolve(import.meta.dirname, '..')
const dirs = ['src/views/teacher', 'src/components/teacher']

function walk(dir) {
  const out = []
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out.push(...walk(p))
    else if (e.name.endsWith('.vue')) out.push(p)
  }
  return out
}

function buildReplacementMap() {
  const map = new Map()
  for (const [key, , arText] of entries) {
    if (arText && !map.has(arText)) map.set(arText, `teacher.${key}`)
  }
  for (const [arText, commonKey] of Object.entries(commonArMap)) {
    map.set(arText, `common.${commonKey}`)
  }
  return [...map.entries()].sort((a, b) => b[0].length - a[0].length)
}

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function fixImports(content) {
  if (!content.includes('useI18n')) return content
  const m = content.match(/<script setup>\s*\n([\s\S]*?)<\/script>/)
  if (!m) return content
  const body = m[1]
  if (!body.includes("from 'vue-i18n'")) return content
  const lines = body.split('\n')
  const vueI18n = []
  const vue = []
  const rest = []
  for (const line of lines) {
    if (line.includes("from 'vue-i18n'") || line.trim() === 'const { t } = useI18n()') vueI18n.push(line)
    else if (line.includes("from 'vue'")) vue.push(line)
    else rest.push(line)
  }
  const ordered = [...vue, ...vueI18n, ...rest].join('\n')
  return content.replace(m[0], `<script setup>\n${ordered}</script>`)
}

function migrateScriptLiterals(content, replacements) {
  let out = content
  for (const [arText, key] of replacements) {
    if (out.includes(`$t('${key}')`) || out.includes(`t('${key}')`)) continue
    const esc = escapeRegExp(arText)
    out = out.replace(new RegExp(`(label|title|message|actionLabel|emptyText|placeholder|hint|meta|subtitle|eyebrow|text|statusText|helper|description|noDataText|action-label)\\s*:\\s*'${esc}'`, 'g'), `$1: t('${key}')`)
    out = out.replace(new RegExp(`(label|title|message|actionLabel|emptyText|placeholder|hint|meta|subtitle|eyebrow|text|statusText|helper|description|noDataText|action-label)\\s*:\\s*"${esc}"`, 'g'), `$1: t('${key}')`)
    out = out.replace(new RegExp(`\\|\\|\\s*'${esc}'`, 'g'), `|| t('${key}')`)
    out = out.replace(new RegExp(`\\|\\|\\s*"${esc}"`, 'g'), `|| t('${key}')`)
    out = out.replace(new RegExp(`=>\s*'${esc}'`, 'g'), `=> t('${key}')`)
    out = out.replace(new RegExp(`=>\s*"${esc}"`, 'g'), `=> t('${key}')`)
    out = out.replace(new RegExp(`\\?\s*'${esc}'\\s*:`, 'g'), `? t('${key}') :`)
    out = out.replace(new RegExp(`: \`'[^\`]*${esc}[^\`]*\`\\s*\\}`, 'g'), (match) => {
      if (match.includes('t(')) return match
      return match.replace(arText, `\${t('${key}')}`)
    })
  }
  return out
}

const replacements = buildReplacementMap()
let changed = 0
for (const dir of dirs) {
  for (const file of walk(path.join(ROOT, dir))) {
    const original = fs.readFileSync(file, 'utf8')
    let next = migrateScriptLiterals(original, replacements)
    next = fixImports(next)
    if (next !== original) {
      fs.writeFileSync(file, next, 'utf8')
      changed++
      console.log('fixed', path.relative(ROOT, file))
    }
  }
}
console.log('Script pass files:', changed)
