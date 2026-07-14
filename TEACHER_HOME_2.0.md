# TEACHER-HOME-2.0 — Dashboard as Action Center

**Status:** Implemented  
**Build:** `npm run build` — passed  
**Scope:** Dashboard hierarchy, sidebar navigation, TDS task cards — no API, routing, or backend changes.

---

## New dashboard hierarchy

Top → bottom on `/teacher/dashboard`:

| # | Section | Component | Purpose |
|---|---------|-----------|---------|
| 1 | Hero | `TeacherDashboardHero` | Greeting + primary CTAs (الصفوف / الرسائل) |
| 2 | **إجراءات العمل** | `TeacherQuickActions` | إنشاء صف، إضافة درس، إنشاء كويز، إرسال رسالة |
| 3 | **يحتاج إجراء الآن** | `TeacherDashboardTaskSection` | Highest-priority actionable tasks |
| 4 | **مهام اليوم** | `TeacherDashboardTaskSection` | Medium-priority follow-ups |
| 5 | **ملخص التدريس** | `TeacherOverviewSection` | KPI reference cards |
| 6 | Classes + Activity | `TeacherClassesSection` + `TeacherActivitySection` | Workspace context (unchanged content, lower on page) |

### Previous order (for reference)

Hero → Priorities (mixed) → Quick Actions → Classes/Activity → KPIs

### Sections moved

- **KPIs** (`TeacherOverviewSection`) moved from last to **after Quick Actions**
- **Quick Actions** moved to **immediately below task lists**
- **Priorities** split into two tiers:
  - **يحتاج إجراء الآن** — urgent / blocking work
  - **مهم اليوم** — follow-up / monitoring

---

## Sidebar change

**Removed:** standalone `الطلاب` item from `teacherNavItems` in `src/config/navigation.js`.

**Students access path:**

```
الصفوف → اختر الصف → لوحة الطلاب (TeacherStudentSummaryPanel)
```

**Verified:**

| Area | Change |
|------|--------|
| `src/config/navigation.js` | Students nav item removed |
| `src/layouts/TeacherLayout.vue` | Unchanged — renders `teacherNavItems` from config |
| `src/router/index.js` | Route `/teacher/students` **kept** (no routing change) — reachable via class detail / deep links |
| `TeacherClassWorkspaceCard.vue` | “الطلاب” link now points to class detail (`coursePath`) instead of global students list |
| `TeacherQuickActions.vue` | Students shortcut removed |
| `TeacherDashboardHero.vue` | Secondary CTA changed from الطلاب → الرسائل |

---

## Action tiers (existing data only)

### يحتاج إجراء الآن

| Signal | Source | Action |
|--------|--------|--------|
| Unread messages | `fetchConversationsUnreadCount()` | فتح الرسائل |
| Quiz attempts awaiting review | `attempt_count` per quiz (`fetchTeacherManualQuizzes`) | تصحيح الآن |
| AI processing failed | Lesson `status === 'error'` (`fetchTeacherCourseDetail`) | إعادة المعالجة |
| Class with no lessons | `lesson_count === 0` (`fetchTeacherGrades`) | إضافة درس |
| Unpublished class | `is_published === false` | فتح الصف |
| Unpublished quizzes | `unpublished_quizzes` from quiz list | فتح الكويز |
| Draft lessons | Lesson `status === 'draft'` | تعديل الدرس |

### مهم اليوم

| Signal | Source | Action |
|--------|--------|--------|
| Expiring subscriptions | `subscription_summary.expiring_soon` + per-course `analytics.expiring_soon` | فتح الصف |
| Expired subscriptions | `subscription_summary.expired_subscribers` + per-course analytics | فتح الصف |
| Low lesson completion | `completion_percent < 40%` with subscribers | متابعة الصف |
| Inactive students | `last_activity_at` older than 14 days (`fetchTeacherCourseDetail` students) | عرض الطلاب |
| Upcoming quiz | Published quiz with `due_at` within 7 days | فتح الكويز |

Empty sections use `TeacherEmptyStateCard`.

---

## Components reused (TDS)

| Component | Usage |
|-----------|--------|
| `TeacherWarningCard` | Task title + explanation with urgency variant (`error` / `warning` / `info`) |
| `TeacherButton` | Primary action per task card |
| `TeacherEmptyStateCard` | Empty state when no tasks in a tier |
| `TeacherStatCard` | KPI values in overview |
| `TeacherSummaryGrid` | KPI layout (2–4 columns) |

**New (composition only):** `TeacherDashboardTaskSection.vue` — wraps `AppSection` + TDS task list pattern.

**Legacy retained (unused on dashboard):** `TeacherPrioritiesSection.vue` — not removed from repo; dashboard no longer imports it.

---

## Files changed

- `src/config/navigation.js`
- `src/views/TeacherDashboardView.vue`
- `src/components/teacher/dashboard/TeacherDashboardTaskSection.vue` *(new)*
- `src/components/teacher/dashboard/TeacherOverviewSection.vue`
- `src/components/teacher/dashboard/TeacherQuickActions.vue`
- `src/components/teacher/dashboard/TeacherDashboardHero.vue`
- `src/components/teacher/classes/TeacherClassWorkspaceCard.vue`
- `src/assets/styles/teacher-home.css`

---

## Data loading (no new APIs)

Dashboard `loadDashboard()` parallel fetch:

1. `fetchTeacherOverview()` — KPIs, activity, subscription summary  
2. `fetchTeacherGrades()` — course rows  
3. `fetchConversationsUnreadCount()` — unread messages  

Per course enrichment (existing endpoints):

- `fetchTeacherManualQuizzes(courseId)` — attempts, drafts, due dates  
- `fetchTeacherCourseDetail(courseId)` — lesson statuses, students activity, per-class subscription counts  

---

## No backend / API / routing changes

- No new endpoints or schema fields  
- `/teacher/students` route remains for bookmarks and analytics deep links  
- Visual hierarchy and navigation entry points updated only
