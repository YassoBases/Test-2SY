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
const used = new Set()
for (const dir of dirs) {
  for (const file of walk(dir)) {
    const c = fs.readFileSync(file, 'utf8')
    let m
    while ((m = keyRe.exec(c))) used.add(m[1])
  }
}

const missing = [...used].filter((k) => get(en, k) === undefined).sort()
console.log('Used keys:', used.size)
console.log('Missing keys:', missing.length)
missing.forEach((k) => console.log(' - teacher.' + k))
