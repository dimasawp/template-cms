#!/usr/bin/env bash
# =============================================================
# Backup database MySQL (D1 — container cms_db)
#   Hasil: backups/db_cms_template_YYYYmmdd_HHMMSS.sql.gz
#   Rotasi otomatis: hapus backup lebih lama dari BACKUP_KEEP_DAYS
#
# Contoh cron (jalankan tiap 03:00):
#   0 3 * * * cd /path/to/template-cms && ./scripts/backup-db.sh >> backups/backup.log 2>&1
# =============================================================
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
BACKUP_KEEP_DAYS="${BACKUP_KEEP_DAYS:-7}"
DB_NAME="${DB_NAME:-db_cms_template}"
DB_CONTAINER="cms_db"

mkdir -p "${BACKUP_DIR}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
OUT_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql"

if ! docker exec "${DB_CONTAINER}" true 2>/dev/null; then
  echo "ERROR: container '${DB_CONTAINER}' tidak berjalan." >&2
  exit 1
fi

# MYSQL_ROOT_PASSWORD tersedia sebagai env di dalam container db
docker exec -e DB_NAME="${DB_NAME}" "${DB_CONTAINER}" \
  sh -c 'mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" --single-transaction --routines --triggers "$DB_NAME"' \
  > "${OUT_FILE}"

gzip -f "${OUT_FILE}"

# Rotasi backup lama
find "${BACKUP_DIR}" -name '*.sql.gz' -mtime "+${BACKUP_KEEP_DAYS}" -delete

echo "Backup selesai: ${OUT_FILE}.gz"
echo "Sisa backup: $(find "${BACKUP_DIR}" -name '*.sql.gz' | wc -l) file"