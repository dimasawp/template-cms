# Database Guide

## Overview

The system uses **MySQL 8.0** with **SQLAlchemy 2.0** as ORM and **Alembic** for migrations. All timestamp fields use **WIB (UTC+7)**.

Database configuration is in `app/core/config.py` (loaded from `.env`).

## Project Structure

Database-related files are consolidated under `fastapi-backend/db/`:

```
fastapi-backend/
├── alembic.ini                  # Alembic configuration (at project root)
└── db/
    ├── migrations/              # Alembic migration history
    │   ├── env.py               # Alembic environment (imports all models)
    │   ├── script.py.mako       # Migration template
    │   └── versions/            # Migration revisions
    │       ├── 4539779c0812_initial_migration_fixed.py
    │       └── f1d9e8001da8_add_cms_models_fix.py
    ├── seeds/
    │   ├── __init__.py          # Upsert helpers (upsert_by_name, add_missing_permissions)
    │   ├── data.py              # Pure data constants (SEED_ROLES, SEED_PERMISSIONS, etc.)
    │   └── seed.py              # Master data seeder (CLI: --sync / --reset)
    └── scripts/                 # One-off database scripts
        ├── phase2_schema_update.py
        └── migrate_settings_group.py
```

## Migrations with Alembic

### Creating a New Migration

After modifying a model, generate an auto-migration:

```bash
cd fastapi-backend
alembic revision --autogenerate -m "describe_your_changes"
```

**Important:** Before running, ensure all models are imported in `db/migrations/env.py` (lines 17-26). If you created a new model module, add it there:

```python
from app.modules.products.models.product_model import Product
```

### Applying Migrations

```bash
cd fastapi-backend
alembic upgrade head
```

### Rolling Back

```bash
alembic downgrade -1    # Roll back one step
alembic downgrade <revision_id>  # Roll back to specific revision
```

### Checking Status

```bash
alembic current          # Show current revision
alembic history          # Show migration history
```

## Seeding

The seeder creates initial data: roles, permissions, users, and settings. All operations use **idempotent upsert** patterns — existing data is never removed in sync mode.

### CLI Flags

| Flag | Description |
|---|---|
| `--sync` (default) | Idempotent sync — upserts missing records, never drops tables. Safe for all environments. |
| `--reset` | Drops and recreates all tables before seeding. Confirmation prompt required. **Blocked in production** unless `--force` is also passed. |

### Running the Seeder

**Local (sync — safe):**
```bash
cd fastapi-backend
python -m db.seeds.seed --sync
```

**Local (reset — development only):**
```bash
cd fastapi-backend
python -m db.seeds.seed --reset
```

**Docker (sync):**
```bash
docker compose exec backend python -m db.seeds.seed --sync
```

**Docker (reset):**
```bash
docker compose exec backend python -m db.seeds.seed --reset
```

> The seeder also runs automatically on container start (after `alembic upgrade head`) via the Dockerfile CMD.

### Adding New Permissions

Edit `db/seeds/data.py` — add entries to `SEED_PERMISSIONS`:

```python
{"name": "products.view",   "description": "View products"},
{"name": "products.create", "description": "Create products"},
{"name": "products.update", "description": "Update products"},
{"name": "products.delete", "description": "Delete products"},
```

Then add them to the `super_admin` role in `SEED_ROLE_PERMISSIONS`:

```python
"super_admin": ALL_PERMISSION_NAMES,  # auto-includes all
```

Re-seed with `--sync` to add them to the database without affecting existing data.

### Adding New Settings

Edit `db/seeds/data.py` — add entries to `SEED_SETTINGS`:

```python
{"setting_key": "my_setting", "setting_value": "default", "description": "My new setting"},
```

Re-seed with `--sync`. Existing settings (even if values were changed manually) will NOT be overwritten.

## Database Reset

### Full Reset (Development)

```bash
# 1. Drop and recreate the database (MySQL)
docker compose exec db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "DROP DATABASE IF EXISTS $DB_NAME; CREATE DATABASE $DB_NAME"'

# 2. Seed (reset mode drops & recreates tables)
docker compose exec backend python -m db.seeds.seed --reset

# 3. Stamp Alembic head
docker compose exec backend alembic stamp head
```

### Soft Delete Pattern

The system uses soft delete: records are not physically removed, but marked with `deleted_at`. The `BaseRepository` automatically excludes deleted records from queries.

```python
# Soft delete (sets deleted_at)
ProductRepository.delete(db, product_id, updated_by=actor_id)

# Hard delete (removes from DB)
ProductRepository.hard_delete(db, product_id)
```

To include deleted records in queries, use the repository directly:
```python
results = db.query(Product).filter(Product.deleted_at != None).all()
```

## Key Tables

| Table | Description |
|---|---|
| `users` | User accounts (soft delete) |
| `roles` | User roles (soft delete) |
| `permissions` | Individual permissions |
| `role_permissions` | Many-to-many: roles ↔ permissions |
| `user_sessions` | Active JWT sessions |
| `password_resets` | Password reset tokens |
| `settings` | Key-value application settings |
| `posts` | Blog/content posts (soft delete) |
| `categories` | Hierarchical categories (soft delete, self-referencing) |
| `audit_logs` | Audit trail for all actions |
| `media` | Uploaded file metadata |
| `notifications` | In-app notifications |
