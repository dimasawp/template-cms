import sys
import os
from sqlalchemy import text
from app.core.database import SessionLocal

def run_migration():
    db = SessionLocal()
    try:
        print("Running settings table migration...")
        
        # 1. Add column if not exists
        # Note: SQLite doesn't support AFTER. For MySQL/Postgres it works.
        # We'll use a generic approach.
        try:
            db.execute(text("ALTER TABLE settings ADD COLUMN setting_group VARCHAR(50) DEFAULT 'general'"))
            db.commit()
            print("- Column 'setting_group' added.")
        except Exception as e:
            print(f"- Column 'setting_group' might already exist or error: {e}")
            db.rollback()

        # 2. Update existing data to groups
        system_keys = ['maintenance_mode', 'maintenance_scheduled_at', 'registration_enabled']
        system_placeholders = ", ".join([f"'{k}'" for k in system_keys])
        
        db.execute(text(f"UPDATE settings SET setting_group = 'system' WHERE setting_key IN ({system_placeholders})"))
        db.commit()
        print("- System settings classified.")
        
        db.execute(text("UPDATE settings SET setting_group = 'general' WHERE setting_group IS NULL OR setting_group = ''"))
        db.commit()
        print("- General settings classified.")
        
        print("Migration completed successfully.")
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Add project root to path
    sys.path.append(os.getcwd())
    run_migration()
