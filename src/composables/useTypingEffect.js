import { onMounted, onUnmounted, ref } from 'vue'

/**
 * Premium typewriter effect — types, pauses, deletes, cycles phrases.
 */
export function useTypingEffect(phrases, options = {}) {
  const {
    typeSpeed = 55,
    deleteSpeed = 32,
    pauseMs = 2200,
    startDelay = 600,
  } = options

  const displayText = ref('')
  const phraseIndex = ref(0)
  let timeoutId = null
  let charIndex = 0
  let deleting = false

  function clearTimer() {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
  }

  function tick() {
    const current = phrases[phraseIndex.value] || ''

    if (!deleting) {
      charIndex += 1
      displayText.value = current.slice(0, charIndex)
      if (charIndex >= current.length) {
        deleting = true
        timeoutId = setTimeout(tick, pauseMs)
        return
      }
      timeoutId = setTimeout(tick, typeSpeed)
      return
    }

    charIndex -= 1
    displayText.value = current.slice(0, charIndex)
    if (charIndex <= 0) {
      deleting = false
      phraseIndex.value = (phraseIndex.value + 1) % phrases.length
      timeoutId = setTimeout(tick, typeSpeed + 120)
      return
    }
    timeoutId = setTimeout(tick, deleteSpeed)
  }

  onMounted(() => {
    timeoutId = setTimeout(tick, startDelay)
  })

  onUnmounted(clearTimer)

  return { displayText, phraseIndex }
}
