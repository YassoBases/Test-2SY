/** Convert erroneous ${t()} in Vue templates back to {{ t() }}. */
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

function fixTemplatePart(part) {
  return part.replace(/\$\{t\('([^']+)'\)(?:,\s*\{[^}]+\})?\)\}/g, (_, key) => `{{ t('${key}') }}`)
}

for (const dir of [join(root, 'src/views/student'), join(root, 'src/components/student')]) {
  for (const file of walk(dir)) {
    let c = readFileSync(file, 'utf8')
    const before = c
    const scriptIdx = c.indexOf('<script')
    if (scriptIdx === -1) {
      c = fixTemplatePart(c)
    } else {
      c = fixTemplatePart(c.slice(0, scriptIdx)) + c.slice(scriptIdx)
    }
    // fix broken backtick emits
    c = c.replace(/\$emit\(`(\w+)`\)/g, "$emit('$1')")
    c = c.replace(/from `vue`/g, "from 'vue'")
    c = c.replace(/:title="t\('([^']+)`\)"/g, ":title=\"t('$1')\"")
    c = c.replace(/`success' : 'warning`/g, "submitResult.passed ? 'success' : 'warning'")
    if (c !== before) {
      writeFileSync(file, c, 'utf8')
      console.log('Fixed', file.replace(root + '\\', ''))
    }
  }
}
console.log('Done')
