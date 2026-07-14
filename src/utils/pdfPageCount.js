/**
 * Client-side PDF page count via pdfjs-dist v6.
 * Package main: build/pdf.mjs — there is no pdfjs-dist/build/pdf path.
 */

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
 * @param {ArrayBuffer | Uint8Array} data
 * @returns {Promise<number>}
 */
export async function countPdfPages(data) {
  const pdfjs = await getPdfJs()
  const pdf = await pdfjs.getDocument({ data }).promise
  return pdf.numPages
}

/**
 * @param {File | Blob} file
 * @returns {Promise<number>}
 */
export async function countPdfPagesFromFile(file) {
  const buf = await file.arrayBuffer()
  return countPdfPages(buf)
}
