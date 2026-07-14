const res = await fetch('http://127.0.0.1:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'student@eduspark.sy', password: 'student123' }),
})
console.log('status', res.status)
console.log(await res.text())
