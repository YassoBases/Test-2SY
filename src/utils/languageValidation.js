/** Shared language activity validation (mirrors backend language_validation.py). */

export function countWritingWords(text) {
  return (String(text || '').match(/[A-Za-z']+/g) || []).length
}

export function countWritingSentences(text) {
  const parts = String(text || '').split(/[.!?]+/)
  return parts.filter((p) => p.trim()).length
}

export function minWordsRequiredMessage(minWords) {
  return `Minimum ${Number(minWords)} words required.`
}

export function minSecondsRequiredMessage(minSeconds, actualSeconds = null) {
  const base = `Minimum ${Number(minSeconds)} seconds required.`
  if (actualSeconds != null && Number.isFinite(Number(actualSeconds))) {
    return `${base} Your recording was ${Number(actualSeconds)}s.`
  }
  return base
}

export function validateWritingText(text, { minWords = 20, minSentences = 0 } = {}) {
  const normalized = String(text || '').trim()
  if (!normalized) {
    return { ok: false, message: 'النص مطلوب' }
  }
  const wordCount = countWritingWords(normalized)
  const sentenceCount = countWritingSentences(normalized)
  if (wordCount < minWords) {
    return { ok: false, message: minWordsRequiredMessage(minWords), wordCount, sentenceCount }
  }
  if (minSentences > 0 && sentenceCount < minSentences) {
    return {
      ok: false,
      message: `Minimum ${minSentences} sentences required.`,
      wordCount,
      sentenceCount,
    }
  }
  return { ok: true, wordCount, sentenceCount }
}
