# Adaptive Learning Intelligence — Architecture (Phase 2)

Grammar Engine v1.0 remains the production baseline. Adaptive Intelligence sits
**above** it and is strictly read-only with respect to curriculum, mastery,
progression, resolver, evidence ledger, integrity, planner, and lesson runtime.

## Core principle

| Layer | Decides |
| --- | --- |
| Curriculum / Catalog / Progression | **What** should be learned |
| Adaptive Intelligence | **How** this student should learn it |

Never invert these responsibilities.

## Architecture diagram

```mermaid
flowchart TB
  subgraph locked ["Grammar Engine v1.0 LOCKED"]
    CAT[Catalog / Curriculum]
    RES[Target Resolver]
    MAS[Mastery Engine]
    PROG[Progression Engine]
    REV[Review Engine]
    EV[Evidence Ledger]
    INT[Integrity]
    PLN[Planner]
    RT[Lesson Runtime]
  end

  subgraph adaptive ["Adaptive Intelligence Phase 2 — read-only"]
    PROF[Student Learning Profile]
    SIG[Weakness Detection]
    CONF[Confidence Model]
    DIFF[Adaptive Difficulty]
    REC[Review Recommendations]
    MIX[Personalized Activity Mix]
    REM[AI Remediation Advice]
    TCH[Teacher Signals]
    PAR[Parent Signals]
    EXP[Explainability]
  end

  MAS -->|readonly snapshot| PROF
  MAS -->|readonly snapshot| SIG
  MAS -->|readonly snapshot| CONF
  PROG -->|readonly current/focus| DIFF
  REV -->|due queue hints| REC
  CONF --> DIFF
  CONF --> REC
  SIG --> REM
  SIG --> TCH
  PROF --> MIX
  DIFF --> EXP
  REC --> EXP
  REM --> EXP
  REC --> PAR
  PROG --> PAR
  MAS --> PAR

  DIFF -.->|HOW only| AuthoringHint[Future activity authoring hints]
  MIX -.->|HOW only| AuthoringHint
  REM -.->|HOW only| AuthoringHint

  adaptive -->|never writes| MAS
  adaptive -->|never unlocks| PROG
  adaptive -->|never changes| CAT
  adaptive -->|never bypasses| RES
```

## Recommendation engine flow

```mermaid
flowchart LR
  A[Load mastery + progression + review] --> B[Derive / load Learning Profile]
  B --> C[Detect learning signals]
  C --> D[Compute learning_confidence per topic]
  D --> E[Difficulty for current grammar]
  D --> F[Review horizons]
  C --> G[Remediation kinds]
  B --> H[Activity mix weights]
  F --> I[Teacher + Parent insights]
  E --> J[Explainable bundle]
  F --> J
  G --> J
  H --> J
  I --> J
```

## Difficulty model

| Level | Vocabulary | Sentences | Distractors | Listening | Writing |
| --- | --- | --- | --- | --- | --- |
| Easy | low | short | soft | slow | supported |
| Normal | medium | medium | balanced | normal | standard |
| Advanced | high | long | challenging | fast | extended |

Grammar target (`grammar_id`) is never changed by difficulty.

## Weakness detection strategy

Deterministic thresholds over mastery records:

- recurring mistakes — low accuracy with ≥3 evidence
- forgotten grammar — long idle (≥21 days) with prior mastery
- low confidence — high mastery + low `learning_confidence`
- repeated retries — many evidence + weak accuracy/confidence
- long inactivity — idle ≥9 days
- unstable performance — low stability
- retention risk — elevated `retention_risk`
- skill gap — single-skill evidence concentration

## JSONB namespace

Profile persistence (optional) uses sibling key:

`promotion_readiness_json["adaptive_intelligence"]`

It must never mutate `promotion_readiness_json["grammar"]`.

## Out of scope (Phase 2)

- AI Tutor memory
- Conversational coaching
- Curriculum / unlock / mastery mutations
