# CMS Template

Reusable full-stack CMS boilerplate built with **FastAPI** (Python) and **Vue 3** (TypeScript). Designed to be cloned and extended for any administrative dashboard project.

## 🏗 Architecture

```
template-cms/
├── fastapi-backend/       # REST API, Auth, RBAC, Audit, Media
├── vue3-frontend/         # SPA Admin Dashboard
└── storage/               # Shared file uploads (gitignored)
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
- **Audit Trail**: Tracks all user actions (create, update, delete)
- **Media Upload**: Multi-storage support (local project, local system, cloud-ready)
- **Notifications**: Real-time via WebSocket, in-app notification center
- **Global Settings**: App name, maintenance mode, registration toggle
- **Active Sessions**: View and revoke user login sessions
- **Maintenance Mode**: Toggle system-wide with admin bypass
- **Dark/Light Theme**: Persistent matte-dark design system
- **Component Gallery**: Built-in UI documentation page at `/components`

## 📖 Documentation

- **Backend README**: [`fastapi-backend/README.md`](./fastapi-backend/README.md)
- **Frontend README**: [`vue3-frontend/README.md`](./vue3-frontend/README.md)
- **API Docs (Swagger)**: `http://localhost:8000/docs` (after starting backend)

## 📝 License

Internal template — not for public distribution.
