# UI/UX Enhancement Phase

Enhancements preserve the existing EduSpark dark glass identity while improving readability, hierarchy, and subtle motion.

## Global surfaces (`src/assets/styles/main.css`)

| Token / class | Purpose |
|---------------|---------|
| `--em-glass` (0.72 opacity) | Default cards — less see-through |
| `--em-glass-solid` | Forms, auth, empty states, `.glass-card--solid` |
| `--em-overlay-scrim` | Dialog/backdrop — blocks content behind |
| `.kpi-card` | Dashboard mini-stat cards with gradient top bar + hover |
| `.section-block` | Section title + subtitle hierarchy |
| `.page-header--panel` | Page headers on a solid panel (default via `PageHeader`) |

### Overlays (automatic)

- `v-dialog` cards — opaque background
- `v-menu` / select lists — solid surface
- Outlined fields — opaque field background
- Navigation drawer & app bar — semi-opaque with blur

## Components

| Component | Changes |
|-----------|---------|
| `StatCard.vue` | Color accent bar, trend icons, optional progress bar |
| `AppToast.vue` + `useToast.js` | Typed toasts (success/error/warning/info), icons, entrance animation |
| `PageHeader.vue` | `panel` prop (default `true`) — solid header panel |
| `EmptyState.vue` | Solid card + float animation on icon |
| `AuthShell.vue` | Solid auth card for login/register forms |

## Dashboards

- **Teacher** — KPI subscription row + `StatCard` color mapping from API
- **Student** — KPI row with icons; courses section uses `section-block`

## Vuetify defaults (`src/plugins/vuetify.js`)

- Field `bgColor`: `rgba(12, 18, 38, 0.94)`
- Drawer/app bar: opaque tints
- `VDialog.scrim`: dark overlay

## Motion (subtle)

- Card hover: `.eduspark-card-hover`, `.kpi-card`
- Route transitions: `.fade` in layouts
- Skeleton shimmer on loaders
- Toast `toast-enter` animation
- Buttons: 1px lift on hover

## Consistency

Teacher, student, parent, and language modules share the same tokens and utilities — no separate theme per role.

## Usage

```vue
<!-- Readable form panel -->
<v-card class="glass-card glass-card--solid pa-6" />

<!-- Dashboard stat -->
<v-card class="glass-card kpi-card kpi-card--success pa-4 text-center" />

<!-- Section -->
<section class="section-block">
  <div class="section-block__head">...</div>
</section>

<!-- Page header without panel (rare) -->
<PageHeader :panel="false" ... />
```
