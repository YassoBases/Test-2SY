import fs from 'fs'
import path from 'path'
import { entries, commonArMap } from './teacher-i18n-entries.mjs'

const ROOT = path.resolve(import.meta.dirname, '..')
const VIEW_DIR = path.join(ROOT, 'src/views/teacher')
const COMP_DIR = path.join(ROOT, 'src/components/teacher')

function setNested(obj, keyPath, value) {
  const parts = keyPath.split('.')
  let cur = obj
  for (let i = 0; i < parts.length - 1; i++) {
    cur[parts[i]] ??= {}
    cur = cur[parts[i]]
  }
  cur[parts[parts.length - 1]] = value
}

function buildLocaleFiles() {
  const en = {}
  const ar = {}
  for (const [key, enText, arText] of entries) {
    setNested(en, key, enText)
    setNested(ar, key, arText)
  }
  fs.writeFileSync(path.join(ROOT, 'src/locales/en/teacher.json'), JSON.stringify(en, null, 2) + '\n', 'utf8')
  fs.writeFileSync(path.join(ROOT, 'src/locales/ar/teacher.json'), JSON.stringify(ar, null, 2) + '\n', 'utf8')
  return { en, ar }
}

function buildReplacementMap() {
  const map = new Map()
  for (const [key, , arText] of entries) {
    const fullKey = `teacher.${key}`
    if (arText && !map.has(arText)) map.set(arText, fullKey)
  }
  for (const [arText, commonKey] of Object.entries(commonArMap)) {
    map.set(arText, `common.${commonKey}`)
  }
  return [...map.entries()].sort((a, b) => b[0].length - a[0].length)
}

function walk(dir) {
  const out = []
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out.push(...walk(p))
    else if (e.name.endsWith('.vue')) out.push(p)
  }
  return out
}

function escapeRegExp(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function migrateContent(content, replacements) {
  let out = content
  for (const [arText, key] of replacements) {
    const esc = escapeRegExp(arText)
    const attrs = ['title', 'label', 'meta', 'subtitle', 'eyebrow', 'placeholder', 'hint', 'helper', 'helper-before', 'action-label', 'no-data-text', 'empty-text', 'empty-title', 'empty-description']
    for (const attr of attrs) {
      out = out.replace(new RegExp(`(${attr})="${esc}"`, 'g'), `:$1="$t('${key}')"`)
      out = out.replace(new RegExp(`(${attr})='${esc}'`, 'g'), `:$1="$t('${key}')"`)
    }
    out = out.replace(new RegExp(`aria-label="${esc}"`, 'g'), `:aria-label="$t('${key}')"`)
    out = out.replace(new RegExp(`aria-label='${esc}'`, 'g'), `:aria-label="$t('${key}')"`)
    out = out.replace(new RegExp(`>(\\s*)${esc}(\\s*)<`, 'g'), `>$1{{ $t('${key}') }}$2<`)
    out = out.replace(new RegExp(`getErrorMessage\\(\\s*([^,]+),\\s*'${esc}'\\s*\\)`, 'g'), `getErrorMessage($1, t('${key}'))`)
    out = out.replace(new RegExp(`getErrorMessage\\(\\s*([^,]+),\\s*"${esc}"\\s*\\)`, 'g'), `getErrorMessage($1, t('${key}'))`)
    out = out.replace(new RegExp(`showSuccess\\('${esc}'\\)`, 'g'), `showSuccess(t('${key}'))`)
    out = out.replace(new RegExp(`showSuccess\\("${esc}"\\)`, 'g'), `showSuccess(t('${key}'))`)
    out = out.replace(new RegExp(`showError\\('${esc}'\\)`, 'g'), `showError(t('${key}'))`)
    out = out.replace(new RegExp(`showError\\("${esc}"\\)`, 'g'), `showError(t('${key}'))`)
    out = out.replace(new RegExp(`error\\.value\\s*=\\s*'${esc}'`, 'g'), `error.value = t('${key}')`)
    out = out.replace(new RegExp(`error\\.value\\s*=\\s*"${esc}"`, 'g'), `error.value = t('${key}')`)
    out = out.replace(new RegExp(`return\\s+'${esc}'`, 'g'), `return t('${key}')`)
    out = out.replace(new RegExp(`return\\s+"${esc}"`, 'g'), `return t('${key}')`)
  }
  return out
}

function ensureUseI18n(content) {
  if (!content.includes("t('teacher.") && !content.includes('t("teacher.') && !content.includes("t('common.") && !content.includes('$t(')) {
    return content
  }
  if (content.includes('useI18n')) return content
  if (!content.includes('<script setup>')) return content

  let out = content.replace(
    /<script setup>\s*\n/,
    "<script setup>\nimport { useI18n } from 'vue-i18n'\n\nconst { t } = useI18n()\n",
  )
  if (out === content) {
    out = content.replace(
      /<script setup>/,
      "<script setup>\nimport { useI18n } from 'vue-i18n'\nconst { t } = useI18n()",
    )
  }
  return out
}

function migrateFiles(replacements) {
  const files = [...walk(VIEW_DIR), ...walk(COMP_DIR)]
  const migrated = []
  for (const file of files) {
    const original = fs.readFileSync(file, 'utf8')
    let next = migrateContent(original, replacements)
    next = ensureUseI18n(next)
    if (next !== original) {
      fs.writeFileSync(file, next, 'utf8')
      migrated.push(path.relative(ROOT, file))
    }
  }
  return migrated
}

const { en } = buildLocaleFiles()
const replacements = buildReplacementMap()
const migrated = migrateFiles(replacements)

function countKeys(obj, prefix = '') {
  let n = 0
  for (const [k, v] of Object.entries(obj)) {
    if (v && typeof v === 'object' && !Array.isArray(v)) n += countKeys(v, `${prefix}${k}.`)
    else n++
  }
  return n
}

console.log('Keys added:', countKeys(en))
console.log('Replacement rules:', replacements.length)
console.log('Files migrated:', migrated.length)
migrated.forEach((f) => console.log(' -', f))
