/** Fix broken {{ t() }} inside script strings and attributes. */
import { readFileSync, writeFileSync, readdirSync, statSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name)
    if (statSync(p).isDirectory()) walk(p, out)
    else if (name.endsWith('.vue')) out.push(p)
  }
  return out
}

function fixScriptSection(script) {
  let c = script
  // Pure: '{{ t('key') }}' -> t('key')
  c = c.replace(/'\{\{\s*t\('([^']+)'\)\s*\}\}'/g, "t('$1')")
  c = c.replace(/"\{\{\s*t\('([^']+)'\)\s*\}\}"/g, "t('$1')")
  // Mixed in single-quoted strings: 'text {{ t('key') }} more'
  c = c.replace(
    /'([^'\\]*?)\{\{\s*t\('([^']+)'\)\s*\}\}([^'\\]*?)'/g,
    (_, before, key, after) => `\`${before}\${t('${key}')}${after}\``,
  )
  // Mixed in double-quoted strings
  c = c.replace(
    /"([^"\\]*?)\{\{\s*t\('([^']+)'\)\s*\}\}([^"\\]*?)"/g,
    (_, before, key, after) => `\`${before}\${t('${key}')}${after}\``,
  )
  // Mixed in template literals
  c = c.replace(/\{\{\s*t\('([^']+)'\)\s*\}\}/g, "${t('$1')}")
  // Duplicate useI18n
  c = c.replace(
    /(const\s*\{\s*t\s*\}\s*=\s*useI18n\(\)\s*\n\s*)+const\s*\{\s*t\s*\}\s*=\s*useI18n\(\)/g,
    'const { t } = useI18n()',
  )
  return c
}

function fix(content) {
  let c = content
  c = c.replace(/<script([^>]*)>([\s\S]*?)<\/script>/g, (full, attrs, body) => {
    return `<script${attrs}>${fixScriptSection(body)}</script>`
  })
  // attributes outside script: attr="{{ t('key') }}" -> :attr="t('key')"
  c = c.replace(/\b([:@]?[a-z-]+)="(\{\{\s*t\('([^']+)'\)\s*\}\}[^"]*)"/gi, (m, attr, val, key) => {
    if (attr.startsWith(':')) return m
    if (val.trim() === `{{ t('${key}') }}`) return `:${attr}="t('${key}')"`
    return m
  })
  // template ternary in mustache: ? '{{ t('key') }}'
  c = c.replace(/\?\s*'\{\{\s*t\('([^']+)'\)\s*\}\}'/g, "? t('$1')")
  c = c.replace(/:\s*'\{\{\s*t\('([^']+)'\)\s*\}\}'/g, ": t('$1')")
  return c
}

const dirs = [join(root, 'src')]
let count = 0
for (const dir of dirs) {
  for (const file of walk(dir)) {
    const before = readFileSync(file, 'utf8')
    const after = fix(before)
    if (after !== before) {
      writeFileSync(file, after, 'utf8')
      count++
      console.log('Fixed', file.replace(root + '\\', '').replace(root + '/', ''))
    }
  }
}
console.log('Done. Files fixed:', count)
