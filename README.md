# CMS Template — Premium Full-Stack Boilerplate

A professional, high-performance CMS boilerplate built with **FastAPI** (Python) and **Vue 3** (JavaScript). Designed with premium aesthetics, robust security (RBAC), and modern development workflows (Alembic).

## 🏗 Architecture

```
template-cms/
├── fastapi-backend/       # REST API (RBAC, Audit, Alembic, Storage)
│   └── alembic/           # Database migration history
└── vue3-frontend/         # SPA Dashboard (Pinia, Tailwind, Premium UI)
```

## 🚀 Quick Start

### Prerequisites
- **Python** ≥ 3.11
- **Node.js** ≥ 18 LTS
- **MySQL** ≥ 8.0

### 1. Setup Backend
```bash
cd fastapi-backend
cp .env.example .env        # Edit database credentials
pip install -r requirements.txt

# Database Setup
python -m app.seeds.seed    # Initial tables & master data
alembic upgrade head        # Apply latest migrations

# Run Server
uvicorn main:app --reload   # API runs at http://localhost:8000
```

### 2. Setup Frontend
```bash
cd vue3-frontend
npm install
npm run dev                 # App runs at http://localhost:5173
```

### 3. Default Credentials
| Username     | Password   | Role         |
|--------------|------------|--------------|
| `superadmin` | `admin123` | Super Admin  |
| `admin`      | `admin123` | Admin        |

## 📦 Tech Stack

- **Backend**: FastAPI, SQLAlchemy 2.0, Alembic (Migrations), Pydantic v2, JWT, Bcrypt.
- **Frontend**: Vue 3 (Composition API), Vite, Tailwind CSS, Pinia, Lucide Icons.
- **Database**: MySQL/MariaDB (WIB Local Time standardized).
- **Real-time**: Hybrid WebSocket + Polling fallback.

## 🔐 Core Features

- **Standardized UI**: Unified "Audit Log Style" filters, premium cards, and glassmorphism headers.
- **RBAC**: Granular Permission-Based Access Control with a visual matrix editor.
- **Audit Trail**: Detailed action tracking with JSON payload diffing.
- **WIB Local Time**: All timestamps (`created_at`, `updated_at`) are automatically handled in WIB (UTC+7).
- **Media System**: Organized YYYY/MM storage with support for large file handling.
- **Active Sessions**: Monitor and revoke active user sessions in real-time.
- **Maintenance Mode**: One-click maintenance toggle with real-time broadcast to all users.

## 📖 Documentation
- [Backend Deep-Dive](./fastapi-backend/README.md)
- [Frontend Deep-Dive](./vue3-frontend/README.md)
- **API Docs**: `http://localhost:8000/docs`

## 🏷 Versioning
Version is managed centrally in `fastapi-backend/app/core/config.py`. The frontend automatically syncs this version via the public settings API.

## 📝 License
Internal template — not for public distribution.
