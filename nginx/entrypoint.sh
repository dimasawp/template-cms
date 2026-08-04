#!/bin/sh
set -e

SITE_MODE="${SITE_MODE:-single}"
NGINX_HTTPS="${NGINX_HTTPS:-false}"
NGINX_HTTP_PORT="${NGINX_HTTP_PORT:-80}"
NGINX_HTTPS_PORT="${NGINX_HTTPS_PORT:-443}"
DOMAIN="${DOMAIN:-localhost}"
CERT_FILE="${CERT_FILE:-/etc/letsencrypt/live/${DOMAIN}/fullchain.pem}"
CERT_KEY="${CERT_KEY:-/etc/letsencrypt/live/${DOMAIN}/privkey.pem}"

# ── Validasi SITE_MODE ──────────────────────────────────────
case "$SITE_MODE" in
  subdomain|single) ;;
  *) echo "ERROR: SITE_MODE harus 'subdomain' atau 'single' (dapat: $SITE_MODE)" >&2; exit 1 ;;
esac

# ── Validasi NGINX_HTTPS ────────────────────────────────────
case "$NGINX_HTTPS" in
  true|false) ;;
  *) echo "ERROR: NGINX_HTTPS harus 'true' atau 'false' (dapat: $NGINX_HTTPS)" >&2; exit 1 ;;
esac

if [ "$NGINX_HTTPS" = "true" ]; then
  PROTO="https"
  # Pastikan cert ada sebelum nginx start
  if [ ! -f "$CERT_FILE" ] || [ ! -f "$CERT_KEY" ]; then
    echo "WARNING: Certificate tidak ditemukan ($CERT_FILE / $CERT_KEY)."
    echo "         Jalankan scripts/gen-selfsigned.sh (H2) atau scripts/init-letsencrypt.sh (H3)."
    exit 1
  fi
  # Reload berkala supaya cert renewal (Let's Encrypt) ikut ter-load tanpa docker socket
  ( while :; do sleep 21600; nginx -s reload 2>/dev/null || true; done ) &
else
  PROTO="http"
fi

# ── Pilih & render template ─────────────────────────────────
TEMPLATE="/etc/nginx/templates/${SITE_MODE}.${PROTO}.conf.template"
if [ ! -f "$TEMPLATE" ]; then
  echo "ERROR: Template tidak ditemukan: $TEMPLATE" >&2
  exit 1
fi

export NGINX_HTTP_PORT NGINX_HTTPS_PORT DOMAIN CERT_FILE CERT_KEY

envsubst '$DOMAIN $NGINX_HTTP_PORT $NGINX_HTTPS_PORT $CERT_FILE $CERT_KEY' \
  < "$TEMPLATE" > /etc/nginx/conf.d/default.conf

echo "[nginx] SITE_MODE=$SITE_MODE PROTO=$PROTO DOMAIN=$DOMAIN ports=$NGINX_HTTP_PORT/$NGINX_HTTPS_PORT"

exec nginx -g "daemon off;"
