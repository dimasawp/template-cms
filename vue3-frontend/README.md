# CMS Template — Frontend Dashboard

Admin dashboard SPA built with **Vue 3**, **TypeScript**, **Vite**, and **Tailwind CSS 3**. Uses a shadcn-vue inspired design system with persistent dark/light theme support.

## 🛠 Tech Stack

| Category          | Technology                                    |
|-------------------|-----------------------------------------------|
| Framework         | Vue 3 (Composition API, `<script setup>`)     |
| Language          | TypeScript                                    |
| Build Tool        | Vite 5                                        |
| Styling           | Tailwind CSS 3 + CSS Variables (HSL tokens)   |
| State Management  | Pinia                                         |
| Routing           | Vue Router 4                                  |
| HTTP Client       | Axios (with interceptors)                     |
| UI Primitives     | Radix-Vue (headless)                          |
| Icons             | Lucide Vue Next                               |
| Animations        | tailwindcss-animate                           |
| Utilities         | VueUse, clsx, tailwind-merge, date-fns        |

## 🏗 Project Structure

```
vue3-frontend/
├── index.html                        # HTML entry point
├── vite.config.ts                    # Vite configuration
├── tailwind.config.js                # Tailwind theme tokens (HSL)
├── .env.example                      # Environment template
│
├── src/
│   ├── main.ts                       # App bootstrap (Router + Pinia + Theme)
│   ├── App.vue                       # Root component
│   │
│   ├── assets/
│   │   └── index.css                 # CSS Variables: dark/light color palette
│   │
│   ├── components/
│   │   ├── common/                   # Reusable layout components
│   │   │   ├── DataTableToolbar.vue  # Search, filter, bulk actions toolbar
│   │   │   ├── MaintenanceBanner.vue # Global maintenance mode banner
│   │   │   ├── PageHeader.vue        # Page title + breadcrumbs
│   │   │   └── Pagination.vue        # Page navigation component
│   │   │
│   │   └── ui/                       # Base UI components (shadcn-style)
│   │       ├── Avatar.vue
│   │       ├── Badge.vue
│   │       ├── Button.vue
│   │       ├── CardBasic.vue
│   │       ├── CardImage.vue
│   │       ├── CardStats.vue
│   │       ├── ConfirmationDialog.vue
│   │       ├── Dialog.vue
│   │       ├── FormField.vue
│   │       ├── Input.vue
│   │       ├── Label.vue
│   │       ├── PopoverHeader.vue
│   │       ├── SkeletonLoader.vue
│   │       ├── StatusIndicator.vue
│   │       └── Toaster.vue
│   │
│   ├── composables/                  # Vue Composables (reusable logic)
│   │   ├── useConfirmation.ts        # Confirmation dialog state
│   │   ├── useDataTable.ts           # Pagination, search, sort logic
│   │   ├── useRealtime.ts            # WebSocket notification listener
│   │   ├── useTheme.ts               # Dark/Light mode toggle (persistent)
│   │   └── useToast.ts               # Toast notification system
│   │
│   ├── layouts/
│   │   └── DashboardLayout.vue       # Sidebar + Topbar + Content area
│   │
│   ├── lib/
│   │   └── utils.ts                  # cn() utility for class merging
│   │
│   ├── router/
│   │   └── index.ts                  # Route definitions + navigation guards
│   │
│   ├── services/                     # API service layer (Axios)
│   │   ├── api.ts                    # Axios instance + interceptors
│   │   ├── authService.ts            # Auth endpoints
│   │   ├── userService.ts            # User CRUD endpoints
│   │   ├── roleService.ts            # Role & permission endpoints
│   │   ├── auditService.ts           # Audit log endpoints
│   │   ├── notificationService.ts    # Notification endpoints
│   │   └── settingService.ts         # Settings endpoints
│   │
│   ├── stores/
│   │   └── auth.ts                   # Pinia auth store (user, token, permissions)
│   │
│   └── views/
│       ├── auth/
│       │   ├── LoginView.vue         # Login form
│       │   ├── RegisterView.vue      # Self-registration form
│       │   └── ForgotPasswordView.vue # Password reset request
│       │
│       ├── dashboard/
│       │   ├── DashboardView.vue     # Main dashboard page
│       │   └── ComponentsDocView.vue # UI component gallery / docs
│       │
│       ├── settings/
│       │   ├── ProfileView.vue       # Personal profile editing
│       │   ├── UsersView.vue         # User management table
│       │   ├── RolesView.vue         # Role & permission matrix
│       │   ├── AuditLogView.vue      # Audit trail viewer
│       │   ├── NotificationsView.vue # Notification center
│       │   ├── SessionsView.vue      # Active session management
│       │   └── GlobalSettingsView.vue # System settings panel
│       │
│       └── errors/
│           ├── ForbiddenView.vue     # 403 page
│           ├── MaintenanceView.vue   # 503 maintenance page
│           └── NotFoundView.vue      # 404 page
```

