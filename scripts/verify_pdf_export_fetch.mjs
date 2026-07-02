/** Verify PDF export fetch path returns a valid blob (simulates browser export). */
import { createHmac } from 'node:crypto'
import { writeFileSync } from 'node:fs'

const secret = process.env.JWT_SECRET || 'change-me-to-a-long-random-secret'
const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url')
const payload = Buffer.from(
  JSON.stringify({ sub: '23', role: 'parent', exp: Math.floor(Date.now() / 1000) + 3600, sid: '275' }),
).toString('base64url')
const sig = createHmac('sha256', secret).update(`${header}.${payload}`).digest('base64url')
const token = `${header}.${payload}.${sig}`

const url = 'http://127.0.0.1:5173/api/parent/historical-report/export?format=pdf&period=this_week&student_id=5'
const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } })
const buf = await res.arrayBuffer()
const ok = res.ok && buf.byteLength > 1000 && new Uint8Array(buf)[0] === 0x25 // %PDF

console.log(
  JSON.stringify(
    {
      status: res.status,
      bytes: buf.byteLength,
      contentType: res.headers.get('content-type'),
      pdfMagic: ok,
      pass: ok,
    },
    null,
    2,
  ),
)

if (ok) writeFileSync('scripts/_verify_export.pdf', Buffer.from(buf))
process.exit(ok ? 0 : 1)
