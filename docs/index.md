# CMS Template Documentation

> Professional full-stack CMS boilerplate built with **FastAPI** (Python) and **Vue 3** (JavaScript).

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, JWT, Bcrypt |
| Frontend (Admin) | Vue 3 (Composition API), Vite, Pinia, Vue Router, Tailwind CSS, Lucide Icons, Jodit |
| Frontend (Public) | Vue 3, Vite, axios |
| Database | MySQL 8.0 / MariaDB |
| Deployment | Docker Compose (4 services) |
| Real-time | WebSocket + Polling fallback |

## Project Structure

```
template-cms/
├── fastapi-backend/          # REST API (RBAC, Audit, DB tools)
│   ├── app/                  # Application code (core, modules, helpers)
│   ├── db/                   # Database tools (migrations, seeds, scripts)
│   ├── tests/                # Integration & unit tests
│   ├── storage/              # File uploads
│   └── main.py               # Entry point
├── vue3-frontend/            # Admin SPA Dashboard
├── vue3-public-frontend/     # Public-facing SPA
├── docker-compose.yml        # Docker orchestration
└── docs/                     # Documentation
```

## Quick Links

| Document | Description |
|---|---|
| [01-architecture.md](01-architecture.md) | System architecture, backend layers, frontend layers, DB schema |
| [02-module-development.md](02-module-development.md) | **[KEY]** Step-by-step guide to create a new module |
| [03-api.md](03-api.md) | Authentication, all endpoints, response format, error handling |
| [04-database.md](04-database.md) | Migrations, seeding, reset procedures |
| [05-deployment.md](05-deployment.md) | Docker setup, env vars, production checklist |
| [06-testing.md](06-testing.md) | Backend & frontend testing guide |
| [07-adr.md](07-adr.md) | Architecture Decision Records |

## Default Credentials

| Username | Password | Role |
|---|---|---|
| `superadmin` | `admin123` | Super Admin |
| `admin` | `admin123` | Admin |

## Quick Start

```bash
# Backend
cd fastapi-backend
cp .env.example .env
pip install -r requirements.txt
python -m db.seeds.seed --sync
alembic upgrade head

# Frontend
cd vue3-frontend
npm install
npm run dev

# Or Docker (all services)
cd .. && docker compose up -d --build
```
