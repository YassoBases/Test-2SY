# STUDENT_STITCH_CONTEXT — EduSpark Design Context for Google Stitch

This document is **design context only**. It describes what EduSpark is, how it should feel, and the visual rules any student-facing screen must respect. It is not an implementation plan.

---

## 1. Product identity

- **EduSpark** is a single, connected **AI learning platform** for students (Syrian curriculum + English language learning).
- It is one product, not a collection of separate tools. Every screen should feel like the same app.
- Resolve the brand to **one name and one wordmark: EduSpark** (older "EduMind" naming should be treated as legacy and not used).
- Tone: modern, calm, encouraging, "smart tutor by your side" — not clinical, not gamified-to-excess. Learning-first, AI-assisted.

---

## 2. Target student experience

- Primary users are school-age students studying in **Arabic**, many also learning **English**.
- The experience should feel **guided**: the student always knows where they are, what to do next, and how they are progressing.
- Two core journeys share one home base:
  1. **Academic** — courses, lessons, quizzes, planning, achievements.
  2. **Language learning** — placement, then adaptive reading / listening / speaking / writing / vocabulary practice.
- Emotional targets: confidence, momentum, clarity. Reduce cognitive load, especially for younger and lower-English-level students.

---

## 3. Current visual problems to fix

- **Two competing "primary" colors**: an indigo/purple family across the app and a teal/cyan family inside the language module. There is no single action color.
- **Split brand identity** (EduSpark vs. EduMind) in the same interface.
- **Mixed language in the chrome**: page titles and language-module labels appear in English while the surrounding UI is Arabic.
- **Two different navigation systems**: a global grouped sidebar vs. a separate horizontal tab-carousel inside the language module. Entering language learning feels like leaving the app.
- **Duplicate/overlapping planning screens** with two different visual treatments for what is essentially one "plan my study" idea.
- **Card inconsistency**: different corner radii, padding, and shadow weight for cards that play the same role.
- **Very long, flat forms** (profile, planning, settings) with weak sectioning and no anchoring.
- **Flat empty states** with no clear next action.
- **Status shown by color alone** (locked vs. active, exam step progress).

---

## 4. Existing design tokens that must be respected

Stitch output should stay within this token language (do not invent a new palette or scale):

**Brand / accent**
- Primary (indigo): `#6366f1` (hover `#7c6cf0`, deep `#4f46e5`)
- Violet accent: `#7c3aed`
- Cyan/blue accent: `#38bdf8` / `#22d3ee` (accent only — not a second primary)
- Success `#34d399` / `#10b981`, Warning `#fbbf24` / `#f59e0b`, Error `#f87171` / `#ef4444`

**Themes**
- Two modes: **Morning (light)** and **Night (dark)**. Design must work in both.
- Morning surfaces: page `#f4f7fb`, elevated card `#ffffff`, secondary `#edf3fa`; text `#0c1929` with muted `#3f4f63`.
- Night surfaces: deep navy backgrounds (`#060a14`–`#121a32`), light text `#e8ecf4` with muted variants.

**Radius scale**: 8 / 12 / 16 / 20 / 24 px (default 20). Cards typically 16px; pills/chips use the smaller end.

**Spacing scale**: 8 / 12 / 16 / 24 / 32 / 40 px. Use this rhythm; avoid arbitrary values.

**Typography**: Arabic-first fonts **Tajawal** (display) and **Cairo** (body). Sizes: display `clamp(1.5rem–2rem)`, title `1.25rem`, body `1rem`, small `0.875rem`, caption `0.75rem`.

**Motion**: subtle, fast (180–350ms), ease-out; respect reduced-motion.

---

## 5. RTL-first requirements

- Arabic is the **default direction**. Layout, alignment, iconography, and flow are **right-to-left first**; LTR is the exception.
- Navigation lives on the **right**; content reads right-to-left.
- Directional icons (arrows, chevrons, "next/back", progress) must mirror correctly in RTL.
- Numbers, times, and dates must read naturally in an Arabic context.
- Spacing and padding should be logical (start/end), never hard-coded left/right in a way that breaks mirroring.

---

## 6. Bilingual Arabic / English content behavior

