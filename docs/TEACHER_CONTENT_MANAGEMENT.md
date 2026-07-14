# Teacher Content Management — Phase 2 Verification Report

## Supported file types

| Type | Accept | Max size | Validation |
|------|--------|----------|------------|
| PDF | `application/pdf`, `.pdf` | 50 MB | Client type + size; page count via pdfjs |
| Video | `video/*` | Server enforced | Browser file picker |
| Audio (voice profile) | `audio/*`, recorded WebM | Server enforced | Min 60s recording; ffprobe on backend |

## Preview behavior

| Media | Before save | After upload |
|-------|-------------|--------------|
| PDF | Canvas render of pages with navigation (`PdfPreviewCard`) | Same preview retained until page reload; post-upload status via AI timeline |
| Video | HTML5 `<video controls>` via blob URL (`VideoPreviewCard`) | Lesson list shows processing status; student view plays uploaded file |
| Audio | `<audio controls>` on recorded blob before upload (`VoiceRecorder`) | AI-generated preview via profile dialog; TTS preview after processing |

## Upload flow

### Standalone upload (`/teacher/upload`)

1. Teacher opens **مساحة عمل الدرس** (full-screen opaque workspace).
2. Fills lesson details (grade, subject, title, description).
3. Optionally attaches video and/or PDF — each with live preview.
4. Clicks **رفع الدرس** → confirm workspace (layered, opaque).
5. Files upload with real progress (`onUploadProgress`).
6. Toast: **تم رفع الدرس بنجاح**; if PDF attached: **بدأت معالجة الذكاء الاصطناعي**.
7. AI processing timeline polls until complete → toast **اكتملت المعالجة**.

### Course-scoped upload (grade detail → إضافة درس)

1. Dashboard/grade cards hidden (`v-show`) while workspace open.
2. Same preview panels for video/PDF.
3. Toast on success/failure; dialog closes on success.

### Voice profile (`/teacher/profile`)

1. Record or upload audio sample.
2. Preview recording **before** upload (playback, replace, delete).
3. Upload → toast success + AI processing info.
4. After processing: **معاينة** generates TTS sample with playback.

## Error handling

| Event | User feedback |
|-------|----------------|
| Upload success | Green toast (top) |
| AI processing started | Blue info toast |
| Upload failed | Red toast + inline `v-alert` |
| PDF invalid type/size | Inline error on drop zone |
| Validation incomplete | Warning alert before confirm |
| Voice upload failure | Red toast + inline alert |

## UX hardening (Part B)

- Replaced `glass-card` / transparent `v-dialog` with **`LessonWorkspaceScreen`** (fixed, opaque, z-index 2400).
- Background scrolling disabled while workspace open.
- Grade detail statistics/lesson cards hidden during add-lesson flow.
- Confirm step uses layered workspace (z-index 2500).
- Global **`AppToast`** mounted in `App.vue`.

## Files modified (Phase 2)

- `src/views/UploadLessonView.vue`
- `src/components/teacher/AddLessonDialog.vue`
- `src/components/teacher/LessonWorkspaceScreen.vue` (new)
- `src/components/teacher/VideoPreviewCard.vue` (new)
- `src/components/teacher/PdfPreviewCard.vue`
- `src/components/teacher/VoiceRecorder.vue`
- `src/components/teacher/TeacherVoiceProfileSection.vue`
- `src/components/common/UploadCard.vue`
- `src/components/common/AppToast.vue` (new)
- `src/composables/useToast.js` (new)
- `src/utils/pdfPreview.js` (new)
- `src/api/teacherCourses.js`
- `src/App.vue`
- `src/views/teacher/TeacherGradeDetailView.vue`

## Teacher lesson preview

### Routes

- `/teacher/courses/:courseId/lessons/:lessonId/preview` — media + metadata preview
- `/teacher/courses/:courseId/lessons/:lessonId/edit` — edit title/description

### API

- `GET /teacher/courses/{course_id}/lessons/{lesson_id}` — full preview payload
- `PATCH /teacher/courses/{course_id}/lessons/{lesson_id}` — update metadata

### Table actions

- **معاينة** — opens preview page
- **تعديل** — opens edit workspace (metadata + replace/remove media)
- **AI** — reprocess when status is draft/processing/error and lesson has PDF

### Lesson content editing

Teachers can edit from **Preview → Edit**:

- Title, description, visibility (`is_visible`)
- Replace or remove: video, PDF, audio
- Old files deleted from disk; asset rows updated
- PDF or video change on PDF lessons → status `draft` + `needs_reprocessing: true`
- Auto-schedules AI when PDF is replaced (optional manual reprocess from preview)

### API (content update)

- `POST /teacher/courses/{course_id}/lessons/{lesson_id}/update-content` — multipart
- `PATCH /teacher/courses/{course_id}/lessons/{lesson_id}` — JSON metadata only

### Additional files (content editing)

- `src/components/teacher/LessonContentEditorCard.vue`
- `src/views/teacher/TeacherLessonEditView.vue` — full edit workflow
- `backend/app/services/lesson_assets_service.py` — `remove_lesson_asset`
- `backend/app/services/teacher_courses_service.py` — `update_course_lesson_content`
