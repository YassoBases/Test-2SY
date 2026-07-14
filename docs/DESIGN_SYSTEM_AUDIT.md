# EduSpark Design System Audit — Phase UX

**Date:** 2026-06-02  
**Scope:** Consistency polish (no rebrand). Dark theme, purple/cyan EduSpark identity preserved.

---

## Executive summary

The platform already had strong foundations (`glass-card`, `btn-glow`, `StatCard`, `PageHeader`, sidebar nav fix, toast system). Phase UX adds a **single design-system layer** (`design-system.css` + shared components) and rolls it into high-traffic teacher/student/parent surfaces.

| Area | Before | After |
|------|--------|--------|
| Sidebar active state | Multiple items on `/student/dashboard` | Exactly one (`navActive.js` + `SidebarNavList`) |
| Empty lists | Ad-hoc icons + plain text per view | `EmptyState` + `emptyStatePresets.js` |
| Loading | Mixed spinners / raw skeletons | `LoadingState` (cards / table / inline) |
| Cards | `glass-card` only | + `content-card`, `message-card`, `ContentCard.vue` |
| Modals | Global Vuetify overrides only | + `edu-dialog-card`, `EduDialog.vue` |
| Buttons | `btn-glow` / tonal scattered | `em-btn--*` aliases (primary/secondary/danger/ghost) |
| Toasts | Styled in `main.css` | Unchanged API; tokens aligned in design-system |
| Page motion | Student layout fade | Student + Teacher + Parent layouts |

---

## 1. Navigation consistency ✅

- **Root cause (student):** Hash links shared path `/student/dashboard`; Vuetify marked all as active.
- **Fix:** `src/utils/navActive.js`, `src/components/layout/SidebarNavList.vue`, `src/assets/styles/sidebar-nav.css`
- **Roles:** Student, Teacher (`matchChildren` on grades/students/quizzes/languages), Parent (dashboard vs `#activity`)

---

## 2. Card system ✅

| Class / component | Use |
|-------------------|-----|
| `glass-card` + `kpi-card` | Dashboard KPIs (existing) |
| `stat-card` + `StatCard.vue` | Analytics / teacher stats |
| `content-card` + `ContentCard.vue` | Panels, lists, forms |
| `message-card` | Conversation rows (CSS ready) |
| `glass-card--solid` | Opaque readable panels |

**Tokens:** `--em-radius-sm/md/lg`, `--em-shadow-card`, `--em-space-*`

---

## 3. Modal & overlay system ✅

- Scrim: `--em-overlay-scrim` (opaque, no bleed-through)
- Dialog body: `--em-glass-solid` via `.v-dialog` overrides (main.css) + `.edu-dialog-card`
- Z-index scale: `--em-z-modal` (2400), `--em-z-toast` (2600)
- **Component:** `EduDialog.vue` — title bar, body, footer actions

**Adoption:** New dialogs should use `EduDialog` or `class="edu-dialog-card"` on `v-card`.

---

## 4. Button system ✅

| Class | Role |
|-------|------|
| `em-btn em-btn--primary` / `btn-glow` | Primary CTA |
| `em-btn em-btn--secondary` / `btn-glow-outline` | Secondary |
| `em-btn em-btn--danger` | Destructive |
| `em-btn em-btn--ghost` | Low emphasis |
| `:disabled` | 42% opacity, no lift |

Legacy `btn-glow` remains valid (aliased).

---

## 5. Empty states ✅

**Component:** `EmptyState.vue` with `preset` prop  
**Presets:** `src/constants/emptyStatePresets.js`

| Preset | Applied in |
|--------|------------|
| `messages` | Messages UI (`MessagesEmptyState` aligned) |
| `lessons` | `TeacherLessonsView` |
| `quizzes` | `TeacherQuizzesView` |
| `students` / `studentsFiltered` | `TeacherStudentsView` |
| `subscriptions` | `StudentSubscriptionsView` |
| `courses` | `StudentDashboardView` |
| `notifications` | `NotificationBell` panel |

---

## 6. Loading states ✅

**Component:** `LoadingState.vue`

| Variant | Use |
|---------|-----|
| `cards` | Grid pages (dashboard, subscriptions, quizzes) |
| `table` | Table pages (students, lessons) |
| `inline` | Full-page fetch (course view) |
| `bar` | Optional top progress |

Skeleton styling: `.em-skeleton` (brand shimmer, solid background).

---

## 7. Notification system ✅

- **Toast:** `useToast.js` + `AppToast.vue` — success/error/warning/info colors & `toast-enter` animation (main.css)
- **Bell panel:** Opaque `notification-panel`, structured empty state

---

## 8. Forms ✅

Global (main.css): opaque `v-field` backgrounds, focused outline glow.  
Design-system additions:

- `.em-form-section`, `.em-field-label`, `.em-field-label--required`
- `.em-field-hint`, `.em-field-error`
- `.em-upload-zone` (aligned with existing `.upload-zone`)

---

## 9. Visual hierarchy ✅

Existing + reinforced:

- `PageHeader` + `.page-header--panel`
- `.section-block`, `.section-block__title`, `.section-block__subtitle`
- `.page-stack` gap utility
- `.page-container` max-width 1280px

---

## 10. Animation & microinteractions ✅

| Interaction | Implementation |
|-------------|----------------|
| Page transition | `.fade-*` on Student/Teacher/Parent layouts |
| Card hover | `.eduspark-card-hover`, `.content-card--interactive`, `.kpi-card:hover` |
| Sidebar | Active border + glow; hover ≠ active |
| Toast | `toast-enter` keyframes |
| Buttons | `translateY` on hover (main.css + em-btn) |
| Empty state | `slide-up`, `icon-float` |
| Messages | Existing `messages-chat.css` |

---

## Files added

- `src/assets/styles/design-system.css`
- `src/utils/navActive.js` (navigation)
- `src/components/layout/SidebarNavList.vue`
- `src/components/common/ContentCard.vue`
- `src/components/common/LoadingState.vue`
- `src/components/common/EduDialog.vue`
- `src/constants/emptyStatePresets.js`
- `docs/DESIGN_SYSTEM_AUDIT.md`

## Files updated (representative)

- `src/main.js` — imports design-system + sidebar-nav
- `src/components/common/EmptyState.vue` — presets
- `src/config/navigation.js` — matchChildren
- Layout sidebars → `SidebarNavList`
- Views: `StudentDashboardView`, `StudentSubscriptionsView`, `StudentCourseView`, `TeacherStudentsView`, `TeacherLessonsView`, `TeacherQuizzesView`
- `NotificationBell.vue`, `MessagesEmptyState.vue`

---

## Verification checklist

1. `npm run build` — must pass
2. Student sidebar: one active item per route/hash
3. Teacher: students/grades/quizzes empty + loading states
4. Open dialog — no transparent bleed-through
5. Trigger toast success/error — consistent colors
6. Notification bell empty — icon + copy

---

## Follow-up (optional, not blocking)

- Migrate remaining dialogs to `EduDialog`
- Apply `message-card` class in `ConversationListItem`
- Replace remaining `v-progress-circular` page loaders with `LoadingState`
- «دروسي» and «تقدّمي» removed from student sidebar; `#lessons` / `#progress` redirect to Smart Planner; `#courses` is the student hub (دوراتي)
