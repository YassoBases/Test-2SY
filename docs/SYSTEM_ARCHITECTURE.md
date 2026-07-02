# EduSpark — System Architecture

**Stack:** Vue 3 + Vuetify 3 (SPA) · FastAPI (async) · PostgreSQL · optional Ollama/Gemini · local/S3 media  
**API base:** `/api` (see `settings.API_PREFIX`)  
**Data model reference:** [ERD.md](./ERD.md) · [ERD.dbml](./ERD.dbml)  
**API reference:** [API_ARCHITECTURE.md](./API_ARCHITECTURE.md)

---

## High-level overview

```mermaid
flowchart TB
  subgraph Client["Browser (Vue 3 SPA)"]
    Views[Views / Components]
    Router[Vue Router]
    API_Client[Axios api client]
    Session[localStorage session]
  end

  subgraph Backend["FastAPI Application"]
    API[API Routers]
    Deps[Auth deps / RBAC]
    Services[Domain services]
    Hooks[integration_hooks]
    BG[Background: subscription checker]
  end

  subgraph Data["PostgreSQL"]
    Tables[(47 tables)]
    Rollups[Analytics rollups]
  end

  subgraph AI_Stack["AI & Media (optional)"]
    PDF[pdf_service / PyMuPDF]
    RAG[rag_service + FAISS]
    LLM[ai_service Ollama/Gemini]
    TTS[tts_service]
    Voice[voice_service Whisper]
    Uploads[(UPLOAD_DIR / media_objects)]
  end

  Views --> Router --> API_Client
  API_Client -->|Bearer JWT| API
  API --> Deps --> Services
  Services --> Tables
  Services --> Hooks
  Hooks --> Tables
  Services --> PDF
  Services --> RAG
  Services --> LLM
  BG --> Tables
  API_Client --> Session
```

---

## 1. Frontend architecture

### 1.1 Technology

| Layer | Choice |
|-------|--------|
| Framework | Vue 3 (Composition API, `<script setup>`) |
| UI | Vuetify 3 + Material Design Icons |
| Routing | Vue Router 4 (history mode) |
| HTTP | Axios (`src/api/client.js`) |
| Build | Vite 8 |
| i18n / RTL | Arabic-first UI (RTL layouts) |

### 1.2 Project structure

```
src/
├── api/              # Thin HTTP clients per domain (maps to backend routers)
├── components/       # Reusable UI (layout, attendance, parent, settings, …)
├── composables/      # useAuth, useParentMonitor, useAuthSessions, …
├── config/           # navigation.js (sidebar items per role)
├── constants/        # ROUTES, app constants
├── layouts/          # StudentLayout, TeacherLayout, ParentLayout, OnboardingLayout
├── router/           # Guards: auth, onboarding, payment, teacher setup
├── utils/            # session.js, studentFlow.js, format.js
└── views/            # Page-level screens by role
```

### 1.3 Runtime modes

| Mode | Trigger | Behavior |
|------|---------|----------|
| **API mode** | `VITE_USE_MOCK !== 'true'` | All data from FastAPI; JWT on each request |
| **Mock mode** | `VITE_USE_MOCK=true` | Limited local session only (legacy/dev) |

Dev proxy: Vite serves `/api` → backend (`VITE_API_URL` or proxy config).

### 1.4 Layouts and role surfaces

```mermaid
flowchart LR
  subgraph Public
    Welcome[WelcomeView]
    Login[LoginView]
    Register[RegisterView]
  end

  subgraph Student
    SL[StudentLayout]
    Onb[OnboardingLayout]
    Dash[Dashboard / Course / Lesson]
    Pay[Payment flow]
    Prof[Profile + linked parents]
  end

  subgraph Teacher
    TL[TeacherLayout]
    TSetup[TeacherSetupView]
    TCourses[Grades / Lessons / Quizzes]
    TDash[TeacherDashboardView]
  end

  subgraph Parent
    PL[ParentLayout]
    PLink[ParentLinkStudentView]
    PDash[ParentDashboardView]
  end

  Login --> SL
  Login --> TL
  Login --> PL
  Register --> Onb
  Register --> PLink
```

### 1.5 Router guards (`src/router/index.js`)

Guards enforce business rules **before** navigation:

