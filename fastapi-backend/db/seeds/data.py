SEED_ROLES = [
    {"name": "super_admin", "description": "Full system access"},
    {"name": "admin", "description": "Administrative access"},
]

SEED_PERMISSIONS = [
    {"name": "users.view",    "description": "View users"},
    {"name": "users.create",  "description": "Create users"},
    {"name": "users.update",  "description": "Update users"},
    {"name": "users.delete",  "description": "Delete users"},
    {"name": "roles.view",    "description": "View roles"},
    {"name": "roles.create",  "description": "Create roles"},
    {"name": "roles.update",  "description": "Update roles"},
    {"name": "roles.delete",  "description": "Delete roles"},
    {"name": "audit.view",    "description": "View audit logs"},
    {"name": "notifications.view", "description": "View notifications"},
    {"name": "settings.view",   "description": "View settings"},
    {"name": "settings.update", "description": "Update settings"},
    {"name": "sessions.view",   "description": "View active sessions"},
    {"name": "sessions.delete", "description": "Revoke sessions (kick)"},
    {"name": "categories.view",   "description": "View categories"},
    {"name": "categories.create", "description": "Create categories"},
    {"name": "categories.update", "description": "Update categories"},
    {"name": "categories.delete", "description": "Delete categories"},
    {"name": "posts.view",      "description": "View posts"},
    {"name": "posts.create",    "description": "Create posts"},
    {"name": "posts.update",    "description": "Update posts"},
    {"name": "posts.delete",    "description": "Delete posts"},
    {"name": "media.view",      "description": "View media files"},
    {"name": "media.create",    "description": "Upload media files"},
    {"name": "media.update",    "description": "Update media files"},
    {"name": "media.delete",    "description": "Delete media files"},
]

ALL_PERMISSION_NAMES = [p["name"] for p in SEED_PERMISSIONS]

SEED_ROLE_PERMISSIONS = {
    "super_admin": "*",
    "admin": [p for p in ALL_PERMISSION_NAMES if p not in ("roles.delete", "settings.update")],
}

SEED_USERS = [
    {
        "username": "superadmin",
        "email": "superadmin@example.com",
        "full_name": "Super Administrator",
        "password": "admin123",
        "role": "super_admin",
    },
    {
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Administrator",
        "password": "admin123",
        "role": "admin",
    },
]

SEED_SETTINGS = [
    {"setting_key": "app_name",            "setting_value": "CMS Template", "description": "Application Name"},
    {"setting_key": "maintenance_mode",     "setting_value": "false",       "description": "Maintenance Mode Toggle"},
    {"setting_key": "registration_enabled", "setting_value": "true",        "description": "Allow user self-registration"},
    {"setting_key": "captcha_enabled",      "setting_value": "false",       "description": "CAPTCHA verification on login/register"},
]