## 🚀 Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 3. Start Development Server

```bash
npm run dev
```

Open browser at `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

## 🎨 Design System

### Theme

The app uses **HSL CSS Variables** for theming, defined in `src/assets/index.css`. Supports both light and dark modes with a matte desaturated palette for a premium feel.

Color tokens are consumed via Tailwind config (`tailwind.config.js`) which maps semantic names:

| Token         | Usage                       |
|---------------|-----------------------------|
| `background`  | Page background             |
| `foreground`  | Primary text                |
| `primary`     | Buttons, links, accents     |
| `secondary`   | Secondary actions           |
| `muted`       | Disabled / placeholder text |
| `destructive` | Delete, error actions       |
| `card`        | Card backgrounds            |
| `popover`     | Dropdown / popover bg       |
| `border`      | Borders, dividers           |

### Theme Toggle

The `useTheme()` composable provides persistent dark/light mode:
- Saves preference to `localStorage`
- Syncs class `dark` on `<html>` element
- No flash/flicker on page reload

## 📄 Pages & Routes

| Path               | Name               | Auth | Permission       | Description                |
|--------------------|--------------------| -----|------------------|----------------------------|
| `/login`           | login              | Guest | —               | Login form                 |
| `/register`        | register           | Guest | —               | Registration (toggleable)  |
| `/forgot-password` | forgot-password    | Guest | —               | Password reset request     |
| `/dashboard`       | dashboard          | ✓    | —                | Main dashboard             |
| `/profile`         | profile            | ✓    | —                | Personal profile           |
| `/components`      | components-doc     | ✓    | —                | UI component gallery       |
| `/users`           | users              | ✓    | `users.view`     | User management            |
| `/roles`           | roles              | ✓    | `roles.view`     | Role management            |
| `/settings/audit-logs` | audit-logs     | ✓    | `super_admin`    | Audit trail                |
| `/global-settings` | global-settings    | ✓    | `super_admin`    | System settings            |
| `/active-sessions` | active-sessions    | ✓    | `super_admin`    | Session management         |
| `/notifications`   | notifications      | ✓    | —                | Notification center        |
| `/403`             | forbidden          | —    | —                | Access denied              |
| `/maintenance`     | maintenance        | —    | —                | Maintenance mode           |
| `/*`               | not-found          | —    | —                | 404 page                   |

## 🔌 API Integration

### Axios Interceptors (`services/api.ts`)

- **Request**: Automatically attaches `Authorization: Bearer <token>` header
- **Response 401**: Auto-attempts token refresh; if fails, logs out user
- **Response 503**: Redirects to maintenance page
- **Response errors**: Shows toast notification with server error message

### Service Layer Pattern

Each module has a dedicated service file:

```typescript
// Example: userService.ts
import api from './api'

export const userService = {
  getAll: (params) => api.get('/users', { params }),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
}
```

## 📦 Key Composables

| Composable          | Description                                        |
|---------------------|----------------------------------------------------|
| `useTheme()`        | Dark/Light mode toggle with localStorage persistence |
| `useDataTable()`    | Pagination, search, sort state for data tables     |
| `useConfirmation()` | Confirmation dialog open/close state management    |
| `useToast()`        | Global toast notification system                   |
| `useRealtime()`     | WebSocket connection for live notifications        |

## 🧩 Adding a New Page

1. Create `src/views/your-module/YourView.vue`
2. Add route in `src/router/index.ts` under the dashboard children
3. Add API service in `src/services/yourService.ts`
4. Add sidebar link in `src/layouts/DashboardLayout.vue`
5. (Optional) Add permission guard via `meta: { permission: 'your.permission' }`

## 📡 Real-time & Reactivity

### useRealtime() Composable
Enhanced with a hybrid connection strategy:
- **WebSocket First**: Attempts connection to `ws/notifications`.
- **Intelligent Fallback**: If WebSocket is disabled via `.env` or connection fails, automatically switches to **HTTP Polling** (60s interval).
- **Race-Condition Safe**: Connection attempts wait for global settings to load before deciding to handshake.

### Global Settings Store
Centralized reactivity via `src/stores/settings.ts`:
- **siteName**: Syncs across Document Title, Sidebar, and Login pages.
- **maintenanceMode**: Triggers the global maintenance banner and redirection.
- **enableWebsockets**: Controlled by Backend to reduce frontend connection errors.

