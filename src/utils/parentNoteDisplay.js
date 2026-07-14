const EMPTY_TITLE = 'بدون عنوان'
const EMPTY_BODY = 'لا يوجد نص في هذه الملاحظة.'

export function getParentNoteTitle(note) {
  const raw = note?.title ?? note?.note_title ?? ''
  return String(raw).trim()
}

export function getParentNoteBody(note) {
  const raw = note?.description ?? note?.body ?? note?.content ?? ''
  return String(raw).trim()
}

export function parentNoteDisplayTitle(note) {
  return getParentNoteTitle(note) || EMPTY_TITLE
}

export function parentNoteDisplayBody(note) {
  return getParentNoteBody(note) || EMPTY_BODY
}

export function parentNoteTitleIsEmpty(note) {
  return !getParentNoteTitle(note)
}

export function parentNoteBodyIsEmpty(note) {
  return !getParentNoteBody(note)
}
