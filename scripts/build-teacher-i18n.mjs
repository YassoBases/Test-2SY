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

const dirs = ['src/views/teacher', 'src/components/teacher']
const arabicRe = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF][\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\s،؛؟!.…—–\-:()«»0-9%]+/g
const englishUiRe = /(?:title|label|meta|subtitle|eyebrow|placeholder|hint|helper|action-label|aria-label)=["']([A-Za-z][^"']{2,80})["']/g

const allArabic = new Set()
const fileStrings = {}

for (const d of dirs) {
  for (const f of walk(d)) {
    const c = fs.readFileSync(f, 'utf8')
    const matches = [...c.matchAll(arabicRe)].map((m) => m[0].trim()).filter((s) => s.length >= 3)
    if (matches.length) {
      fileStrings[f] = [...new Set(matches)]
      matches.forEach((s) => allArabic.add(s))
    }
  }
}

const out = { totalUnique: allArabic.size, files: Object.keys(fileStrings).length, byFile: fileStrings }
fs.writeFileSync('scripts/teacher-strings-json.json', JSON.stringify(out, null, 2), 'utf8')
console.log('Unique Arabic strings:', allArabic.size, 'Files:', Object.keys(fileStrings).length)
