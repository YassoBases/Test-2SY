import fs from 'fs'
import path from 'path'

function walk(dir) {
  const results = []
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) results.push(...walk(p))
    else if (e.name.endsWith('.vue')) results.push(p)
  }
  return results
}

const arabicRe = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF][\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\s،؛؟!.…—–\-:()«»0-9%]+/g

const dirs = ['src/views/parent', 'src/components/parent']
const out = []
for (const d of dirs) {
  for (const f of walk(d)) {
    const c = fs.readFileSync(f, 'utf8')
    const matches = [...new Set([...c.matchAll(arabicRe)].map((m) => m[0].trim()).filter((s) => s.length >= 3))]
    if (matches.length) {
      out.push({ file: f, strings: matches })
    }
  }
}
console.log(JSON.stringify(out, null, 2))
