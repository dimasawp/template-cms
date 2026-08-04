# Plan Production-Ready + Nginx (dev-* versioned)

> Prefix `dev-` = file ini **di-push ke GitHub** (versioned).
> File `plan-*.md` lain tidak di-push (gitignored).

---

## 1. Gambaran & Keputusan

### Arsitektur Target

Saat ini semua service jalan langsung (Vite dev server + uvicorn). Target production:

```
Browser ──► :80/:443 nginx ────────────────────────────────────┐
   ├── admin.example.com   │ /admin/*  → admin SPA (static dist)   │
   ├── public.example.com  │ /public/* → public SPA (static dist)  │
   ├── api.example.com     │ /api/*    → backend proxy             │
   ├── /api/v1/ws/*                   → backend (WebSocket upgrade) │
   └── /storage/*                     → nginx serve dari volume    │
                                 ┌── backend (uvicorn, workers)
                                 └── db (container ATAU eksternal)
```

### Tabel Pilihan Skenario

| Kategori | Pilihan | Lokasi Detail |
|----------|---------|---------------|
| Domain | **A** Subdomain · **B** Satu Domain+Path · **C** Staging via Port | Bagian 2 |
| HTTPS | **H1** HTTP polos · **H2** Self-signed · **H3** Let's Encrypt | Bagian 3 |
| Database | **D1** MySQL Container · **D2** Eksternal/Managed DB | Bagian 4 |

---

## ★ Cara Menggunakan Plan Ini

Plan ini **skenario-agnostik**: dibangun sekali, dipakai berbagai kasus.

1. **Pilih 1 skenario domain**: `A` | `B` | `C`
2. **Pilih 1 skenario HTTPS**: `H1` | `H2` | `H3`
3. **Pilih 1 skenario database**: `D1` | `D2`

→ Kombinasi valid: `A+H2+D1`, `B+H3+D2`, `C+H1+D1`, dst.
   (semua kombinasi didukung, tidak ada pasangan terlarang)

### Langkah Eksekusi (untuk AI/Developer)

1. Baca bagian 2, 3, 4 → tentukan skenario (contoh: `A`, `H3`, `D1`)
2. Sampaikan ke AI: "pakai Skenario A, H3, D1"
3. AI mengerjakan **Fase Implementasi (bagian 5)** — file dibangun lengkap
   untuk mendukung SEMUA skenario. Yang berubah antar skenario hanya:
   - Env value: `SITE_MODE`, `DOMAIN`, `VITE_BASE_PATH`, `NGINX_HTTP/HTTPS_PORT`, `DB_HOST`
   - Template konfigurasi nginx yang dipakai (A/B/C)
4. Verifikasi dengan runbook (bagian 6) sesuai skenario.

| Skenario | Env / Konfigurasi yang Dipakai |
|----------|--------------------------------|
| A | `SITE_MODE=subdomain`, template `subdomain.conf` |
| B | `SITE_MODE=single`, template `single-domain.conf`, `VITE_BASE_PATH=/admin`, `/public` |
| C | `NGINX_HTTP_PORT=8080`, `NGINX_HTTPS_PORT=8443` |
| H1 | Skip semua bagian TLS/certbot |
| H2 | `scripts/gen-selfsigned.sh` |
| H3 | `scripts/init-letsencrypt.sh` + service certbot |
| D1 | `docker compose --profile local-db` |
| D2 | `DB_HOST=<ip-managed-db>`, tanpa profile db |

---

## 2. Skenario Domain (pilih SATU)

### Skenario A — Subdomain

```
admin.example.com    → admin SPA
public.example.com   → public SPA
api.example.com      → backend API + WebSocket + /storage
```

- **Env**: `SITE_MODE=subdomain`, `DOMAIN=example.com`
- **Nginx**: template `subdomain.conf.template`
- **Vue Router**: base tetap `/` (tidak perlu ubah)
- **Kebutuhan**: DNS (3 A record) + cert wildcard `*.example.com` atau SAN

### Skenario B — Satu Domain + Path

```
example.com/admin/    → admin SPA (base /admin/)
example.com/public/   → public SPA (base /public/)
example.com/api/      → backend API + WebSocket + /storage
example.com/          → redirect ke /public/
```

- **Env**: `SITE_MODE=single`, `DOMAIN=example.com`, `VITE_BASE_PATH=/admin/` & `/public/`
- **Nginx**: template `single-domain.conf.template`
- **Vue Router**: `base` di-set saat build (Fase 1.4)
- **Kebutuhan**: 1 DNS + 1 cert saja

### Skenario C — Staging via Port (non-80/443)

```
localhost:8080   → HTTP (staging internal)
localhost:8443   → TLS self-signed (opsional)
```

