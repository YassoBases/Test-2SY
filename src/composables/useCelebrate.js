// Celebration effects powered by canvas-confetti (realistic physics, shapes, performance).
import confetti from 'canvas-confetti'

const COLORS = ['#22d3ee', '#a78bfa', '#34d399', '#fbbf24', '#f472b6', '#60a5fa']

function _reduced() {
  return typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)')?.matches
}

/** A confetti burst for a win (passed lesson, aced review). */
export function celebrate(opts = {}) {
  if (_reduced()) return
  confetti({
    particleCount: opts.count ?? 120,
    spread: opts.spread ?? 75,
    startVelocity: opts.power ?? 42,
    origin: opts.origin ?? { x: 0.5, y: 0.42 },
    colors: COLORS,
    scalar: 1.05,
    ticks: 240,
    zIndex: 99999,
  })
}

/** A big multi-burst — side cannons + a center pop — for a milestone (perfect score, level up). */
export function celebrateBig() {
  if (_reduced()) return
  const end = Date.now() + 900
  ;(function frame() {
    confetti({ particleCount: 7, angle: 60, spread: 62, startVelocity: 55, origin: { x: 0, y: 0.75 }, colors: COLORS, zIndex: 99999 })
    confetti({ particleCount: 7, angle: 120, spread: 62, startVelocity: 55, origin: { x: 1, y: 0.75 }, colors: COLORS, zIndex: 99999 })
    if (Date.now() < end) requestAnimationFrame(frame)
  })()
  confetti({ particleCount: 160, spread: 110, startVelocity: 50, origin: { x: 0.5, y: 0.45 }, colors: COLORS, scalar: 1.1, zIndex: 99999 })
}

/** A gentle, continuous shimmer (e.g. while a level-up modal is open). Returns a stop() fn. */
export function celebrateShower(durationMs = 2200) {
  if (_reduced()) return () => {}
  const end = Date.now() + durationMs
  let running = true
  ;(function frame() {
    if (!running) return
    confetti({
      particleCount: 3,
      startVelocity: 0,
      ticks: 300,
      gravity: 0.45,
      spread: 360,
      origin: { x: Math.random(), y: -0.1 },
      colors: COLORS,
      scalar: 0.9,
      zIndex: 99999,
    })
    if (Date.now() < end) requestAnimationFrame(frame)
  })()
  return () => {
    running = false
  }
}
