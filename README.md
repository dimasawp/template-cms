# CMS Template — Premium Full-Stack Boilerplate

A professional, high-performance CMS boilerplate built with **FastAPI** (Python) and **Vue 3** (JavaScript). Designed with premium aesthetics, robust security (RBAC), and modern development workflows (Alembic).

## 🏗 Architecture

```
template-cms/
├── fastapi-backend/       # REST API (RBAC, Audit, Alembic, Storage)
│   └── db/                # Database tools (migrations, seeds, scripts)
└── vue3-frontend/         # SPA Dashboard (Pinia, Tailwind, Premium UI)
```


## 🧩 Modular Architecture (Core + Extensions)

This CMS is designed using Domain-Driven Design (DDD) to be highly modular. Features can be easily uninstalled if a specific project doesn't need them.

- **Core Modules** (Cannot be disabled): `auth`, `users`, `roles`, `settings`, `audit`.
- **Extension Modules**: `posts`, `categories`, `public`.

### How to Disable/Uninstall an Extension:
1. **Backend:** Open `fastapi-backend/app/core/extensions.py` and comment out the module name from the `ENABLED_EXTENSIONS` list.
2. **Frontend:** Open `vue3-frontend/src/config/modules.js` and comment out or remove the module block from the `extensionModules` list. This will hide it from the Sidebar.
3. **Apply Changes:** Jika Anda menjalankan aplikasi menggunakan Docker, Anda wajib melakukan *rebuild* agar perubahan file konfigurasi terbaca oleh sistem:
   ```bash
   docker compose up -d --build backend frontend
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
python -m db.seeds.seed --sync  # Idempotent seed (roles, permissions, users, settings)
alembic upgrade head  # Apply latest migrations (from project root)
cd ..

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

## 🐳 Docker Deployment

The project is fully dockerized. To start everything (Database, Backend, Frontend):

```bash
docker compose up -d --build
```
- **Backend API**: `http://localhost:8000`
- **Frontend Dashboard**: `http://localhost:5173`

### Database Reset (Clean Wipe)
If you want to completely empty the database and re-seed it with default data (e.g., during development), run these commands:

```bash
# 1. Drop and Recreate the database inside the MySQL container
docker compose exec db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "DROP DATABASE IF EXISTS $DB_NAME; CREATE DATABASE $DB_NAME"'

# 2. Re-create all tables and insert default seed data
docker compose exec backend python -m db.seeds.seed --reset

# 3. Tell Alembic that the database is already up to date
docker compose exec backend alembic stamp head
```

> **Note:** Use `--sync` (default) for idempotent seeding — never drops tables, safe for staging/production.  
> Use `--reset` to drop & recreate tables (development only — blocked in production unless `--force` is passed).

### Applying Code Changes (Rebuild)
Because the application runs entirely inside Docker without code bind mounts in production/default setup, you must rebuild the containers when you edit the source code.

```bash
# Rebuild Backend container (FastAPI) after editing Python code:
docker compose up -d --build backend

# Rebuild Frontend container (Vue) after editing JS/Vue code:
docker compose up -d --build frontend

# Rebuild Public Frontend container (Vue) after editing JS/Vue code:
docker compose up -d --build public_frontend
```

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
- **CAPTCHA Protection**: Built-in CAPTCHA module for login/register forms with global toggle in Settings.

## 📖 Documentation
- [Backend Deep-Dive](./fastapi-backend/README.md)
- [Frontend Deep-Dive](./vue3-frontend/README.md)
- **API Docs**: `http://localhost:8000/docs`

## 🏷 Versioning
Version is managed centrally in `fastapi-backend/app/core/config.py`. The frontend automatically syncs this version via the public settings API.

## 📝 License
Internal template — not for public distribution.
