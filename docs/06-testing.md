# Testing Guide

## Backend Testing (Pytest)

### Stack

| Tool | Purpose |
|---|---|
| `pytest` | Test runner |
| `pytest-asyncio` | Async test support |
| `httpx` | HTTP client for API tests |
| `sqlite3` | In-memory database for fast tests |

### Running Tests

```bash
cd fastapi-backend
pytest                     # Run all tests
pytest -v                  # Verbose
pytest -k "auth"           # Filter by keyword
pytest tests/integration/  # Run specific directory
pytest --cov              # With coverage (if pytest-cov installed)
```

### Test Structure

```
tests/
├── conftest.py              # Fixtures: db, client, auth headers
├── unit/                    # Unit tests (no DB) — to be populated
│   └── __init__.py
└── integration/             # Integration tests (with DB)
    ├── test_auth.py
    ├── test_captcha.py
    ├── test_categories.py
    ├── test_media.py
    ├── test_notifications.py
    ├── test_posts.py
    ├── test_public_api.py
    ├── test_roles.py
    ├── test_seed.py
    ├── test_settings.py
    └── test_users.py
```

### Fixtures (conftest.py)

The `conftest.py` provides:

| Fixture | Scope | Description |
|---|---|---|
| `db_engine` | session | Creates tables, seeds data (one-time) |
| `db` | function | Transaction per test (auto-rollback) |
| `client` | function | FastAPI TestClient with DB override |
| `async_client` | function | httpx AsyncClient with DB override |
| `admin_token_headers` | function | Bearer token for super_admin |
| `normal_user_token_headers` | function | Bearer token for normal user |

### Writing Tests

**Pattern for API integration tests:**

```python
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_get_items(async_client: AsyncClient, admin_token_headers):
    response = await async_client.get("/api/v1/products", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "items" in data["data"]


async def test_create_item(async_client: AsyncClient, admin_token_headers):
    payload = {"name": "Test Product", "slug": "test-product"}
    response = await async_client.post("/api/v1/products", json=payload, headers=admin_token_headers)
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Test Product"


async def test_create_item_denied_without_auth(async_client: AsyncClient):
    payload = {"name": "Hacker", "slug": "hacker"}
    response = await async_client.post("/api/v1/products", json=payload)
    assert response.status_code == 401
```

**Conventions:**
1. Use `@pytest.mark.asyncio` for async tests
2. Use `admin_token_headers` for authenticated requests
3. Test both success and error cases
4. Each test should be independent (test DB resets per function)

### Test Configuration

`pytest.ini`:
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
```

## Frontend Testing (Vitest)

### Stack

| Tool | Purpose |
|---|---|
| `vitest` | Test runner (integrated with Vite) |
| `@vue/test-utils` | Vue component mounting & interaction |
| `jsdom` | DOM environment in Node.js |

### Setup

**`vitest.config.js`:**
```js
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.js'],
    globals: true,
  },
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') }
  }
})
```

### Running Tests

```bash
cd vue3-frontend
npm run test               # vitest run (once)
npm run test:watch         # vitest (watch mode)
```

### Writing Component Tests

**Example — Button component:**

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Button from '@/components/ui/Button.vue'

describe('Button', () => {
  it('renders with default variant', () => {
    const wrapper = mount(Button, {
      slots: { default: 'Click me' }
    })
    expect(wrapper.text()).toBe('Click me')
  })

  it('disables when disabled prop is true', () => {
    const wrapper = mount(Button, {
      props: { disabled: true },
      slots: { default: 'Submit' }
    })
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })
})
```

### Best Practices

1. Test component rendering, props, slots, and emitted events
2. Mock Pinia stores when testing views that depend on auth
3. Use `wrapper.find()` for DOM queries
4. Use `wrapper.vm` to access Vue instance internals
5. Keep tests focused — one assertion concept per test
