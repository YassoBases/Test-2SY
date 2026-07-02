import { countPdfPagesFromFile } from './pdfPageCount.js'

let pdfjsModule = null

async function getPdfJs() {
  if (!pdfjsModule) {
    pdfjsModule = await import('pdfjs-dist')
    const { default: workerSrc } = await import('pdfjs-dist/build/pdf.worker.min.mjs?url')
    pdfjsModule.GlobalWorkerOptions.workerSrc = workerSrc
  }
  return pdfjsModule
}

/**
 * Render a PDF page to a canvas element.
 * @param {File | Blob} file
 * @param {HTMLCanvasElement} canvas
 * @param {number} pageNumber 1-based
 */
export async function renderPdfPageToCanvas(file, canvas, pageNumber = 1) {
  const pdfjs = await getPdfJs()
  const buf = await file.arrayBuffer()
  const pdf = await pdfjs.getDocument({ data: buf }).promise
  const page = await pdf.getPage(Math.min(Math.max(1, pageNumber), pdf.numPages))
  const viewport = page.getViewport({ scale: 1 })
  const maxWidth = 640
  const scale = Math.min(1.5, maxWidth / viewport.width)
  const scaled = page.getViewport({ scale })

  const ctx = canvas.getContext('2d')
  canvas.width = scaled.width
  canvas.height = scaled.height
  await page.render({ canvasContext: ctx, viewport: scaled }).promise
  return pdf.numPages
}

export { countPdfPagesFromFile }
