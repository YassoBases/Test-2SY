/** Client-side thumbnail + duration from a local video File. */

export function extractVideoFileMetadata(file) {
  if (!file || typeof document === 'undefined') {
    return Promise.resolve({ duration: 0, thumbnail: null })
  }

  return new Promise((resolve) => {
    const objectUrl = URL.createObjectURL(file)
    const video = document.createElement('video')
    video.preload = 'metadata'
    video.muted = true
    video.playsInline = true

    const cleanup = () => {
      video.removeAttribute('src')
      video.load()
      URL.revokeObjectURL(objectUrl)
    }

    const finish = (result) => {
      cleanup()
      resolve(result)
    }

    video.addEventListener('error', () => finish({ duration: 0, thumbnail: null }), { once: true })

    video.addEventListener(
      'loadedmetadata',
      () => {
        const duration = Number.isFinite(video.duration) ? video.duration : 0
        const seekTo = duration > 0 ? Math.min(1, duration * 0.08) : 0

        const captureFrame = () => {
          try {
            const canvas = document.createElement('canvas')
            canvas.width = 320
            canvas.height = 180
            const ctx = canvas.getContext('2d')
            if (!ctx) {
              finish({ duration, thumbnail: null })
              return
            }
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
            finish({ duration, thumbnail: canvas.toDataURL('image/jpeg', 0.82) })
          } catch {
            finish({ duration, thumbnail: null })
          }
        }

        if (seekTo > 0) {
          video.addEventListener('seeked', captureFrame, { once: true })
          video.currentTime = seekTo
        } else {
          captureFrame()
        }
      },
      { once: true },
    )

    video.src = objectUrl
  })
}
