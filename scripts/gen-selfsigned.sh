#!/usr/bin/env bash
# =============================================================
# H2 — Generate self-signed SSL certificate (via container nginx)
#
# Prasyarat: nginx container sudah jalan dalam mode HTTP (H1).
#   NGINX_HTTPS=false  →  up compose   →  jalankan skrip ini
#   lalu set NGINX_HTTPS=true  →  restart nginx
# =============================================================
set -euo pipefail

# Variabel bisa di-override dari .env.prod / environment
DOMAIN="${DOMAIN:-localhost}"
NGINX_CONTAINER="cms_nginx"
DAYS="${CERT_DAYS:-365}"

if ! docker exec "$NGINX_CONTAINER" true 2>/dev/null; then
  echo "ERROR: container '${NGINX_CONTAINER}' tidak berjalan." >&2
  echo "Jalankan dulu compose dalam mode HTTP (NGINX_HTTPS=false)." >&2
  exit 1
fi

# Buat cert di dalam container yang me-mount volume certbot_certs
docker exec "$NGINX_CONTAINER" sh -c "
  mkdir -p '/etc/letsencrypt/live/${DOMAIN}' &&
  openssl req -x509 -nodes -newkey rsa:2048 -days '${DAYS}' \
    -keyout '/etc/letsencrypt/live/${DOMAIN}/privkey.pem' \
    -out '/etc/letsencrypt/live/${DOMAIN}/fullchain.pem' \
    -subj '/CN=${DOMAIN}' \
    -addext 'subjectAltName=DNS:${DOMAIN},DNS:*.${DOMAIN}' \
    -addext 'basicConstraints=critical,CA:FALSE' \
    -addext 'keyUsage=critical,digitalSignature,keyEncipherment' \
    -addext 'extendedKeyUsage=serverAuth'
"

echo "Self-signed cert dibuat untuk '${DOMAIN}'."
echo "Langkah berikutnya:"
echo "  1) Set NGINX_HTTPS=true di .env.prod"
echo "  2) docker compose --env-file .env.prod -f docker-compose.prod.yml up -d"