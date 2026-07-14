import fs from 'fs'
import path from 'path'

const ROOT = path.resolve(import.meta.dirname, '..')
const en = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/locales/en/teacher.json'), 'utf8'))

function get(obj, keyPath) {
  return keyPath.split('.').reduce((o, k) => (o && typeof o === 'object' ? o[k] : undefined), obj)
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

const dirs = [
  path.join(ROOT, 'src/views/teacher'),
  path.join(ROOT, 'src/components/teacher'),
]
const keyRe = /(?:\$t|[^a-zA-Z]t)\(\s*['"]teacher\.([^'"]+)['"]/g
const used = new Map()
for (const dir of dirs) {
  for (const file of walk(dir)) {
    const c = fs.readFileSync(file, 'utf8')
    const lines = c.split('\n')
    lines.forEach((line, i) => {
      let m
      const re = /(?:\$t|[^a-zA-Z]t)\(\s*['"]teacher\.([^'"]+)['"]/g
      while ((m = re.exec(line))) {
        const k = m[1]
        if (!used.has(k)) used.set(k, [])
        used.get(k).push({ file: path.relative(ROOT, file), line: i + 1, text: line.trim() })
      }
    })
  }
}

const missing = [...used.keys()].filter((k) => get(en, k) === undefined).sort()
for (const k of missing) {
  console.log('\n=== teacher.' + k + ' ===')
  used.get(k).slice(0, 3).forEach((u) => console.log(u.file + ':' + u.line + ' ' + u.text))
}
