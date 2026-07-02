## Phase B — Placement Assessment (English) — Completion Report

### Architecture summary
- **Frontend**: Vue 3 + Vuetify placement flow at `src/views/student/languages/StudentLanguagePlacementView.vue` with autosave, step navigation, leave-guard, speaking recording upload, and an in-flow Results screen.
- **Backend**: FastAPI endpoints under `backend/app/api/language_student.py` powered by:
  - `backend/app/services/language_placement_service.py` (attempt lifecycle, autosave, submit, retake enforcement)
  - `backend/app/services/language_placement_scoring_service.py` (Phase B scoring + CEFR mapping, bottleneck overall)
  - `backend/app/services/language_learning_path_service.py` (weighted skill distribution 40/30/20/10 and `language_path_items` generation)
- **Persistence**: PostgreSQL tables (Phase A + Phase B migration additions).

### Database summary
#### Placement + assessment (Phase A migration `0008_language_learning_phase1`)
- `language_placement_sections`
- `language_placement_questions`
- `language_placement_attempts`
- `language_placement_responses`
- `language_assessments`
- `language_assessment_skill_scores`
- `language_learning_paths`
- `language_path_items`

#### Phase B additions (migration `0009_language_phase2`)
- **Certificates (foundation only)**: `language_certificates`
  - `certificate_status`, `verification_url` included
  - No PDF generation and no UI in Phase B.
- **Autosave integrity**: unique constraint
  - `uq_language_placement_attempt_question` on `(attempt_id, question_id)`

#### Live schema audit (current DB)
- `alembic_version`: `0009_language_phase2`
- Language tables present: **22** (all expected; none unknown under `language_%`).

### API summary
All routes are under router `backend/app/api/language_student.py` (prefix `/api/student/languages`) and registered via `backend/app/api/router.py`.

- **Access/paywall**
  - `GET /api/student/languages/access`
  - `GET /api/student/languages/product`
  - `POST /api/student/languages/subscribe`
- **Placement**
  - `POST /api/student/languages/placement/start`
  - `PUT /api/student/languages/placement/responses` (autosave)
  - `POST /api/student/languages/placement/speaking/upload`
    - Speaking recordings are stored as **`media_objects`**
    - Placement responses store **only** `media_object_id` reference.
  - `POST /api/student/languages/placement/submit` → creates:
    - `language_assessments` (overall = bottleneck)
    - `language_assessment_skill_scores` (per skill CEFR + raw metrics; `ai_evaluation_json=NULL`)
    - `language_learning_paths` + `language_path_items`

### Placement flow (end-to-end)
Student with active subscription:
1. Opens `/student/languages/placement`
2. Steps: Reading → Listening → Writing → Speaking
3. Autosave per question (`language_placement_responses`)
4. Submit:
   - Auto scoring:
     - Reading + Listening: MCQ scoring
     - Writing + Speaking: rule-based metrics stored in `raw_metrics_json`, no AI yet
   - Overall level:
     - `overall_level = min(skill levels)` (bottleneck)
   - Results screen shown

### Learning path flow (weighted distribution)
On submit, a new path is generated and previous path replaced for the same student/language.

Distribution across four skills based on ascending skill levels:
- 40% weakest
- 30% second weakest
- 20% third
- 10% strongest

Phase B path items are created with `(skill, level)` but without binding to content items yet (Phase C will surface this in the dashboard).

### Retake enforcement (90 days)
- After a successful placement submit:
  - `language_student_profiles.next_allowed_retake_date = placement_completed_at + 90 days`
- `POST /placement/start` blocks retakes until that timestamp with `HTTP 409` and a structured error body (`code=placement_retake_blocked`).
- UI disables “إعادة الاختبار” when `next_allowed_retake_date` is in the future.

### Certificate foundation
Implemented DB + model only:
- Table: `language_certificates`
- Fields include:
  - `certificate_level`, `certificate_number`, `verification_code`
  - `certificate_status`, `verification_url`
  - `issued_at`, `pdf_url`
No issuance workflow, PDF generation, or UI in Phase B.

### Known limitations (intentional in Phase B)
- **Listening audio assets**: questions reference URLs under `/language-assets/...` for portability. The repo currently does not include those mp3 files in `public/`, so playback will 404 until assets are added.
- **Speaking/Writing evaluation**: rule-based metrics only; `ai_evaluation_json` remains `NULL`.
- **Results deep link**: results are shown after submit; hub offers “عرض النتائج” by routing to placement with `?results=1` (Phase C will introduce a proper dashboard/results page).

### Phase C entry point (Learning Dashboard)
Implement `/student/languages/dashboard` and unlock it when:
- subscription active AND placement complete.

Phase C should:
- render the generated path (`language_learning_paths` + `language_path_items`)
- show per-skill CEFR + focus/strength
- attach path items to actual `language_content_items` and track progress using existing progress tables.

