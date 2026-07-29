# Database Guide

## Overview

The system uses **MySQL 8.0** with **SQLAlchemy 2.0** as ORM and **Alembic** for migrations. All timestamp fields use **WIB (UTC+7)**.

Database configuration is in `app/core/config.py` (loaded from `.env`).

## Project Structure

Database-related files are consolidated under `fastapi-backend/db/`:

```
fastapi-backend/db/
├── alembic.ini                  # Alembic configuration
├── migrations/                  # Alembic migration history
│   ├── env.py                   # Alembic environment (imports all models)
│   ├── script.py.mako           # Migration template
│   └── versions/                # Migration revisions
│       ├── 4539779c0812_initial_migration_fixed.py
│       └── f1d9e8001da8_add_cms_models_fix.py
├── seeds/
│   └── seed.py                  # Master data seeder
└── scripts/                     # One-off database scripts
    ├── phase2_schema_update.py
    └── migrate_settings_group.py
```

## Migrations with Alembic

### Creating a New Migration

After modifying a model, generate an auto-migration:

```bash
cd fastapi-backend/db
alembic revision --autogenerate -m "describe_your_changes"
```

**Important:** Before running, ensure all models are imported in `migrations/env.py` (lines 17-26). If you created a new model module, add it there:

```python
from app.modules.products.models.product_model import Product
```

### Applying Migrations

```bash
cd fastapi-backend/db
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

The seeder creates initial data: roles, permissions, users, and settings.

### Running the Seeder

**Local:**
```bash
cd fastapi-backend
python -m db.seeds.seed
```

**Docker:**
```bash
docker compose exec backend python -m db.seeds.seed
```

**Non-production** environments will drop and recreate all tables before seeding.

### Adding New Permissions

Edit `db/seeds/seed.py` → `seed_permissions()` function:

```python
permissions = [
    # ... existing permissions ...,
    {"id": 23, "name": "products.view",   "description": "View products"},
    {"id": 24, "name": "products.create", "description": "Create products"},
    {"id": 25, "name": "products.update", "description": "Update products"},
    {"id": 26, "name": "products.delete", "description": "Delete products"},
]
```

Then re-seed to add them to the database.

### Adding New Settings

Edit `db/seeds/seed.py` → `seed_settings()` function:

```python
settings_data = [
    # ... existing settings ...,
    {"setting_key": "my_setting", "setting_value": "default", "description": "My new setting"},
]
```

## Database Reset

### Full Reset (Development)

```bash
# 1. Drop and recreate the database (MySQL)
docker compose exec db sh -c 'mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "DROP DATABASE IF EXISTS $DB_NAME; CREATE DATABASE $DB_NAME"'

# 2. Seed
docker compose exec backend python -m db.seeds.seed

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
