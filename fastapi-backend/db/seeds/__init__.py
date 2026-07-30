"""Database seed helpers."""

from sqlalchemy.orm import Session


def upsert(db: Session, model, lookup_field: str, lookup_value, defaults: dict):
    """Find record by lookup_field=lookup_value, update defaults if exists, insert if not."""
    record = db.query(model).filter(getattr(model, lookup_field) == lookup_value).first()
    if record:
        for k, v in defaults.items():
            setattr(record, k, v)
    else:
        data = {lookup_field: lookup_value, **defaults}
        record = model(**data)
        db.add(record)
    db.flush()
    return record


def upsert_by_name(db: Session, model, name: str, defaults: dict):
    """Upsert by 'name' field."""
    return upsert(db, model, "name", name, defaults)


def add_missing_permissions(db: Session, role, all_permission_objects: list):
    """Add permissions to role that it doesn't already have. Never removes existing ones."""
    existing = {p.name for p in role.permissions}
    for p in all_permission_objects:
        if p.name not in existing:
            role.permissions.append(p)
    db.flush()


def confirm_or_abort(message: str) -> bool:
    """Ask for CLI confirmation. Returns True if confirmed."""
    try:
        reply = input(f"\n  {message} (y/N): ").strip().lower()
        return reply == "y"
    except (EOFError, KeyboardInterrupt):
        return False