| Guard | Rule |
|-------|------|
| `requiresAuth` | Redirect to `/login` if no session |
| `meta.role` | Student / teacher / parent route isolation |
| `onboardingFlow` | Step order: grade → subjects → teachers |
| `paymentFlow` | Checkout when `needs_payment` (legacy bulk path) |
| `teacherSetup` | Redirect until `teacher_setup_complete` |
| `parentViewer` | Parent layout requires `role=parent` |
| `accountSettings` | Settings pages skip onboarding enforcement |
| `fetchMe` | Refresh flags via `GET /auth/me` on protected routes |

Post-auth routing is centralized in `utils/studentFlow.js` (`resolvePostAuthRoute`, `onboardingRouteForSession`).

### 1.6 State and session

| Concern | Implementation |
|---------|----------------|
| Auth session | `localStorage` key `eduspark_session` (access token, refresh token, `sessionId`, user flags) |
| API auth header | Axios interceptor attaches `Authorization: Bearer` |
| 401 handling | Clear session → redirect `/login` |
| Parent student context | `useParentStudents` + query `student_id` on parent APIs |
| Notifications | `NotificationBell` → `/notifications` |

### 1.7 Frontend ↔ backend mapping

Each `src/api/*.js` module mirrors a backend router group (see [API_ARCHITECTURE.md](./API_ARCHITECTURE.md)).

---

## 2. Backend architecture

### 2.1 Technology

| Layer | Choice |
|-------|--------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x (async via `asyncpg`) |
| Migrations | Alembic (`0001` … `0007_subscription_lifecycle`) |
| Auth | JWT access tokens + refresh tokens in `auth_sessions` |
| Validation | Pydantic v2 schemas (`app/schemas/`) |
| Static files | `/uploads` mounted from `UPLOAD_DIR` |

### 2.2 Layered design

```mermaid
flowchart TB
  HTTP[HTTP Request]
  Router[app/api/*.py routers]
  Deps[app/core/deps.py]
  Schema[Pydantic schemas]
  Service[app/services/*_service.py]
  Model[app/models/*.py]
  DB[(PostgreSQL)]

  HTTP --> Router
  Router --> Deps
  Router --> Schema
  Router --> Service
  Service --> Model
  Model --> DB
  Service --> Service
```

| Layer | Responsibility |
|-------|----------------|
| **Routers** | HTTP mapping, status codes, `Depends()` wiring, `db.commit()` at boundaries |
| **deps** | `AuthContext`, `require_role`, `require_student_actor`, `require_parent`, `require_admin` |
| **Schemas** | Request/response DTOs (API contract) |
| **Services** | Business logic, queries, orchestration |
| **Models** | SQLAlchemy table mappings |
| **integration_hooks** | Side effects after commits: notifications, attendance, analytics refresh |

### 2.3 API router registration

Central registry: `app/api/router.py` — mounts 20+ sub-routers under `/api`.

### 2.4 Key services (by domain)

| Domain | Services |
|--------|----------|
| Auth | `auth_session_service`, `user_status_service` |
| Catalog | `catalog_service`, `teacher_setup_service`, `teacher_courses_service` |
| Lessons | `lesson_processor`, `lesson_assets_service`, `lesson_publish_service`, `lesson_processing_tasks` |
| Student learning | `student_courses_service`, `subscription_service`, `subscription_access_service`, `subscription_expiration_service` |
| Quizzes | `quiz_service` (AI lesson), `course_quiz_service` (manual) |
| Parent | `parent_link_service`, `parent_monitoring_service`, `parent_insight_service`, `parent_subscription_service`, `student_parent_transparency_service` |
| Payments | `payment_service` |
| AI | `ai_service`, `rag_service`, `embedding_service`, `pdf_service`, `voice_service`, `tts_service`, `ai_job_service` |
| Ops | `notification_service`, `attendance_service`, `attendance_activity_service`, `analytics_rollup_service`, `grade_report_service`, `audit_service` |
| Planner | `planner_chat_service`, `schedule_optimizer`, `planner_memory_service` |

### 2.5 Application lifecycle (`app/main.py`)

| Startup | Action |
|---------|--------|
| `init_db()` | Connectivity check; optional pgvector extension |
| Background task | `_subscription_expiration_loop()` — periodic expiry notifications |
| Static mount | `/uploads` for lesson PDFs, voice, avatars |

### 2.6 Security model

