/** Voice recording helpers (browser-safe MIME + validation). */

export const MIN_VOICE_BYTES = 400
export const MIN_VOICE_MS = 400

const RECORDER_MIME_CANDIDATES = [
  'audio/webm;codecs=opus',
  'audio/webm',
  'audio/ogg;codecs=opus',
  'audio/mp4',
]

export function getPreferredRecorderMime() {
  if (typeof MediaRecorder === 'undefined') return ''
  for (const mime of RECORDER_MIME_CANDIDATES) {
    try {
      if (MediaRecorder.isTypeSupported(mime)) return mime
    } catch {
      /* ignore */
    }
  }
  /* Browser may still record with default type when isTypeSupported is false */
  return 'audio/webm'
}

export function extensionForMime(mime) {
  const m = (mime || '').toLowerCase()
  if (m.includes('mp4')) return '.m4a'
  if (m.includes('ogg')) return '.ogg'
  return '.webm'
}

export function validateVoiceBlob(blob, durationMs) {
  if (!blob || blob.size < MIN_VOICE_BYTES) {
    return 'التسجيل قصير جداً أو تالف. حاول مرة أخرى.'
  }
  if (durationMs != null && durationMs < MIN_VOICE_MS) {
    return 'التسجيل قصير جداً. اضغط مع الاستمرار ثم أرسل.'
  }
  return ''
}

export function normalizeVoiceMime(mime, filename = '') {
  const m = (mime || '').split(';')[0].trim().toLowerCase()
  const ext = (filename || '').toLowerCase()
  if (m.startsWith('audio/') && m !== 'application/octet-stream') return mime.split(';')[0]
  if (ext.endsWith('.mp4') || ext.endsWith('.m4a')) return 'audio/mp4'
  if (ext.endsWith('.ogg')) return 'audio/ogg'
  return 'audio/webm'
}
