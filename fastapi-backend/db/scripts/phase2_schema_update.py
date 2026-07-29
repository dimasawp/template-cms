"""
Migration script: Phase 2 Database Schema Updates
- Posts: is_published -> status, meta_data -> additional_contents, add thumbnail/created_by/updated_by
- Categories: add order_index/is_menu/created_by/updated_by

Run: python -m app.migrations.phase2_schema_update
"""

from sqlalchemy import text
from app.core.database import SessionLocal, engine


def run():
    print("\n" + "=" * 50)
    print("  PHASE 2 SCHEMA MIGRATION")
    print("=" * 50 + "\n")

    with engine.begin() as conn:
        dialect = engine.dialect.name

        # ── Posts table migrations ──────────────────────────
        print("[POSTS] Checking columns...")

        # 1. Add 'status' column
        try:
            conn.execute(text("SELECT status FROM posts LIMIT 1"))
            print("[SKIP] posts.status already exists")
        except Exception:
            conn.execute(text("ALTER TABLE posts ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'DRAFT'"))
            # Migrate existing is_published data
            try:
                conn.execute(text("UPDATE posts SET status = CASE WHEN is_published = 1 THEN 'PUBLISHED' ELSE 'DRAFT' END"))
                print("[OK] posts.status added and migrated from is_published")
            except Exception:
                print("[OK] posts.status added (no is_published data to migrate)")

        # 2. Add 'thumbnail' column
        try:
            conn.execute(text("SELECT thumbnail FROM posts LIMIT 1"))
            print("[SKIP] posts.thumbnail already exists")
        except Exception:
            conn.execute(text("ALTER TABLE posts ADD COLUMN thumbnail VARCHAR(500) NULL"))
            print("[OK] posts.thumbnail added")

        # 3. Add 'additional_contents' column
        try:
            conn.execute(text("SELECT additional_contents FROM posts LIMIT 1"))
            print("[SKIP] posts.additional_contents already exists")
        except Exception:
            conn.execute(text("ALTER TABLE posts ADD COLUMN additional_contents JSON NULL"))
            print("[OK] posts.additional_contents added")

        # 4. Add 'created_by' column
        try:
            conn.execute(text("SELECT created_by FROM posts LIMIT 1"))
            print("[SKIP] posts.created_by already exists")
        except Exception:
            conn.execute(text("ALTER TABLE posts ADD COLUMN created_by INT NULL"))
            print("[OK] posts.created_by added")

        # 5. Add 'updated_by' column
        try:
            conn.execute(text("SELECT updated_by FROM posts LIMIT 1"))
            print("[SKIP] posts.updated_by already exists")
        except Exception:
            conn.execute(text("ALTER TABLE posts ADD COLUMN updated_by INT NULL"))
            print("[OK] posts.updated_by added")

        # 6. Drop old columns if they exist (is_published, meta_data)
        if dialect == "mysql":
            try:
                conn.execute(text("SELECT is_published FROM posts LIMIT 1"))
                conn.execute(text("ALTER TABLE posts DROP COLUMN is_published"))
                print("[OK] posts.is_published dropped (migrated to status)")
            except Exception:
                print("[SKIP] posts.is_published already removed")

            try:
                conn.execute(text("SELECT meta_data FROM posts LIMIT 1"))
                conn.execute(text("ALTER TABLE posts DROP COLUMN meta_data"))
                print("[OK] posts.meta_data dropped (replaced by additional_contents)")
            except Exception:
                print("[SKIP] posts.meta_data already removed")

        # ── Categories table migrations ─────────────────────
        print("\n[CATEGORIES] Checking columns...")

        # 1. Add 'order_index' column
        try:
            conn.execute(text("SELECT order_index FROM categories LIMIT 1"))
            print("[SKIP] categories.order_index already exists")
        except Exception:
            conn.execute(text("ALTER TABLE categories ADD COLUMN order_index INT NOT NULL DEFAULT 0"))
            print("[OK] categories.order_index added")

        # 2. Add 'is_menu' column
        try:
            conn.execute(text("SELECT is_menu FROM categories LIMIT 1"))
            print("[SKIP] categories.is_menu already exists")
        except Exception:
            conn.execute(text("ALTER TABLE categories ADD COLUMN is_menu BOOLEAN NOT NULL DEFAULT 0"))
            print("[OK] categories.is_menu added")

        # 3. Add 'created_by' column
        try:
            conn.execute(text("SELECT created_by FROM categories LIMIT 1"))
            print("[SKIP] categories.created_by already exists")
        except Exception:
            conn.execute(text("ALTER TABLE categories ADD COLUMN created_by INT NULL"))
            print("[OK] categories.created_by added")

        # 4. Add 'updated_by' column
        try:
            conn.execute(text("SELECT updated_by FROM categories LIMIT 1"))
            print("[SKIP] categories.updated_by already exists")
        except Exception:
            conn.execute(text("ALTER TABLE categories ADD COLUMN updated_by INT NULL"))
            print("[OK] categories.updated_by added")

    print(f"\n{'=' * 50}")
    print("  ✅  MIGRATION COMPLETED SUCCESSFULLY")
    print(f"{'=' * 50}\n")


if __name__ == "__main__":
    run()
