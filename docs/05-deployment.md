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

### 5. Production (nginx Reverse Proxy)

For production, use the dedicated `docker-compose.prod.yml` (standalone — does **not** reference the dev compose). It adds an **nginx** service that reverse-proxies the frontends and backend, plus optional MySQL container and certbot auto-renew.

```
template-cms/
├── .env.prod.example     # (tracked) Production config template
├── .env.prod             # (gitignored) Your real production config
├── docker-compose.prod.yml
├── nginx/                # Reverse proxy image
├── scripts/
│   ├── gen-selfsigned.sh # H2 — self-signed cert
│   ├── init-letsencrypt.sh # H3 — Let's Encrypt first issuance
│   └── backup-db.sh      # D1 — database backup + rotation
└── ...
```

**Start (D1 — MySQL container):**

```bash
cp .env.prod.example .env.prod
# edit .env.prod
docker compose --env-file .env.prod -f docker-compose.prod.yml --profile local-db up -d --build
```

**Start (D2 — external/managed DB):** omit `--profile local-db` and set `DB_HOST`/`DB_PORT` in `.env.prod`.

**Stop:** `docker compose --env-file .env.prod -f docker-compose.prod.yml down`

**Project name:** fixed to `cms-prod` so it never collides with the dev compose.

#### Common Commands (production)

All commands target the prod compose. Plain `docker compose ...` (without `-f`) only touches the **dev** `docker-compose.yml` — it will **not** restart the prod nginx.

```bash
# Status & logs
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f --tail 100 nginx

# Restart all services
docker compose --env-file .env.prod -f docker-compose.prod.yml restart

# Restart one service (e.g. nginx)
docker compose --env-file .env.prod -f docker-compose.prod.yml restart nginx

# Stop / remove containers (volumes db_data_prod & certbot_* KEEP data)
docker compose --env-file .env.prod -f docker-compose.prod.yml down
# Stop + delete all volumes/data (destructive — use carefully)
docker compose --env-file .env.prod -f docker-compose.prod.yml down -v
```

**Alias shortcut** (tambahkan ke `~/.bashrc` di server):

```bash
alias cms-up='docker compose --env-file .env.prod -f docker-compose.prod.yml --profile local-db up -d --build'
alias cms-restart='docker compose --env-file .env.prod -f docker-compose.prod.yml restart'
alias cms-down='docker compose --env-file .env.prod -f docker-compose.prod.yml down'
alias cms-logs='docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f --tail 100'
alias cms-ps='docker compose --env-file .env.prod -f docker-compose.prod.yml ps'
```