- **Env**: `NGINX_HTTP_PORT=8080`, `NGINX_HTTPS_PORT=8443`, `SITE_MODE=single` (atau A)
- **Nginx**: sama dengan A/B, hanya `listen` port non-standar
- **Guna**: test internal sebelum domain publik

---

## 3. Skenario HTTPS (gabung dengan domain mana pun)

### H1 — HTTP Polos

- Nginx `listen 80` saja, tanpa TLS.
- Cocok: internal / LAN / belum ada domain.
- **Skip**: semua bagian certbot/self-signed.

### H2 — Self-signed TLS

- `listen 443 ssl` + cert dari `scripts/gen-selfsigned.sh` (openssl).
- Cocok: staging.
- Peringatan browser "not secure" → wajar untuk internal.

### H3 — Let's Encrypt (auto-renew)

- `listen 80` (redirect) + `listen 443 ssl`.
- Certbot container + `scripts/init-letsencrypt.sh` (issuance awal) + renewal hook reload nginx.
- Kebutuhan: domain publik valid + port 80/443 terbuka ke internet.

---

## 4. Skenario Database (pilih SATU)

### D1 — MySQL Container

- Jalankan: `docker compose --profile local-db up -d`
- Volume `db_data` + backup via `scripts/backup-db.sh`.

### D2 — Eksternal/Managed DB

- Tanpa profile `db` (container db tidak dibuat).
- Set `DB_HOST=<host-managed>`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`.
- Backend konek langsung ke managed DB (RDS/CloudSQL/dll).

---

## 5. Fase Implementasi (skenario-agnostik)

### Fase 1 — Frontend Production Builds (Multi-stage)

| Task | Status | File | Detail |
|------|--------|------|--------|
| 1.1 | ✅ | `vue3-frontend/Dockerfile.prod` | Stage 1: `node:18-alpine` `npm ci && npm run build`. Stage 2: `nginx:alpine` copy `dist/` ke `/usr/share/nginx/html/` |
| 1.2 | ✅ | `vue3-public-frontend/Dockerfile.prod` | Sama, untuk public FE |
| 1.3 | ✅ | `vue3-public-frontend/.dockerignore` | Exclude `node_modules`, `dist` (admin & backend sudah punya) |
| 1.4 | ✅ | `vite.config.js` kedua FE | `base: process.env.VITE_BASE_PATH || '/'` — dibutuhkan skenario B |
| 1.5 | ✅ | `.env.prod.example` | `VITE_BASE_PATH` per service |

### Fase 2 — Nginx Service

| Task | Status | File | Detail |
|------|--------|------|--------|
| 2.1 | ✅ | `nginx/Dockerfile` | `nginx:1.27-alpine`, entrypoint envsubst |
| 2.2 | ✅ | `nginx/nginx.conf` | worker auto, gzip, `client_max_body_size 20m`, log format |
| 2.3 | ✅ | `nginx/snippets/proxy_common.conf` | upstream backend + `location /api/` + `location /api/v1/ws/` (Upgrade) + `location /storage/` (alias, immutable) |
| 2.4 | ✅ | `nginx/templates/subdomain.conf.template` | Server blocks admin/public/api + SPA fallback |
| 2.5 | ✅ | `nginx/templates/single-domain.conf.template` | Satu block: `/admin/`, `/public/`, `/api/`, `/api/v1/ws/`, `/storage/` |
| 2.6 | ✅ | `nginx/templates/ssl.conf.template` | 443 ssl + HTTP→HTTPS redirect, envsubst cert paths |
| 2.7 | ✅ | `nginx/entrypoint.sh` | Select template by `SITE_MODE`, envsubst `DOMAIN`, `CERT_*`, `NGINX_*PORT` |
| 2.8 | ✅ | `nginx/conf.d/security-headers.conf` | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` (CSP longgar karena Jodit) |
| 2.9 | ✅ | Skenario C | Dukungan `NGINX_HTTP_PORT` / `NGINX_HTTPS_PORT` di template |

### Fase 3 — Compose Production

| Task | Status | File | Detail |
|------|--------|------|--------|
| 3.1 | ✅ | `docker-compose.prod.yml` | Service `nginx` (port 80/443, volume storage ro + certs), backend prod, frontends prod |
| 3.2 | ✅ | DB dual-mode | Service `db` pakai `profiles: ["local-db"]` |
| 3.3 | ✅ | Shared volume | `storage` di-mount nginx (ro) + backend (rw) |
| 3.4 | ✅ | Healthcheck & restart | `restart: unless-stopped`, healthcheck nginx |

### Fase 4 — Config & Secrets

| Task | Status | Detail |
|------|--------|--------|
| 4.1 | ✅ | `.env.prod.example` — `ENV=production`, `DEBUG=false`, `ENABLE_WEBSOCKETS=true`, `SECRET_KEY` kuat, `CORS_ORIGINS` |
| 4.2 | ✅ | Backend command prod: `uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers` |
| 4.3 | ✅ | Verifikasi `ENV=production` memblokir `seed --reset` |