- **UI chrome is Arabic** in the Arabic experience: titles, navigation, buttons, labels, empty states — all localized. No stray English in the frame.
- **English appears only as intentional learning content** ("English content islands"): reading passages, listening/exam questions, vocabulary words, dictionary entries.
- These English islands are **LTR blocks embedded inside the RTL page**, visually marked as content (not chrome), with correct bidirectional handling so punctuation and alignment stay correct.
- For lower-level learners, keep instructions and controls in Arabic even when the practice content is English.

---

## 7. Global navigation model

- A single, persistent **global sidebar** is the constant frame across the whole platform, grouped into:
  - **Learning** (journey/home, messages, languages)
  - **Planning** (subscriptions, schedule/routine, planner)
  - **Account** (achievements, profile, settings)
- A persistent **top header** shows the current page title (localized), plus language, theme, notifications, and account.
- A pinned **AI teacher presence** ("معلمك الذكي") is anchored in the frame.
- The student should never lose this frame while moving between areas.

---

## 8. Language module relationship to the main platform

- The language module is a **section inside EduSpark**, not a separate product.
- Its internal navigation (reading, listening, speaking, writing, vocabulary, dictionary, curriculum, placement) should read as a **secondary, in-page navigation nested under the global sidebar** — clearly subordinate, same visual system, same direction (RTL frame with English content islands).
- Entering the language module must not swap the app's identity, color, or navigation paradigm.
- Placement/paywall should preview value and feel continuous with the rest of the platform.

---

## 9. AI teacher identity

- EduSpark's AI is presented as a **friendly, supportive smart teacher** ("معلمك الذكي"), consistently themed wherever AI appears (assistant panels, planners, exam feedback, chat).
- One recognizable AI motif/voice across the platform: encouraging, concise, Arabic-first.
- AI moments (feedback, guidance, generated plans) should share a consistent visual treatment so the "tutor" feels like one entity, not many disconnected features.

---

## 10. Unified card, button, spacing, radius, and typography direction

- **Cards**: one card family. Rounded (≈16px), soft elevation, consistent internal padding on the spacing scale. Same role → same card. Distinct levels only via subtle elevation/surface tokens, not random radii/shadows.
- **Buttons**: **one primary action style** (indigo). Clear hierarchy: primary → secondary (outline/tonal) → ghost/text. Cyan/teal is an accent, never a competing primary.
- **Spacing**: consistent vertical rhythm using the 8–40px scale; generous section separation; avoid dense walls of controls.
- **Radius**: consistent scale; cards, inputs, chips, and buttons each use a predictable radius tier.
- **Typography**: Arabic-first type ramp with clear hierarchy (display for hero, title for sections, body for content, caption for meta). One page skeleton: **hero → sectioned content → cards**.
- **Heroes**: one banner pattern (eyebrow + title + subtitle) reused across dashboards and language pages, localized.

---

## 11. Accessibility requirements

- **Never rely on color alone** for state — pair with icon and/or text (locked/active, exam step done/current/upcoming, correct/incorrect).
- **Contrast**: body and muted text must reach at least 4.5:1 against their surface, including over gradient/aurora backgrounds; large text at least 3:1.
- **Touch targets**: comfortably large and spaced (radios, chips, day pickers, audio controls) for younger users and touch devices.
- **Visible focus** state on all interactive elements, including custom buttons and chips.
- **Legible sizing**: avoid tiny caption-only critical information; keep controls readable.
- Respect **reduced-motion** preferences.

---

## 12. Responsive requirements

- Design **mobile-first within an RTL frame**; screens must hold up on narrow widths.
- The global sidebar collapses to an accessible drawer on small screens; the header stays usable.
- The language module's secondary navigation must **wrap or scroll gracefully** (no cramped overflow) and remain clearly navigable on mobile.
- The placement-exam step indicator must degrade cleanly on narrow widths (no crowded, unreadable chips).
- **Long forms** (profile, planning, settings) should break into digestible, sectioned, scannable steps rather than a single tall scroll.
- Content and cards reflow to single-column on mobile with the same spacing/radius/typography rules.

---

*Companion document: `STUDENT_UI_AUDIT.md` (full findings). This file is the distilled design context for Google Stitch.*
