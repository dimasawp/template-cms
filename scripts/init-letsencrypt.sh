#!/usr/bin/env bash
# =============================================================
# H3 — Let's Encrypt: issuance sertifikat pertama (certonly)
# Setelah berhasil, jalankan compose dengan --profile letsencrypt
# agar certbot renew otomatis tiap 12 jam.
#
# Prasyarat:
#  - DNS domain sudah mengarah ke server (A Record)
#  - nginx container jalan dalam mode HTTP (NGINX_HTTPS=false),
#    agar challenge /.well-known/acme-challenge/ bisa dilayani.
# =============================================================
set -euo pipefail

# Mutlak harus diisi
DOMAIN="${DOMAIN:-example.com}"
EMAIL="${LE_EMAIL:?Set LE_EMAIL=<email> di .env.prod (untuk renew notice)}"

# Volume (nama mengikuti project name "cms-prod")
CERTS_VOL="cms-prod_certbot_certs"
WEBROOT_VOL="cms-prod_certbot_webroot"

# Subdomain yang disertakan
DOMAINS=( "${DOMAIN}" "www.${DOMAIN}" "api.${DOMAIN}" "admin.${DOMAIN}" "public.${DOMAIN}" )

ARGS=()
for d in "${DOMAINS[@]}"; do
  ARGS+=( -d "${d}" )
done

echo "Meminta sertifikat untuk: ${DOMAINS[*]}"
docker run --rm \
  -v "${CERTS_VOL}:/etc/letsencrypt" \
  -v "${WEBROOT_VOL}:/var/www/certbot" \
  certbot/certbot certonly \
  --webroot -w /var/www/certbot \
  "${ARGS[@]}" \
  --email "${EMAIL}" \
  --agree-tos --no-eff-email --keep-until-expiring

echo ""
echo "Sertifikat berhasil dibuat."
echo "Langkah berikutnya:"
echo "  1) Set NGINX_HTTPS=true di .env.prod"
echo "  2) docker compose --env-file .env.prod -f docker-compose.prod.yml --profile letsencrypt up -d"
echo "     (certbot container ikut jalan & auto-renew tiap 12 jam)"