# Architecture Decision Records

## ADR-001: Extension System via Config Files

**Status:** Accepted

**Context:** The CMS needed a way to enable/disable modules (posts, categories, public) per project without removing code.

**Decision:** Use a simple config toggle in two files:
- Backend: `app/core/extensions.py` — `ENABLED_EXTENSIONS` list
- Frontend: `src/config/modules.js` — `extensionModules` array

**Alternatives considered:**
- CLI installer (`python manage.py install posts`) — too complex for current scope
- Runtime database flag — over-engineered for MVP

**Consequences:**
- Docker requires rebuild after config change
- Simple, transparent, easy to revert

---

## ADR-002: Jodit over Editor.js for Rich Text

**Status:** Accepted

**Context:** The CMS needed a WYSIWYG editor for post content.

**Decision:** Use Jodit (v4.12) instead of Editor.js or BlockNote.js.

**Rationale:**
- Jodit outputs standard HTML — simple to store and render
- No need for a JSON block-based system yet (planned for Phase 2)
- Lower learning curve for content editors
- Built-in media upload integration

**Consequences:**
- Content is stored as raw HTML in `content` column
- Future migration to JSON blocks (`content_blocks`) is a breaking change (Phase 2)

---

## ADR-003: Adjacency List for Category Hierarchy

**Status:** Accepted

**Context:** Categories needed hierarchical (parent-child) relationships.

**Decision:** Use Adjacency List (single `parent_id` self-referencing FK).

**Alternatives considered:**
- Nested Set — complex updates, overkill for simple trees
- Materialized Path — more flexible but more complex queries
- Closure Table — best for deep trees but adds join complexity

**Consequences:**
- Simple, intuitive, SQL-native
- Recursive queries needed for full tree depth
- Max depth limited by frontend (`categoryMaxLevel` setting)

---

## ADR-004: Soft Delete for All Major Entities

**Status:** Accepted

**Context:** Need safe deletion that can be reverted.

**Decision:** Add `deleted_at` (nullable DateTime) to all major tables. `BaseRepository` filters out deleted records by default. Hard delete available for admin force-removal.

**Rationale:**
- Prevents accidental data loss
- Maintains referential integrity (deleted posts still linked to categories)
- Audit trail still references soft-deleted users/items

**Consequences:**
- Queries need `WHERE deleted_at IS NULL` (handled by BaseRepository)
- Storage grows over time (require periodic cleanup script)
- No cascading soft delete (orphaned records stay)

---

## ADR-005: JWT with Session ID (SID) for Token Revocation

**Status:** Accepted

**Context:** Standard JWT cannot be revoked before expiry. Admin needs to kick users out instantly.

**Decision:** Embed `sid` (session_id) in both access and refresh tokens. Every authenticated request checks the session still exists in DB.

**Flow:**
1. Login → creates `UserSession` row → JWT contains `sid`
2. Each request → `get_current_user()` validates `sid` exists
3. Logout/revoke → deletes `UserSession` row → JWT invalidated

**Consequences:**
- One extra DB query per request (permission check adds another)
- Sessions are visible and manageable in Admin UI
- Revocation is instant — no token blacklist needed

---

## ADR-006: Monorepo with Separate Frontends

**Status:** Accepted

**Context:** The system has two distinct user interfaces (admin dashboard and public blog).

**Decision:** Keep both frontends in the same repository under separate directories (`vue3-frontend` and `vue3-public-frontend`).

**Rationale:**
- Shared API contracts (both consume same backend)
- Easier to maintain during early development
- Single docker-compose for all services

**Consequences:**
- Separate `node_modules` and build pipelines
- Version mismatches possible (currently: vue-router v4 vs v5, Vite 5 vs 8)
- Future: could split into separate repos or a monorepo tool (Nx, Turborepo)

---

## ADR-007: WIB (UTC+7) as Standard Timezone

**Status:** Accepted

**Context:** The application targets Indonesian users and needs consistent timestamps.

**Decision:** All `created_at`/`updated_at` fields use WIB (UTC+7) via `app.helpers.date_helper.get_now_wib()`. Timestamps are stored as naive datetime (no timezone info) for MySQL compatibility.

**Consequences:**
- Not suitable for global/multi-timezone use without modification
- Simple and consistent for the target audience
- Frontend does not need timezone conversion
