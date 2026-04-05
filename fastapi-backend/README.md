# CMS Template — Backend API

REST API backend built with **FastAPI**, **SQLAlchemy**, and **MySQL**. Provides authentication, role-based access control, audit logging, media management, and real-time notifications out of the box.

## 🏗 Project Structure

```
fastapi-backend/
├── main.py                          # App entry point, middleware, WebSocket
├── requirements.txt                 # Python dependencies
├── pytest.ini                       # Test configuration
├── .env.example                     # Environment template
│
├── app/
│   ├── core/
│   │   ├── config.py                # Pydantic Settings (from .env)
│   │   ├── database.py              # SQLAlchemy engine & session
│   │   ├── security.py              # JWT creation, password hashing
│   │   ├── dependencies.py          # Auth & permission FastAPI dependencies
│   │   ├── logger.py                # Rotating file logger
│   │   ├── websocket.py             # WebSocket connection manager
│   │   └── storage/                 # Multi-provider file storage
│   │       ├── base.py              # Abstract storage interface
│   │       ├── manager.py           # Storage provider factory
│   │       ├── local_project.py     # Save to ./storage/uploads/
│   │       └── local_system.py      # Save to absolute system path
│   │
│   ├── modules/                     # Auto-discovered feature modules
│   │   ├── __init__.py              # Router auto-discovery registry
│   │   ├── _base/                   # Base repository & service classes
│   │   ├── auth/                    # Login, Register, JWT refresh, Sessions
│   │   ├── users/                   # User CRUD, profile, avatar
│   │   ├── roles/                   # Role & Permission CRUD, matrix
│   │   ├── audit/                   # Audit trail (read-only)
│   │   ├── notifications/           # In-app notifications
│   │   ├── media/                   # File upload & management
│   │   └── settings/                # Global app settings
│   │
│   ├── seeds/
│   │   └── seed.py                  # Database seeder
│   │
│   ├── helpers/
│   │   ├── response.py              # Standard JSON envelope helpers
│   │   └── file_handler.py          # File validation utilities
│   │
│   └── exceptions/
│       ├── __init__.py              # Custom exception classes
│       └── handler.py               # Global exception handlers
│
├── tests/
│   ├── conftest.py                  # SQLite in-memory fixtures
│   └── integration/                 # 23 integration test cases
│       ├── test_auth.py
│       ├── test_users.py
│       ├── test_roles.py
│       ├── test_audit.py
│       ├── test_notifications.py
│       ├── test_media.py
│       └── test_settings.py
│
└── storage/                         # Uploaded files (gitignored)
```

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=db_cms_template

# Security — MUST change in production
SECRET_KEY=your-random-secret-key-here

# Storage mode: local_project | local_system | cloud
STORAGE_MODE=local_project
```

### 3. Seed Database

```bash
python -m app.seeds.seed
```

This will:
- **Non-production**: Drop all tables → recreate → seed fresh data (sequential IDs)
- **Production**: Only create missing tables & insert missing seed rows

### 4. Run Development Server

```bash
uvicorn main:app --reload
```

API available at `http://localhost:8000` · Swagger UI at `http://localhost:8000/docs`

## 🗄 Database Seeder

The seeder (`app/seeds/seed.py`) creates initial data:

### Roles (2)

| ID | Name          | Permissions                                     |
|----|---------------|-------------------------------------------------|
| 1  | `super_admin` | All 14 permissions                              |
| 2  | `admin`       | All except `roles.delete` and `settings.update` |

### Permissions (14)

| Module        | Permissions                                  |
|---------------|----------------------------------------------|
| Users         | `users.view`, `users.create`, `users.update`, `users.delete` |
| Roles         | `roles.view`, `roles.create`, `roles.update`, `roles.delete` |
| Audit         | `audit.view`                                 |
| Notifications | `notifications.view`                         |
| Settings      | `settings.view`, `settings.update`           |
| Sessions      | `sessions.view`, `sessions.delete`           |

### Users (2)

| Username     | Email                   | Password   | Role         |
|--------------|-------------------------|------------|--------------|
| `superadmin` | superadmin@example.com  | `admin123` | super_admin  |
| `admin`      | admin@example.com       | `admin123` | admin        |

### Settings (3)

| Key                     | Default Value  | Description                     |
|-------------------------|----------------|---------------------------------|
| `app_name`              | CMS Template   | Application display name        |
| `maintenance_mode`      | false          | Enable system-wide maintenance  |
| `registration_enabled`  | true           | Allow public self-registration  |

## 🔌 API Endpoints

### Auth (`/api/v1/auth`)

