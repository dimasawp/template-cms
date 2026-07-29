# Architecture

## Overview

This CMS uses a **Monolithic Modular DDD** architecture. The backend is a single FastAPI application organized into domain modules, each with its own layered structure. Two separate Vue 3 SPAs consume the REST API.

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        docker-compose.yml                        │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────────┐ │
│  │   MySQL   │  │   Backend    │  │  Admin FE │  │  Public FE   │ │
│  │   :3306   │◄─┤  FastAPI     │◄─┤  Vue 3    │  │  Vue 3       │ │
│  │           │  │  :8000       │  │  :5173    │  │  :3000       │ │
│  └──────────┘  └──────┬───────┘  └──────────┘  └──────────────┘ │
│                       │ WebSocket                                │
│                       └────────────────────────────────┘         │
└──────────────────────────────────────────────────────────────────┘
```

## Backend Layers (DDD per Module)

Each module under `app/modules/<module_name>/` follows the same layered structure:

```
modules/<module_name>/
├── models/            # SQLAlchemy models (table definitions)
├── schemas/           # Pydantic v2 request/response models
├── repositories/      # Data access layer (extends BaseRepository)
├── services/          # Business logic layer (optional, extends BaseService)
└── controllers/       # FastAPI route handlers (APIRouter)
```

**Request flow:**

```
HTTP Request
    │
    ▼
Controller (FastAPI route)
    │  ┌─ Depends(check_permission("..."))  → RBAC guard
    │  └─ Depends(get_db)                    → DB session
    ▼
Service (business logic)
    │
    ▼
Repository (data access)
    │
    ▼
Model (SQLAlchemy)
    │
    ▼
Database
```

### Core Files

| File | Purpose |
|---|---|
| `app/core/config.py` | Pydantic settings from `.env` |
| `app/core/database.py` | SQLAlchemy engine, session, Base |
| `app/core/dependencies.py` | `get_current_user`, `check_permission`, `get_db` |
| `app/core/security.py` | JWT creation/decoding, password hashing |
| `app/core/extensions.py` | Toggle switch for extension modules |
| `app/core/websocket.py` | WebSocket connection manager |
| `app/modules/_base/repository.py` | Generic CRUD (`BaseRepository`) |
| `app/modules/_base/service.py` | Base service layer |
| `app/helpers/response.py` | Standardized JSON response envelope |

### Modules List

**Core Modules** (always active):
- `auth`, `users`, `roles`, `settings`, `audit`, `dashboard`, `media`, `menus`, `notifications`

**Extension Modules** (can be toggled via `extensions.py`):
- `posts`, `categories`, `public`

## Frontend Layers (Admin SPA)

```
src/
├── router/index.js      # Route definitions + navigation guards
├── stores/              # Pinia stores (auth, settings)
├── services/            # Axios API service modules
├── composables/         # Reusable composition functions
├── views/               # Page-level components (per module)
├── components/
│   ├── ui/              # Atomic UI components (shadcn/vue-style)
│   └── common/          # Composite domain components
├── layouts/             # DashboardLayout (sidebar, topbar)
└── config/modules.js    # Extension module config for sidebar
```

**Data flow:**

```
User Action
    │
    ▼
View Component
    │
    ▼
Composable / Store (Pinia)
    │
    ▼
Service (Axios)
    │
    ▼
API Call → Backend
    │
    ▼
Response → Store → View re-renders
```

## Database

### ERD (Simplified)

```
User ───> Role ───> Permission     (via role_permissions)
  │
  ├──> UserSession
  ├──> AuditLog
  ├──> Post
  ├──> Category
  └──> Notification

Category ──┐  (self-referencing parent_id)
  │         │
  └──> Post

Post ───> Category
```

### Key Patterns

- **Soft delete**: All major entities have `deleted_at` (nullable DateTime). The `BaseRepository` automatically filters out deleted records.
- **Timestamps**: All timestamps use **WIB (UTC+7)** via `app.helpers.date_helper.get_now_wib()`.
- **UUID-like slugs**: Entities use unique string slugs for URL-friendly identifiers.

## Module Registration (Extension System)

The `app/modules/__init__.py` auto-discovers routers:

1. It iterates all directories under `app/modules/`.
2. It skips `__pycache__`, `_base`, and dotted/hidden dirs.
3. Modules are classified as **core** (always active) or **extension** (only active if listed in `ENABLED_EXTENSIONS` from `app/core/extensions.py`).
4. For each active module, it scans `controllers/*_controller.py` for `APIRouter` instances.
5. All discovered routers are registered via `app.include_router(router)`.

## RBAC (Role-Based Access Control)

Three tables: `permissions`, `roles`, `role_permissions` (many-to-many).

- Every user has exactly one `role_id`
- Permissions are checked per-request via `check_permission("module.action")` dependency
- Super Admin bypasses all checks on frontend (not backend — super_admin must have the permission assigned via seeder)

See [02-module-development.md](02-module-development.md) for adding new permissions.