```mermaid
sequenceDiagram
  participant C as Client
  participant API as FastAPI
  participant JWT as JWT decode
  participant AS as auth_sessions

  C->>API: Authorization Bearer access_token
  API->>JWT: decode sub, role, sid, viewer_mode
  JWT-->>API: payload
  API->>AS: get_active_session(sid, user_id)
  AS-->>API: session valid
  API->>API: require_role / require_student_actor
  API-->>C: response
```

- Access token embeds `sub` (user id), `role`, optional `sid` (session id).
- Each request with `sid` validates session not revoked/expired (`auth_session_service.get_active_session`).
- Role checks are **additive** to `users.role`; extended roles via `user_roles` + `roles` (e.g. admin audit API).

---

## 3. Database architecture

### 3.1 Overview

- **47 tables** in PostgreSQL (see [ERD.md](./ERD.md)).
- **Single database**; no per-tenant schemas.
- **Alembic** is the source of truth for schema evolution (head: `0007_subscription_lifecycle`).

### 3.2 Domain clusters

```mermaid
erDiagram
  users ||--o| student_profiles : student
  users ||--o| teacher_profiles : teacher
  users ||--o{ auth_sessions : sessions
  teacher_profiles ||--o{ courses : teaches
  subjects ||--o{ courses : catalog
  courses ||--o{ lessons : content
  lessons ||--o{ content_chunks : rag
  users ||--o{ student_course_access : enrollment
  courses ||--o{ student_course_access : access
  users ||--o{ parent_student_links : parent
  users ||--o{ parent_student_links : child
```

### 3.3 Identity model

| Concept | Storage |
|---------|---------|
| All account types | `users` (`role` enum: student, teacher, parent) |
| Student extension | `student_profiles` (1:1) |
| Teacher extension | `teacher_profiles` (1:1) |
| Parent | No separate profile — `users` + `parent_student_links` |
| Admin / extra roles | `roles` + `user_roles` |

### 3.4 Enrollment and subscriptions

| Table | Purpose |
|-------|---------|
| `student_course_access` | Per-student per-course unlock; `payment_status`, `activated_at`, `expires_at` |
| `payments` / `payment_items` | Checkout records (bulk or audit trail) |
| Per-course subscribe | `subscription_service` → `activate_paid_access()` |

Access check: `subscription_access_service.is_access_active()` — paid **and** `expires_at > now`.

### 3.5 Analytics pattern

Pre-aggregated rollups (refreshed by `analytics_rollup_service` via hooks):

| Table | PK |
|-------|-----|
| `course_analytics` | `course_id` |
| `teacher_analytics` | `teacher_profile_id` |
| `student_analytics` | `student_id` |
| `student_grade_reports` | `id` (unique student+course) — parent dashboard |

### 3.6 Media

| Table | Role |
|-------|------|
| `media_objects` | Storage metadata (local/S3/R2/MinIO) |
| `lesson_assets` | Ordered assets per lesson, optional FK to `media_objects` |
| Legacy columns on `lessons` | `pdf_path`, `video_url`, `voice_path` (synced by `lesson_assets_service`) |

---

## 4. AI pipeline architecture

EduSpark has **two quiz systems** and **one lesson intelligence pipeline**.

### 4.1 Lesson processing pipeline

Triggered by teacher upload/process endpoints → `lesson_processor.process_lesson()` (and/or `ai_jobs` queue).

```mermaid
flowchart LR
  PDF[PDF upload] --> Extract[pdf_service extract_text]
  Extract --> Chunk[chunk_text]
  Chunk --> DB[(content_chunks)]
  Chunk --> FAISS[embedding_service FAISS index optional]
  Voice[voice sample] --> Whisper[voice_service transcribe]
  Whisper --> Persona[persona_prompt]
  Persona --> Lesson[(lessons)]
  Chunk --> QuizGen[quiz_service generate_questions]
  QuizGen --> QQ[(quiz_questions)]
  Lesson --> Status[status processed]
```

| Step | Service | Output |
|------|---------|--------|
| PDF text extraction | `pdf_service` | `lessons.preview`, `page_count` |
| Chunking | `pdf_service.chunk_text` | `content_chunks` rows |
| Vector index (optional) | `embedding_service` | FAISS under `VECTOR_INDEX_DIR` |
| Voice / persona | `voice_service`, `teacher_voice_service` | `lessons.persona_prompt` |
| Quiz generation | `quiz_service` | `quiz_questions` (AI lesson quiz) |
| Job tracking | `ai_job_service` | `ai_jobs` row (pending → running → completed) |

