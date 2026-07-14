# TEACHER-DESIGN-SYSTEM-1.0 — Foundation Report

**Status:** Foundation complete. No teacher pages migrated yet.  
**Build:** Passing (`npm run build`)

---

## Overview

A reusable Teacher Design System (TDS) was added as visual foundations only. All patterns consume existing `--em-*` tokens from `tokens.css`. Styles live in a single stylesheet; Vue components are thin wrappers with slots and props.

**Import path:** `src/components/teacher/design-system/index.js`  
**Stylesheet:** `src/assets/styles/teacher-design-system.css` (loaded in `main.js` after `teacher-typography.css`)

**Scope class:** `.tds-scope` — applied on every design-system component root for token aliases and morning-mode overrides.

---

## Reusable Components Created

### Card patterns

| Component | Purpose | Key classes |
|-----------|---------|-------------|
| `TeacherWorkspaceCard` | List/toolbar panels (lessons, quizzes, students) | `.tds-workspace`, `__toolbar`, `__body`, `__footer` |
| `TeacherSummaryCard` | Compact KPI tile (label + value + hint) | `.tds-summary-card` |
| `TeacherSummaryGrid` | Responsive grid for summary cards (2–5 columns) | `.tds-summary-grid` |
| `TeacherAnalyticsCard` | Larger metric with optional icon (dashboard/analytics) | `.tds-analytics-card` |
| `TeacherWarningCard` | Accent-border info / warning / error / success note | `.tds-warning-card` |
| `TeacherEmptyStateCard` | Centered empty state with icon, copy, CTA | `.tds-empty` |

### Shell patterns

| Component | Purpose | Key classes |
|-----------|---------|-------------|
| `TeacherDialog` | Standard modal shell (header, body, footer) | `.tds-dialog` |
| `TeacherForm` | Form root with optional `teacher-form-surface` | `.tds-form` |
| `TeacherFormSection` | Grouped form section with title + description | `.tds-form__section` |
| `TeacherFormField` | Field wrapper + optional hint slot | `.tds-form__field` |
| `TeacherFormHint` | Standalone helper note (reuses warning card) | `.tds-form__hint` |
| `TeacherTable` | Wrapped `v-table` with teacher data styling | `.tds-table-wrap`, `.tds-table` |
| `TeacherHero` | Page / panel hero (eyebrow, title, subtitle, actions) | `.tds-hero` |
| `TeacherButton` | Button hierarchy wrapper over `v-btn` | `.tds-btn` |
| `TeacherButtonGroup` | Horizontal button group alignment | `.tds-btn-group` |

### Button hierarchy (`TeacherButton`)

| Variant | Use | Maps to |
|---------|-----|---------|
| `primary` | Main CTA | `btn-glow` + flat secondary |
| `secondary` | Outlined emphasis | `btn-glow-outline` |
| `tonal` | Low emphasis filled | Vuetify tonal |
| `ghost` | Tertiary / cancel | Vuetify text |
| `danger` | Destructive | flat error |

---

## Typography Integration

`teacher-typography.css` was extended (not duplicated) to recognize TDS selectors:

- `.tds-form`, `.tds-dialog` — form surface token scope
- `.tds-hero__title`, `.tds-dialog__title` — page title weight
- `.tds-hero__subtitle`, `.tds-dialog__intro` — page description
- `.tds-form__section-title`, `.tds-form__section-desc` — section hierarchy

---

## Legacy Components That Can Be Removed (After Migration)

These become redundant once pages adopt TDS. **Do not delete until migration.**

| Legacy | Replace with |
|--------|----------------|
| `PageHeader.vue` (teacher pages) | `TeacherHero` (`variant="page"`) |
| `StatCard.vue` | `TeacherAnalyticsCard` |
| `TeacherQuizKpiStrip.vue` | `TeacherSummaryGrid` + `TeacherSummaryCard` |
| `glass-card` + scoped `.kpi-card` (Class Detail, Student Profile) | `TeacherSummaryGrid` / `TeacherAnalyticsCard` |
| Scoped `.edit-panel`, `.preview-panel`, `.results-panel`, `.question-editor-panel` | `TeacherWorkspaceCard` or `TeacherFormSection` |
| Scoped `.results-table-wrap` / `.results-table` | `TeacherTable` |
| `TeacherQuizDetailHero.vue` | `TeacherHero` (`variant="panel"`) |
| `EditCourseDialog.vue` shell | `TeacherDialog` + `TeacherForm` + `TeacherFormSection` |
| Quiz create sheet (`glass-card` dialog in `TeacherQuizzesView`) | `TeacherDialog` + list pattern |
| `TeacherQuizPreviewDialog.vue` shell | `TeacherDialog` |
| `EmptyState.vue` / `AppEmptyState.vue` (teacher contexts) | `TeacherEmptyStateCard` |
| `teacher-quiz-empty`, `teacher-classes-empty` CSS blocks | `TeacherEmptyStateCard` |
| Inline `text-caption` helper paragraphs | `TeacherFormHint` / `TeacherWarningCard` |
| Ad-hoc `variant="tonal"` header buttons | `TeacherButton` (`ghost` / `tonal` / `primary`) |
| `create-course-field-hint` / `add-lesson-field-helper` (after form migration) | `TeacherFormHint` |