### Fase 5 — Ops Tooling

| Task | Status | File | Detail |
|------|--------|------|--------|
| 5.1 | ✅ | `scripts/init-letsencrypt.sh` | Issuance awal certbot webroot + reload hook |
| 5.2 | ✅ | `scripts/backup-db.sh` | `mysqldump` + rotasi |
| 5.3 | ✅ | `scripts/gen-selfsigned.sh` | Generate self-signed cert (H2) |
| 5.4 | ✅ | Compose service `certbot` | Auto-renew (H3) |

### Fase 6 — Documentation (`docs/05-deployment.md`)

| Task | Status | Detail |
|------|--------|--------|
| 6.1 | ✅ | Diagram arsitektur prod |
| 6.2 | ✅ | Panduan pilih skenario domain (A/B/C) |
| 6.3 | ✅ | Panduan pilih HTTPS (H1/H2/H3) |
| 6.4 | ✅ | Panduan DB container vs eksternal (D1/D2) |
| 6.5 | ✅ | Runbook: build, deploy, update, rollback, backup, troubleshoot |

---

## 6. Runbook (per skenario)

### 6a. Build & Deploy

```bash
# Skenario A + H3 + D1
cp .env.prod.example .env.prod   # isi sesuai skenario
docker compose --env-file .env.prod -f docker-compose.prod.yml \
  --profile local-db up -d --build

# Ops harian
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f --tail 100 nginx
docker compose --env-file .env.prod -f docker-compose.prod.yml down        # stop, data aman
docker compose --env-file .env.prod -f docker-compose.prod.yml down -v     # + hapus volume (hati-hati)

# Alias shortcut (tambah ke ~/.bashrc)
#   cms-up / cms-restart / cms-down / cms-logs / cms-ps
#   (lihat docs/05-deployment.md → Common Commands)
```

### 6b. Update & Rollback

```bash
# Restart semua (mis. setelah .env.prod diubah)
docker compose --env-file .env.prod -f docker-compose.prod.yml restart
# Restart satu service
docker compose --env-file .env.prod -f docker-compose.prod.yml restart nginx

# Update: pull source lalu rebuild image yang berubah
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build backend frontend public_frontend

# Rollback: checkout commit lama lalu up -d --build
```

### 6c. Backup & Restore

```bash
# Backup (mode D1)
./scripts/backup-db.sh
# Restore
docker exec -i cms_db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" '"${DB_NAME}" < backup.sql
```

### 6d. Troubleshoot

| Gejala | Kemungkinan & Fix |
|--------|-------------------|
| WS realtime putus | Lupa `proxy_set_header Upgrade/Connection` di nginx (Fase 2.3) |
| Upload > limit | `client_max_body_size` terlalu kecil (Fase 2.2) |
| SPA 404 di refresh | `try_files $uri $uri/ /index.html` hilang |
| Cert expired | Renewal hook gagal / port 80 tertutup |
| 502 di /api | backend container down → cek `docker compose ps backend` |
| B layout rusak | `VITE_BASE_PATH` tidak di-set saat build |

---

## ★ Verifikasi Pending

> Belum jalan: Docker daemon WSL DOWN (butuh `sudo` interaktif).
> Begitu daemon nyala, jalankan validasi build + `nginx -t`:

```bash
# 1. Validasi komposisi service (sudah lolos sebelumnya — konfirmasi ulang)
wsl -d Ubuntu docker compose -f docker-compose.prod.yml --profile local-db config >/dev/null

# 2. Build image nginx lalu test konfigurasi yang sudah di-render
wsl -d Ubuntu docker build -f nginx/Dockerfile -t cms-nginx-test nginx/
wsl -d Ubuntu docker run --rm -e SITE_MODE=subdomain -e NGINX_HTTPS=true \
  -e DOMAIN=example.com -e CERT_FILE=/etc/letsencrypt/live/example.com/fullchain.pem \
  -e CERT_KEY=/etc/letsencrypt/live/example.com/privkey.pem \
  cms-nginx-test nginx -t

# Hasil yang diharapkan: "syntax is ok" + "test is successful"
```

Jika daemon mati lagi: `wsl -d Ubuntu sudo service docker start` (interaktif).

---

## 7. Lampiran

### Vite / Vue Router Base Path

- `createWebHistory(import.meta.env.BASE_URL)` sudah dipakai kedua FE.
- `BASE_URL` berasal dari `base` di vite.config.js → `VITE_BASE_PATH` (Fase 1.4).
- Skenario A (subdomain): `VITE_BASE_PATH=/` (default).
- Skenario B (path): `VITE_BASE_PATH=/admin/` dan `/public/`.

### Env Reference Lengkap

Lihat `.env.prod.example` (Fase 4.1) setelah diimplementasikan.