> Catatan profile: tambah `--profile local-db` kalau pakai D1 (MySQL container) dan `--profile letsencrypt` kalau pakai H3 (Let's Encrypt). Tanpa profile tersebut, service `db`/`certbot` tidak ikut dijalankan.

#### Scenario A — Subdomains

| Subdomain | Serves |
|---|---|
| `admin.${DOMAIN}` | Admin SPA |
| `public.${DOMAIN}` | Public SPA |
| `api.${DOMAIN}` | Backend API + WebSocket + storage |

`SITE_MODE=subdomain`; frontends built with `VITE_BASE_PATH=/`. Set `ADMIN_VITE_BASE_PATH=/` and `PUBLIC_VITE_BASE_PATH=/` in `.env.prod`.

#### Scenario B — Single Domain + Paths

| Path | Serves |
|---|---|
| `/admin/` | Admin SPA |
| `/public/` | Public SPA |
| `/api/` | Backend API + WebSocket + storage |
| `/` | Redirect → `/public/` |

`SITE_MODE=single`; frontends built with path base. Set `ADMIN_VITE_BASE_PATH=/admin/` and `PUBLIC_VITE_BASE_PATH=/public/` in `.env.prod`.

#### Scenario C — Staging on a Single Server

Use ports instead of DNS: set `NGINX_HTTP_PORT=8080`, `NGINX_HTTPS_PORT=8443` in `.env.prod`. Everything else identical.

#### HTTPS options

| Option | Config | Setup |
|---|---|---|
| H1 — HTTP | `NGINX_HTTPS=false` | none |
| H2 — self-signed | `NGINX_HTTPS=true` | `./scripts/gen-selfsigned.sh` |
| H3 — Let's Encrypt | `NGINX_HTTPS=true` | `LE_EMAIL` + `./scripts/init-letsencrypt.sh`, run compose with `--profile letsencrypt` |

Let's Encrypt renewal: certbot container runs `certbot renew` every 12h; nginx auto-reloads every 6h to pick up new certs.

#### Database

| Option | Config |
|---|---|
| D1 — MySQL container | `DB_HOST=db`, run with `--profile local-db` |
| D2 — external/managed DB | `DB_HOST=<host>`, `DB_PORT=<port>`, omit `--profile local-db` |

Backup (D1): `./scripts/backup-db.sh` → gzipped dumps in `./backups/`, auto-rotation (default 7 days).

#### Environment Variables (`docker-compose.prod.yml`)

| Variable | Default | Description |
|---|---|---|
| `SITE_MODE` | `single` | `subdomain` (A) or `single` (B) |
| `NGINX_HTTPS` | `false` | `true` (H2/H3) or `false` (H1) |
| `DOMAIN` | `localhost` | Primary domain |
| `NGINX_HTTP_PORT` | `80` | Nginx HTTP port |
| `NGINX_HTTPS_PORT` | `443` | Nginx HTTPS port |
| `CERT_FILE` | `/etc/letsencrypt/live/${DOMAIN}/fullchain.pem` | Cert path (volume `certbot_certs`) |
| `CERT_KEY` | `/etc/letsencrypt/live/${DOMAIN}/privkey.pem` | Key path |
| `MYSQL_ROOT_PASSWORD` | `root` | MySQL root password (D1) |
| `DB_HOST` | `db` | `db` (D1) or external host (D2) |
| `DB_PORT` | `3306` | Database port |
| `DB_USER` / `DB_PASSWORD` | — | Database credentials |
| `DB_NAME` | `db_cms_template` | Database name |
| `SECRET_KEY` | `CHANGE_ME...` | JWT secret (change!) |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Allowed origins |
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | API base used at build time |
| `ADMIN_VITE_BASE_PATH` | `/` | Admin SPA base path |
| `PUBLIC_VITE_BASE_PATH` | `/` | Public SPA base path |

#### Runbook

```bash
# 1. Config
cp .env.prod.example .env.prod && vim .env.prod

# 2. First boot in HTTP mode (H1) so certs/ACME can be set up
docker compose --env-file .env.prod -f docker-compose.prod.yml --profile local-db up -d --build
docker compose --env-file .env.prod -f docker-compose.prod.yml ps   # all healthy?

# 3a. H2 — self-signed
./scripts/gen-selfsigned.sh

# 3b. H3 — Let's Encrypt (DNS must point to the server first)
LE_EMAIL=you@example.com ./scripts/init-letsencrypt.sh

# 4. Enable HTTPS (H2/H3)
#    .env.prod: NGINX_HTTPS=true  (+ LE: add --profile letsencrypt)
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d

# 5. Verify
curl -I http://${DOMAIN}/admin/          # 301 → https (H2/H3)
curl -I https://${DOMAIN}/public/        # 200
curl -I https://${DOMAIN}/api/v1/        # 200

# 6. Daily ops
./scripts/backup-db.sh                    # DB backup (cron this)
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f --tail 100
```

> On Windows with Docker in WSL, run `docker` commands and scripts inside the WSL distro (e.g. `wsl -d Ubuntu ./scripts/backup-db.sh`).

#### Troubleshooting

| Symptom | Cause / Fix |
|---|---|
| `nginx` exits at startup | `NGINX_HTTPS=true` but cert missing → run H2/H3 setup first |
| H3 challenge fails | DNS not pointing to server yet; or port 80 blocked |
| Login fails behind proxy | `CORS_ORIGINS` must match the real origin; backend runs with `--proxy-headers` |
| WebSocket won't connect | Nginx must have the `Upgrade`/`Connection` headers (already in `snippets/proxy_common.conf`) |
| Frontend blank / wrong API | `VITE_API_BASE_URL` / `VITE_BASE_PATH` are baked at **build time** → rebuild frontend |

### 6. CI/CD (Recommended)

The project currently has no CI/CD. Recommended setup:

- **GitHub Actions** for running tests on push
- **Linting**: Ruff for Python, ESLint for JavaScript
- **Pre-commit hooks**: Use `husky` + `lint-staged` for frontend
- **Build & push Docker images** to registry
- **Deploy** via SSH or Kubernetes
