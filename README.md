# CMS Template

Reusable full-stack CMS boilerplate built with **FastAPI** (Python) and **Vue 3** (TypeScript). Designed to be cloned and extended for any administrative dashboard project.

## 🏗 Architecture

```
template-cms/
├── fastapi-backend/       # REST API (RBAC, Audit, Media, Storage)
│   └── storage/           # file uploads (gitignored structure)
└── vue3-frontend/         # SPA Admin Dashboard (Pinia Settings Store)
```

## 🚀 Quick Start

### Prerequisites

| Tool       | Version    |
|------------|------------|
| Python     | ≥ 3.11     |
| Node.js    | ≥ 18 LTS   |
| MySQL      | ≥ 8.0      |

### 1. Clone & Setup Backend

```bash
cd fastapi-backend
cp .env.example .env        # Edit database credentials
pip install -r requirements.txt
python -m app.seeds.seed    # Create tables & seed data
uvicorn main:app --reload   # API runs at http://localhost:8000
```

### 2. Setup Frontend

```bash
cd vue3-frontend
cp .env.example .env
npm install
npm run dev                 # App runs at http://localhost:5173
```

### 3. Login

| Username     | Password   | Role         |
|--------------|------------|--------------|
| `superadmin` | `admin123` | Super Admin  |
| `admin`      | `admin123` | Admin        |

## 📦 Tech Stack

| Layer     | Technology                                              |
|-----------|---------------------------------------------------------|
| Backend   | FastAPI, SQLAlchemy, PyMySQL, Pydantic, JWT (python-jose) |
| Frontend  | Vue 3, TypeScript, Vite, Tailwind CSS 3, Pinia, Radix-Vue |
| Database  | MySQL 8+ (Production) · SQLite In-Memory (Testing)      |
| Testing   | Pytest + httpx (Backend) · 23 integration tests         |

## 🔐 Built-in Features

- **Authentication**: JWT access + refresh tokens, session management
- **Authorization**: Role-Based Access Control (RBAC) with granular permissions
- **User Management**: CRUD users, role assignment, profile editing
- **Role & Permission Management**: Dynamic roles with permission matrix
- **Audit Trail**: Tracks user actions; maintains immutable logs (hard delete only)
- **Media Upload**: Auto-organized by Year/Month (`YYYY/MM/`); multi-storage support
- **Soft Delete**: Integrated across key modules (Roles, Users, Media, Settings)
- **Real-time Notifications**: Hybrid WebSocket + Fallback Polling for high availability
- **Global Settings**: Site name and maintenance reactivity via central Pinia store

## 📖 Documentation

- **Backend README**: [`fastapi-backend/README.md`](./fastapi-backend/README.md)
- **Frontend README**: [`vue3-frontend/README.md`](./vue3-frontend/README.md)
- **API Docs (Swagger)**: `http://localhost:8000/docs` (after starting backend)

## 🏷 Version Management

The system uses a **Centralized Versioning** strategy:
- **Source of Truth**: The version is defined in `fastapi-backend/app/core/config.py` (`APP_VERSION`).
- **Syncing**: The backend automatically exposes this version via the Public Settings API.
- **Frontend**: The Dashboard footer and system metadata dynamically read from the backend, so you only need to update the version in one file.

## 📝 License

Internal template — not for public distribution.