| Method | Path              | Auth | Description                    |
|--------|-------------------|------|--------------------------------|
| POST   | `/login`          | ✗    | Login & get JWT tokens         |
| POST   | `/register`       | ✗    | Self-register new account      |
| POST   | `/refresh`        | ✗    | Refresh access token           |
| POST   | `/logout`         | ✓    | Revoke current session         |
| GET    | `/me`             | ✓    | Get current user profile       |
| PUT    | `/me/profile`     | ✓    | Update profile (name, email)   |
| PUT    | `/me/password`    | ✓    | Change password                |
| POST   | `/me/avatar`      | ✓    | Upload avatar                  |
| GET    | `/sessions`       | ✓    | List all active sessions       |
| DELETE | `/sessions/{id}`  | ✓    | Revoke specific session        |
| POST   | `/forgot-password`| ✗    | Send password reset email      |

### Users (`/api/v1/users`)

| Method | Path          | Permission     | Description          |
|--------|---------------|----------------|----------------------|
| GET    | `/`           | `users.view`   | List users (paginated) |
| POST   | `/`           | `users.create` | Create user          |
| PUT    | `/{id}`       | `users.update` | Update user          |
| DELETE | `/{id}`       | `users.delete` | Delete user          |

### Roles (`/api/v1/roles`)

| Method | Path              | Permission     | Description           |
|--------|-------------------|----------------|-----------------------|
| GET    | `/`               | `roles.view`   | List roles (paginated) |
| GET    | `/permissions`    | `roles.view`   | List all permissions  |
| GET    | `/{id}`           | `roles.view`   | Get role detail       |
| POST   | `/`               | `roles.create` | Create role           |
| PUT    | `/{id}`           | `roles.update` | Update role           |
| DELETE | `/{id}`           | `roles.delete` | Delete role           |

### Audit (`/api/v1/audit`)

| Method | Path | Permission   | Description               |
|--------|------|--------------|---------------------------|
| GET    | `/`  | `audit.view` | List audit logs (paginated) |

### Notifications (`/api/v1/notifications`)

| Method | Path            | Auth | Description              |
|--------|-----------------|------|--------------------------|
| GET    | `/`             | ✓    | List user notifications  |
| GET    | `/unread-count` | ✓    | Get unread badge count   |
| PUT    | `/{id}/read`    | ✓    | Mark single as read      |
| PUT    | `/read-all`     | ✓    | Mark all as read         |

### Media (`/api/v1/media`)

| Method | Path       | Auth | Description               |
|--------|------------|------|---------------------------|
| POST   | `/upload`  | ✓    | Upload file (multipart)   |

### Settings (`/api/v1/settings`)

| Method | Path       | Permission        | Description         |
|--------|------------|-------------------|---------------------|
| GET    | `/`        | `settings.view`   | Get all settings    |
| PUT    | `/`        | `settings.update` | Update settings     |
| GET    | `/public`  | ✗                 | Public settings     |

### WebSocket

| Path                         | Description                  |
|------------------------------|------------------------------|
| `ws://localhost:8000/api/v1/ws/notifications` | Real-time notification push |

## 🧪 Testing

Tests use **SQLite in-memory** database for speed and isolation — your real database is never touched.

```bash
# Run all tests
pytest -v

# Run specific module
pytest -v tests/integration/test_auth.py

# Run with output
pytest -v -s
```

**Test coverage**: 23 integration tests across 7 modules (Auth, Users, Roles, Audit, Notifications, Media, Settings).

## 🛡 Middleware

| Middleware         | Description                                          |
|--------------------|------------------------------------------------------|
| CORS               | Configurable allowed origins via `CORS_ORIGINS`     |
| Request Logging    | Logs 4xx/5xx with request ID, IP, path              |
| Maintenance Mode   | Blocks non-admin requests when `maintenance_mode=true` |

## 📂 Storage Modes

Configured via `STORAGE_MODE` in `.env`:

| Mode             | Description                                       |
|------------------|---------------------------------------------------|
| `local_project`  | Save to `./storage/uploads/` (default)           |
| `local_system`   | Save to absolute path (`SYSTEM_STORAGE_PATH`)    |
| `cloud`          | Placeholder for S3/GCS (falls back to local)     |

## 🔧 Adding a New Module

1. Create folder under `app/modules/your_module/`
2. Add subdirectories: `controllers/`, `models/`, `services/`, `repositories/`, `schemas/`
3. Create `your_module_controller.py` with `router = APIRouter(prefix="/api/v1/your-module")`
4. The auto-discovery in `app/modules/__init__.py` will automatically register it

No manual registration in `main.py` required.