Config flags: `ENABLE_PGVECTOR`, `ENABLE_EMBEDDINGS`, `LLM_PROVIDER` (default `gemini`; optional `ollama` dev fallback), `GEMINI_API_KEY`, `ENABLE_WHISPER`, `ENABLE_TTS`.

### 4.2 Student tutor chat (RAG)

```mermaid
sequenceDiagram
  participant S as Student
  participant API as POST /student/chat
  participant RAG as rag_service
  participant LLM as ai_service

  S->>API: message + lesson_id
  API->>API: student_has_lesson_access
  API->>RAG: retrieve_chunks(lesson_id, query)
  Note over RAG: FAISS if enabled else keyword scoring
  RAG-->>API: context chunks
  API->>LLM: generate_tutor_reply + persona
  LLM-->>API: reply
  API->>API: persist chat_messages
  API-->>S: ChatResponse
```

### 4.3 AI jobs API

- Enqueue: lesson process / publish flows create `ai_jobs` rows.
- Poll: `GET /ai/jobs/{job_id}` for status/result.
- Workers run **in-process** (same app) via `lesson_processing_tasks` — not a separate worker service in repo.

### 4.4 Teacher voice profile

| Step | Endpoint / service |
|------|-------------------|
| Upload sample | `POST /teacher/voice-sample` → `teacher_voice_samples` |
| Process | `teacher_voice_service` → transcript + persona |
| TTS preview | `tts_service` (optional `ENABLE_TTS`) |

Voice informs lesson chat persona and optional answer audio.

---

## 5. Authentication flow

### 5.1 Registration

```mermaid
sequenceDiagram
  participant U as User
  participant FE as RegisterView
  participant API as POST /auth/register
  participant DB as PostgreSQL

  U->>FE: name, email, password, role
  FE->>API: RegisterRequest
  API->>DB: INSERT users
  alt student
    API->>DB: INSERT student_profiles
  else teacher
    API->>DB: INSERT teacher_profiles
  end
  API->>DB: INSERT auth_sessions + tokens
  API-->>FE: TokenResponse + UserOut flags
  FE->>FE: setSession + redirect by role
```

| Role | Post-register redirect (frontend) |
|------|-----------------------------------|
| student | Onboarding grade |
| teacher | Teacher setup or dashboard |
| parent | `/parent/link` |

### 5.2 Login and session

```mermaid
sequenceDiagram
  participant U as User
  participant FE as LoginView
  participant API as POST /auth/login
  participant AS as auth_sessions

  U->>FE: email, password
  FE->>API: LoginRequest
  API->>API: verify_password
  API->>AS: create_session (refresh hash, device meta)
  API-->>FE: access_token, refresh_token, session_id, user
  FE->>FE: merge flags via /auth/me on navigation
```

### 5.3 Session management (multi-device)

| Action | API |
|--------|-----|
| List devices | `GET /auth/sessions` |
| Revoke one | `DELETE /auth/sessions/{id}` |
| Revoke all | `DELETE /auth/sessions` |
| Logout current | `POST /auth/logout` |

Frontend: `UserSettingsView` → `SecurityDevicesSection` (`useAuthSessions`).

### 5.4 Authorization matrix (simplified)

| Dependency | Allows |
|------------|--------|
| `get_auth_context` | Any valid JWT + active session |
| `require_role(teacher)` | `users.role == teacher` |
| `require_role(student)` | `users.role == student` |
| `require_parent` | `users.role == parent` |
| `require_student_actor` | Student writes (blocks parent viewer mode if reintroduced) |
| `require_admin` | `user_roles.slug == admin` |

---

## 6. Parent monitoring flow

Parents are **read-only monitors** of linked students (no student credential sharing at registration).

### 6.1 Linking flow

```mermaid
sequenceDiagram
  participant St as Student
  participant Pa as Parent
  participant API as parent APIs
  participant DB as parent_student_links

  St->>API: GET /parent/link-code (as student)
  API-->>St: parent_link_code on student_profiles
  St->>Pa: shares code offline
  Pa->>API: POST /parent/link { link_code }
  API->>DB: INSERT parent_student_links
  API-->>Pa: student_id
```

### 6.2 Dashboard aggregation

