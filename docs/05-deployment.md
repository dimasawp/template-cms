# Deployment Guide

## Configuration: Root `.env`

Docker Compose reads shared variables from a root `.env` file at the project root:

```
template-cms/
├── .env              # (gitignored) Real credentials
├── .env.example      # (tracked) Template with placeholders
├── docker-compose.yml
└── ...
```

**Every variable** in `docker-compose.yml` has a `${VAR:-default}` fallback, so the system runs even without `.env`. To customise:

```bash
cp .env.example .env   # Create your config
# Edit .env — change DB_USER, DB_PASSWORD, DB_NAME, ports, etc.
docker compose up -d
```

| Variable | Default | Description |
|---|---|---|
| `MYSQL_ROOT_PASSWORD` | `root` | MySQL root password |
| `DB_USER` | `root` | Backend database user |
| `DB_PASSWORD` | `root` | Backend database password |
| `DB_NAME` | `db_cms_template` | Database name |
| `DB_HOST` | `db` | Database host (Docker service name) |
| `DB_PORT` | `3306` | Database port |
| `SECRET_KEY` | `CHANGE_ME_TO_RANDOM_SECRET_DOCKER` | JWT signing secret |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Allowed CORS origins |
| `STORAGE_MODE` | `local_project` | Storage driver |
| `BACKEND_PORT` | `8000` | Backend host port |
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | Frontend API URL |
| `FRONTEND_PORT` | `5173` | Admin SPA host port |
| `PUBLIC_FRONTEND_PORT` | `3000` | Public SPA host port |

Each service also loads its own `.env` via `env_file:` (e.g. `./fastapi-backend/.env`). Docker-specific overrides (like `DB_HOST=db`) are set in `environment:` and take precedence.

## Docker Compose (Development)

The project includes a `docker-compose.yml` at the root with 4 services:

| Service | Container Name | Image | Port | Description |
|---|---|---|---|---|
| `db` | `cms_db` | mysql:8.0 | 3306 | MySQL database |
| `backend` | `cms_backend` | Build from `./fastapi-backend` | 8000 | FastAPI REST API |
| `frontend` | `cms_frontend` | Build from `./vue3-frontend` | 5173 | Admin SPA |
| `public_frontend` | `cms_public_frontend` | Build from `./vue3-public-frontend` | 3000 | Public SPA |

### Start All Services

```bash
cp .env.example .env   # First time only
docker compose up -d --build
```

### Rebuild a Single Service

After code changes:

```bash
docker compose up -d --build backend
docker compose up -d --build frontend
docker compose up -d --build public_frontend
```

### Apply Extension Changes (Rebuild Required)

If you modify `extensions.py` or `modules.js`, you must rebuild:

```bash
docker compose up -d --build backend frontend
```

If containers don't pick up changes, force a clean build:

```bash
docker compose build --no-cache backend frontend
docker compose up -d
```

### Database Reset (Docker)

```bash
# 1. Drop & recreate (uses $MYSQL_ROOT_PASSWORD and $DB_NAME from container env)
docker compose exec db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "DROP DATABASE IF EXISTS $DB_NAME; CREATE DATABASE $DB_NAME"'

# 2. Seed (idempotent sync)
docker compose exec backend python -m db.seeds.seed --sync

# 3. Stamp Alembic
docker compose exec backend alembic upgrade head
```

## Environment Variables

### Root `.env` (Docker Compose)

See table at top of this page. Copy `.env.example` → `.env` and edit.

### Backend (`fastapi-backend/.env`)

Loaded automatically into the `backend` container via `env_file: ./fastapi-backend/.env`. Docker overrides (`DB_HOST=db`, `DB_NAME`) take precedence.

| Variable | Description | Default |
|---|---|---|
| `APP_NAME` | Application name | CMS Template |
| `APP_VERSION` | Version (syncs to frontend) | 1.2.0 |
| `ENV` | Environment: `development`, `staging`, `production` | development |
| `SECRET_KEY` | JWT signing secret | (required) |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | 7 |
| `DB_HOST` | Database host (local dev) | localhost |
| `DB_PORT` | Database port | 3306 |
| `DB_USER` | Database user | root |
| `DB_PASSWORD` | Database password | (required) |
| `DB_NAME` | Database name (local dev) | db_cms_template |
| `CORS_ORIGINS` | Allowed CORS origins | http://localhost:5173,http://localhost:3000 |
| `STORAGE_MODE` | Storage driver: `local_project`, `local_system` | local_project |
| `STORAGE_LOCAL_PATH` | Local storage path | storage/uploads |
| `MAIL_HOST` | SMTP host | (optional) |
| `MAIL_PORT` | SMTP port | 587 |
| `MAIL_USERNAME` | SMTP username | (optional) |
| `MAIL_PASSWORD` | SMTP password | (optional) |
| `MAIL_FROM` | Sender email | (optional) |

### Frontend Admin (`vue3-frontend/.env`)

| Variable | Description | Default |
|---|---|---|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8000/api/v1` |

### Frontend Public (`vue3-public-frontend/.env`)

| Variable | Description | Default |
|---|---|---|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8000/api/v1` |

## Production Checklist

### 1. Security

- [ ] Change `SECRET_KEY` to a random strong value
- [ ] Change database passwords (root and application user)
- [ ] Set `ENV=production` (disables table dropping during seed)
- [ ] Set `CORS_ORIGINS` to the actual frontend domain(s)
- [ ] Set proper `MAIL_*` config for password reset emails
- [ ] Use HTTPS (reverse proxy with nginx/traefik)

### 2. Database

- [ ] Use a managed MySQL/MariaDB service or dedicated DB container
- [ ] Set up regular backups
- [ ] Run `alembic upgrade head` as part of deployment process
- [ ] Only run seed with `--sync` in production (safe, never drops tables). `--reset` is blocked in production unless `--force` is passed.

### 3. Performance

- [ ] Increase `uvicorn` workers: `uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000`
- [ ] Add Redis caching for permission checks (high traffic)
- [ ] Configure CDN for uploaded media files
- [ ] Set up database query optimization (index review)

### 4. Monitoring

- [ ] Set up health check endpoint (`GET /` returns `{"status":"running"}`)
- [ ] Configure logging aggregation
- [ ] Monitor slow queries

### 5. Docker in Production

For production, prepare a separate `.env` (or `.env.prod`) and reference it:

```bash
docker compose --env-file .env.prod up -d --build
```

Or use a production override file:

```yaml
# docker-compose.prod.yml
services:
  backend:
    build: ./fastapi-backend
    restart: always
    environment:
      - ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - DB_PASSWORD=${DB_PASSWORD}
      - CORS_ORIGINS=https://admin.yourdomain.com

  frontend:
    build: ./vue3-frontend
    environment:
      - VITE_API_BASE_URL=https://api.yourdomain.com/api/v1
```

### 6. CI/CD (Recommended)

The project currently has no CI/CD. Recommended setup:

- **GitHub Actions** for running tests on push
- **Linting**: Ruff for Python, ESLint for JavaScript
- **Pre-commit hooks**: Use `husky` + `lint-staged` for frontend
- **Build & push Docker images** to registry
- **Deploy** via SSH or Kubernetes