**Keep for now (student/shared or not yet superseded):**

- `AppCard`, `AppButton`, `AppSection`, `AppEmptyState` — shared app layer
- `CreateCourseDialog.vue` — migrate shell to TDS, keep business logic
- `AddLessonDialog.vue` — same
- Domain cards: `TeacherClassWorkspaceCard`, `TeacherQuizWorkspaceCard`, `TeacherLessonPremiumCard` — content-specific; wrap body in `TeacherWorkspaceCard` later

---

## Pages Ready for Migration

Ordered by impact and dependency.

### Tier 1 — High duplication, clear TDS mapping

| Page / surface | TDS patterns to adopt |
|----------------|----------------------|
| **Analytics** (`TeacherAnalyticsView`) | `TeacherHero`, `TeacherSummaryGrid`, `TeacherAnalyticsCard`, `TeacherTable` |
| **Students** (`TeacherStudentsView`) | `TeacherHero`, `TeacherWorkspaceCard`, `TeacherTable`, `TeacherButton` |
| **Student Profile** (`TeacherStudentProfileView`) | `TeacherHero`, `TeacherSummaryGrid`, `TeacherAnalyticsCard`, `TeacherTable` |
| **Quiz Results** (`TeacherQuizResultsView`) | `TeacherHero`, `TeacherSummaryGrid`, `TeacherWorkspaceCard`, `TeacherTable` |
| **Edit Class** (`EditCourseDialog`) | `TeacherDialog`, `TeacherForm`, `TeacherFormSection`, `TeacherFormField`, `TeacherButtonGroup` |

### Tier 2 — Editor / preview shells

| Page / surface | TDS patterns to adopt |
|----------------|----------------------|
| **Lesson Edit** (`TeacherLessonEditView`) | `TeacherHero`, `TeacherForm`, `TeacherFormSection`, `TeacherWarningCard`, `TeacherButtonGroup` |
| **Lesson Preview** (`TeacherLessonPreviewView`) | `TeacherHero`, `TeacherWorkspaceCard`, `TeacherButtonGroup` |
| **Quiz Builder** — question editor (`TeacherQuizBuilderView`) | `TeacherHero` (panel), `TeacherForm`, `TeacherFormSection`, `TeacherButtonGroup` |
| **Quiz Builder** — main | `TeacherHero` (panel), `TeacherWarningCard` |

### Tier 3 — Already modern; thin migration

| Page / surface | TDS patterns to adopt |
|----------------|----------------------|
| **Classes** (`TeacherGradesView`) | `TeacherHero` (already has PageHeader), `TeacherEmptyStateCard` |
| **Quizzes** (`TeacherQuizzesView`) | `TeacherHero`, `TeacherSummaryGrid`, `TeacherDialog` (create sheet), `TeacherEmptyStateCard` |
| **Class Detail** (`TeacherGradeDetailView`) | `TeacherHero`, `TeacherSummaryGrid` (replace KPI wall), `TeacherWorkspaceCard` (already similar CSS) |
| **Profile** (`TeacherProfileView`) | `TeacherHero`, `TeacherForm`, `TeacherFormSection`, `TeacherFormHint` |
| **Settings** (`UserSettingsView`) | `TeacherHero`, `TeacherWorkspaceCard` for sections |
| **Dashboard** (`TeacherDashboardView`) | `TeacherSummaryCard`, `TeacherAnalyticsCard` for metrics (optional) |

### Tier 4 — Deferred / special layout

| Page / surface | Notes |
|----------------|-------|
| **Messages** (`MessagesView`) | WhatsApp shell; only adopt `TeacherButton` / input tokens |
| **Create Class** / **Add Lesson** | Migrate dialog/workspace shell to TDS; keep section content |
| **Global Lessons** (`TeacherLessonsView`) | `TeacherWorkspaceCard` + `TeacherEmptyStateCard` |
| **Setup** (`TeacherSetupView`) | Full form migration |

---

## CSS Classes for Migration (without components)

When a full component swap is unnecessary, use these global classes inside `.tds-scope`:

- Table cells: `.tds-table__cell-muted`, `.tds-table__cell-strong`
- Summary layout: `.tds-summary-grid`, `.tds-summary-grid--{3,4,5}`

---

## What Was Not Changed

- No teacher page templates modified
- No API, routing, or business logic touched
- No legacy CSS removed (migration phase follows)
- `CreateCourseDialog` / `AddLessonDialog` still use their existing class names

---

## Next Step (TEACHER-DESIGN-SYSTEM-1.1)

1. Migrate **Edit Class** dialog (smallest complete vertical slice)
2. Migrate **Analytics** + **Students** tables (validates `TeacherTable`)
3. Collapse Class Detail KPI wall into `TeacherSummaryGrid`
4. Replace editor panels (`edit-panel`, `question-editor-panel`) with `TeacherFormSection`
