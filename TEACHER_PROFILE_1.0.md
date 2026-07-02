# TEACHER-PROFILE-1.0 — AI Teacher Onboarding Experience

**Status:** Implemented  
**Build:** `npm run build` — passed  
**Scope:** Premium onboarding section at top of Teacher Profile — no API, backend, or form changes.

---

## Objective

When a teacher opens **الملف الشخصي**, they immediately see how EduSpark + Gemini work before editing any settings. The section teaches the **workflow** (why → what happens next), not a feature list.

---

## Placement

```
PageHeader (الملف الشخصي)
    ↓
🚀 TeacherProfileOnboardingWorkflow  ← NEW (always visible, static)
    ↓
Alerts / profile forms (unchanged)
```

Onboarding renders **outside** the loading skeleton so it appears on first paint.

---

## Component

| File | Role |
|------|------|
| `src/components/teacher/profile/TeacherProfileOnboardingWorkflow.vue` | Onboarding card + pipeline + 5 steps |
| `src/views/teacher/TeacherProfileView.vue` | Imports and mounts workflow below header |

### TDS usage

| Element | Component |
|---------|-----------|
| Card shell | `TeacherWorkspaceCard` |
| Footer hint | `TeacherFormHint` (one line) |
| Icons | `v-icon` inside TDS-scoped layout |

No glass cards, no custom card primitives, no new APIs.

---

## Content structure

### Card header

- **Title:** 🚀 ابدأ رحلتك كمعلم ذكي  
- **Subtitle:** EduSpark + Gemini personalization intro (via `meta` prop)

### Data pipeline (visual)

```
المعلم  →  Gemini  →  الطلاب
```

- Horizontal on `≥640px`, vertical on mobile  
- Subtle chevron animation (`prefers-reduced-motion` respected)

### Five workflow steps

| # | Step | Focus (what happens after) |
|---|------|---------------------------|
| 1 | 👤 هوية المعلم | Gemini learns teaching style & communication |
| 2 | 🎤 صوتك | AI narrates summaries in teacher's voice |
| 3 | 🎥 الفيديو | EduSpark analyzes explanation style from video/YouTube |
| 4 | 📄 PDF | Gemini extracts concepts for teaching, Q&A, quizzes |
| 5 | 🚀 إنشاء الدروس | Smart assistant ready to co-build content |

Each step: emoji + title + **one short sentence**. Steps connected by animated vertical connector.

### UX rule applied

Every step answers **“What happens after I upload this?”** — not only what to upload.

---

## Out of scope (next phases)

- Voice section redesign  
- Teacher Identity redesign  
- PDF / Video upload UX  
- Profile form changes  
- Backend / routing / API changes  

---

## Verification

1. Open `/teacher/profile`  
2. Onboarding card appears immediately below page header  
3. Pipeline shows معلم → Gemini → طلاب  
4. Five steps visible with connectors  
5. Existing profile forms unchanged below  
