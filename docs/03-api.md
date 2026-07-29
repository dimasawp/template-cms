# API Reference

## Base URL

All API endpoints are prefixed with `/api/v1`. In development:

- Local: `http://localhost:8000/api/v1`
- Docker: `http://localhost:8000/api/v1`

## Response Format

### Success Response

```json
{
  "status": "success",
  "code": 200,
  "message": "Operation successful",
  "data": { ... },
  "timestamp": "2026-07-29 14:30:00 WIB"
}
```

### Paginated Response

```json
{
  "status": "success",
  "code": 200,
  "message": "Data retrieved",
  "data": {
    "items": [ ... ],
    "pagination": {
      "total": 100,
      "page": 1,
      "per_page": 10,
      "total_pages": 10
    }
  },
  "timestamp": "2026-07-29 14:30:00 WIB"
}
```

### Error Response

```json
{
  "status": "error",
  "code": 422,
  "message": "Validation error",
  "errors": [
    { "field": "title", "message": "Field required" }
  ],
  "timestamp": "2026-07-29 14:30:00 WIB"
}
```

### HTTP Status Codes Used

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created (returned in body `code`, HTTP status is 200) |
| 400 | Bad request (validation, duplicate) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (missing permission) |
| 404 | Not found |
| 409 | Conflict (duplicate slug, etc.) |
| 422 | Validation error |
| 500 | Internal server error |
| 503 | Maintenance mode |

## Authentication

### Register

```
POST /api/v1/auth/register
```

```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "full_name": "New User",
  "password": "securepassword"
}
```

Response: `{"message": "Registration successful. Please login."}`

### Login

```
POST /api/v1/auth/login
```

```json
{
  "username": "superadmin",
  "password": "admin123"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### Get Current User

```
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

Response includes `permissions` array and `role_name`.

### Refresh Token

```
POST /api/v1/auth/refresh
```

```json
{ "refresh_token": "eyJ..." }
```

### Logout

```
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

## Endpoints by Module

### Auth (`/api/v1/auth`)

| Method | Path | Auth | Permission |
|---|---|---|---|
| POST | `/register` | No | — |
| POST | `/login` | No | — |
| POST | `/swagger-login` | No | — |
| POST | `/refresh` | No | — |
| POST | `/logout` | Yes | — |
| GET | `/me` | Yes | — |
| PUT | `/me` | Yes | — |
| PUT | `/change-password` | Yes | — |
| POST | `/avatar` | Yes | — |
| GET | `/sessions` | Yes | `sessions.view` |
| DELETE | `/sessions/{id}` | Yes | `sessions.delete` |
| POST | `/sessions/bulk-revoke` | Yes | `sessions.delete` |

### Users (`/api/v1/users`)

| Method | Path | Permission |
|---|---|---|
| GET | `/` | `users.view` |
| GET | `/{id}` | `users.view` |
| POST | `/` | `users.create` |
| PUT | `/{id}` | `users.update` |
| DELETE | `/{id}` | `users.delete` |
| POST | `/{id}/reset-password` | `users.update` |

### Roles (`/api/v1/roles`)

| Method | Path | Permission |
|---|---|---|
| GET | `/` | `roles.view` |
| GET | `/permissions` | `roles.view` |
| GET | `/{id}` | `roles.view` |
| POST | `/` | `roles.create` |
| PUT | `/{id}` | `roles.update` |
| DELETE | `/{id}` | `roles.delete` |

### Settings (`/api/v1/settings`)

| Method | Path | Auth |
|---|---|---|
| GET | `/` | Public (read) |
| GET | `/raw` | `settings.view` |
| PUT | `/{key}` | `settings.update` |
| POST | `/bulk` | `settings.update` |
| POST | `/reset` | Super Admin |

### Posts (`/api/v1/posts`)

| Method | Path | Permission |
|---|---|---|
| GET | `/` | `posts.view` |
| GET | `/{id}` | `posts.view` |
| POST | `/` | `posts.create` |
| PUT | `/{id}` | `posts.update` |
| DELETE | `/{id}` | `posts.delete` |

Query params: `page`, `per_page`, `search`, `status` (DRAFT/PUBLISHED/ARCHIVED), `category_id`, `category_level`, `order_by`, `order_dir`

### Categories (`/api/v1/categories`)

| Method | Path | Permission |
|---|---|---|
| GET | `/` | `categories.view` |
| GET | `/{id}` | `categories.view` |
| POST | `/` | `categories.create` |
| POST | `/reorder` | `categories.update` |
| PUT | `/{id}` | `categories.update` |
| DELETE | `/{id}` | `categories.delete` |

### Public API (No Auth Required)

| Method | Path | Rate Limit |
|---|---|---|
| GET | `/public/posts` | 100/min |
| GET | `/public/posts/{slug}` | 100/min |
| GET | `/public/categories` | 100/min |
| GET | `/public/settings` | 100/min |

Public posts endpoint only returns `PUBLISHED` posts. The detail endpoint also allows `ARCHIVED` posts.

### Other Modules

| Module | Prefix | Auth |
|---|---|---|
| Audit | `/api/v1/audit` | `audit.view` |
| Dashboard | `/api/v1/dashboard` | `users.view` |
| Media | `/api/v1/media` | Yes (auth required) |
| Notifications | `/api/v1/notifications` | Yes (auth required) |

## WebSocket

```
ws://localhost:8000/api/v1/ws/notifications
```

Used for real-time broadcasts (e.g., maintenance mode changes). The frontend uses a hybrid WebSocket + polling fallback via the `useRealtime` composable.