```mermaid
flowchart TB
  Pa[Parent selects student] --> API[GET /parent/dashboard?student_id=]
  API --> Resolve[parent_link_service.resolve_parent_student_id]
  API --> View[record_parent_view last_viewed_at]
  API --> Mon[parent_monitoring_service.build_full_parent_dashboard]
  Mon --> Act[activity_service]
  Mon --> Quiz[build_quiz_tracking]
  Mon --> Att[attendance_service]
  Mon --> Plan[planner progress]
  Mon --> Sub[parent_subscription_service]
  Mon --> Grades[grade_report_service]
  Mon --> Insights[parent_insight_service]
  API --> FE[ParentDashboardView]
```

| UI section | Data source |
|------------|-------------|
| Child summary | `users` + stats |
| Subscriptions | `student_course_access` via `list_student_subscription_status` |
| Quiz tracking | `quiz_attempts` + course manual quizzes |
| Attendance | `student_attendance_records` |
| Planner | `planner_schedule_slots` |
| Activity feed | `student_activity_events` |
| AI insights | `parent_insight_service` (rule-based + quiz scores) |

### 6.3 Student transparency (inverse)

Students see who is linked: `GET /student/linked-parents` → `StudentLinkedParentsSection` on profile.

---

## 7. Subscription lifecycle flow

### 7.1 Activation

```mermaid
sequenceDiagram
  participant S as Student
  participant API as POST /student/subscriptions/subscribe
  participant Pay as payment_service optional
  participant Acc as subscription_access_service
  participant Hook as integration_hooks

  S->>API: course_id + payment method
  API->>Acc: ensure_course_access
  API->>API: create Payment + PaymentItem
  API->>Acc: activate_paid_access (activated_at, expires_at)
  API->>Hook: notify_payment_received + after_payment_success
  Hook->>Hook: analytics_rollup refresh
  API-->>S: unlocked
```

Renewal while active: `activate_paid_access` **extends** `expires_at` from current expiry.

### 7.2 Access enforcement

```mermaid
flowchart TD
  Req[Student requests lesson/course/quiz] --> Check{is_access_active?}
  Check -->|paid AND expires_at > now| Allow[Return content]
  Check -->|expired or pending| Deny[403 / locked UI]
```

Used in: `student_courses_service`, `student_has_lesson_access`, `course_quiz_service._student_has_paid_access`, `notification_service.notify_course_students` (active only).

### 7.3 Expiration notifications

```mermaid
flowchart LR
  Loop[Background loop main.py] --> Run[subscription_expiration_service.run_expiration_check]
  Run --> Scan[Scan paid student_course_access]
  Scan --> D7{days_left in 7,3,1?}
  D7 --> N1[notifications subscription_expiring]
  Scan --> Exp{expires_at <= now?}
  Exp --> N2[notifications subscription_expired]
  N1 --> Parent[notify_parent_alert optional]
  N2 --> Parent
```

Dedup: notification `payload` contains `access_id` + `marker` (e.g. `expiring_d7`, `expired`).

### 7.4 UI surfaces

| Actor | Surface |
|-------|---------|
| Student | Course cards show expiry chip, lock reason, renew CTA |
| Teacher | Dashboard subscriber counts: active / expiring / expired |
| Parent | `ParentSubscriptionsSection` on dashboard |

---

## 8. Cross-cutting concerns

| Concern | Implementation |
|---------|----------------|
| Notifications | `notifications` table + bell UI; types in `NotificationType` enum |
| Attendance | Auto-write on lesson complete / quiz submit (`attendance_activity_service`) |
| Audit | `audit_logs` + `GET /admin/audit-logs` (admin role) |
| CORS | `settings.cors_list` |
| File uploads | Multipart → `UPLOAD_DIR`; size limits in `config` |

---

## 9. Deployment notes (reference)

| Component | Typical deployment |
|-----------|-------------------|
| Frontend | Static build behind CDN or Vite preview |
| Backend | Uvicorn / Docker (`backend/Dockerfile`) |
| Database | PostgreSQL 14+ |
| Migrations | `alembic upgrade head` before serving traffic |
| AI | Optional GPU host for Whisper; Ollama sidecar for LLM |

---

## 10. Related documents

| Document | Contents |
|----------|----------|
| [ERD.md](./ERD.md) | Full entity list, FKs, Mermaid ERD diagrams |
| [ERD.dbml](./ERD.dbml) | DBML for dbdiagram.io |
| [API_ARCHITECTURE.md](./API_ARCHITECTURE.md) | Complete route catalog |
