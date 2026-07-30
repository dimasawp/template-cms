# Module Development Guide

This guide explains how to create a new module in this CMS, end-to-end: backend models to frontend UI.

## Overview

A "module" is a self-contained feature (e.g., `posts`, `categories`) with its own database model, API endpoints, and UI pages. Each module lives in:

- **Backend**: `fastapi-backend/app/modules/<module_name>/`
- **Frontend**: `vue3-frontend/src/views/<category>/` + services + router config

## Step-by-Step: Creating a "Products" Module

### Step 1: Backend — Create Directory Structure

```
fastapi-backend/app/modules/products/
├── __init__.py
├── models/
│   └── product_model.py
├── schemas/
│   └── product_schema.py
├── repositories/
│   └── product_repository.py
├── services/
│   └── product_service.py
└── controllers/
    └── product_controller.py
```

### Step 2: Database Model

**`models/product_model.py`**:
```python
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.helpers.date_helper import get_now_wib


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=get_now_wib, nullable=False)
    updated_at = Column(DateTime, default=get_now_wib, onupdate=get_now_wib, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    author = relationship("User", foreign_keys=[created_by])
    editor = relationship("User", foreign_keys=[updated_by])


    def __repr__(self):
        return f"<Product {self.name}>"
```

### Step 3: Pydantic Schemas

**`schemas/product_schema.py`**:
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    price: int = Field(..., ge=0)
    category_id: Optional[int] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    slug: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    price: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    price: int
    category_id: Optional[int] = None
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
```

### Step 4: Repository

**`repositories/product_repository.py`**:
```python
from app.modules._base.repository import BaseRepository
from app.modules.products.models.product_model import Product


class ProductRepository(BaseRepository):
    model = Product
    search_fields = ["name", "slug"]
```

This gives you: `get_by_id`, `get_all` (paginated, searchable, sortable), `create`, `update`, `delete` (soft), `hard_delete`.

### Step 5: Service (Optional)

**`services/product_service.py`**:
```python
from sqlalchemy.orm import Session
from app.modules._base.service import BaseService
from app.modules.products.models.product_model import Product
from app.modules.products.repositories.product_repository import ProductRepository


class ProductService(BaseService):
    repository = ProductRepository

    @classmethod
    def create(cls, db, data, actor_id=None, request=None):
        # Auto-set slug if exists (from uncommitted extension)
        if ProductRepository.get_by_slug(db, data.slug):
            raise ConflictException("Slug already exists")

        product = ProductRepository.create(
            db, data.model_dump(),
            created_by=actor_id, updated_by=actor_id
        )
        return product

    # create(), update(), delete() follow the same pattern as BaseService
```

If you don't need custom business logic, you can skip the service and call `ProductRepository` directly from the controller.

### Step 6: Controller / API Endpoints

**`controllers/product_controller.py`**:
```python
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, check_permission
from app.modules.users.models.user_model import User
from app.modules.products.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from app.modules.products.repositories.product_repository import ProductRepository
from app.helpers.response import success_response, paginated_response
from app.exceptions import handle_errors, NotFoundException

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@router.get("")
@handle_errors
async def get_all_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    order_by: Optional[str] = Query(None),
    order_dir: str = Query("asc"),
    db: Session = Depends(get_db),
    _user: User = Depends(check_permission("products.view")),
):
    items, total = ProductRepository.get_all(
        db, page=page, per_page=per_page, search=search,
        order_by=order_by, order_dir=order_dir
    )
    return paginated_response(
        [ProductResponse.model_validate(p).model_dump() for p in items],
        total, page, per_page
    )


@router.get("/{product_id}")
@handle_errors
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(check_permission("products.view")),
):
    product = ProductRepository.get_by_id(db, product_id)
    if not product:
        raise NotFoundException("Product not found")
    return success_response(data=ProductResponse.model_validate(product).model_dump())


@router.post("")
@handle_errors
async def create_product(
    data: ProductCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("products.create")),
):
    product = ProductRepository.create(
        db, data.model_dump(),
        created_by=current_user.id, updated_by=current_user.id
    )
    return success_response(
        data=ProductResponse.model_validate(product).model_dump(),
        message="Product created",
    )


@router.put("/{product_id}")
@handle_errors
async def update_product(
    product_id: int,
    data: ProductUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("products.update")),
):
    product = ProductRepository.get_by_id(db, product_id)
    if not product:
        raise NotFoundException("Product not found")
    product = ProductRepository.update(
        db, product_id, data.model_dump(exclude_unset=True),
        updated_by=current_user.id
    )
    return success_response(data=ProductResponse.model_validate(product).model_dump())


@router.delete("/{product_id}")
@handle_errors
async def delete_product(
    product_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_permission("products.delete")),
):
    ProductRepository.delete(db, product_id, updated_by=current_user.id)
    return success_response(message="Product deleted")
```

### Step 7: Register the Module

The module is auto-discovered if it's in the `app/modules/` directory and:

- **Core module**: Always loaded. Add module name to `CORE_MODULES` list in `app/modules/__init__.py`:
  ```python
  CORE_MODULES = ["auth", "users", "roles", "settings", "audit", "dashboard", "media", "menus", "notifications", "products"]
  ```

- **Extension module**: Add to `ENABLED_EXTENSIONS` in `app/core/extensions.py`:
  ```python
  ENABLED_EXTENSIONS = ["posts", "categories", "public", "products"]
  ```

### Step 8: Add Permissions to Seeder

**`db/seeds/data.py`** — add entries to `SEED_PERMISSIONS`:
```python
{"name": "products.view",   "description": "View products"},
{"name": "products.create", "description": "Create products"},
{"name": "products.update", "description": "Update products"},
{"name": "products.delete", "description": "Delete products"},
```

Then add them to `super_admin` in `SEED_ROLE_PERMISSIONS` (or `ALL_PERMISSION_NAMES` auto-includes all).

Re-seed: `python -m db.seeds.seed --sync`

### Step 9: Create Migration

```bash
cd fastapi-backend
alembic revision --autogenerate -m "add_products_table"
alembic upgrade head
```

### Step 10: Frontend — API Service

**`vue3-frontend/src/services/productService.js`**:
```javascript
import api from './api'

export const productService = {
  getAll(params) { return api.get('/products', { params }) },
  getById(id)    { return api.get(`/products/${id}`) },
  create(data)   { return api.post('/products', data) },
  update(id, data) { return api.put(`/products/${id}`, data) },
  delete(id)     { return api.delete(`/products/${id}`) },
}
```

### Step 11: Frontend — Router

Add routes in `src/router/index.js` under the Dashboard children:
```javascript
{ path: 'products',             name: 'products',      component: () => import('@/views/products/ProductsView.vue'),      meta: { title: 'Product Management', permission: 'products.view' } },
{ path: 'products/create',      name: 'products-create', component: () => import('@/views/products/ProductsFormView.vue'), meta: { title: 'Create Product', permission: 'products.create' } },
{ path: 'products/:id/edit',    name: 'products-edit',  component: () => import('@/views/products/ProductsFormView.vue'), meta: { title: 'Edit Product', permission: 'products.update' } },
```

### Step 12: Frontend — Sidebar Config

**`src/config/modules.js`**:
```javascript
export const extensionModules = [
  { name: 'Products', group: 'Web Content', icon: Package, route: '/products', permission: 'products.view' },
]
```

Import the icon: `import { Package } from 'lucide-vue-next'`

### Step 13: Frontend — Views

Create page components under `src/views/products/` following the pattern of existing views like `PostsView.vue` and `PostsFormView.vue`.

## Summary Checklist

| # | Task | Files to Create/Modify |
|---|---|---|
| 1 | Model | `models/product_model.py` |
| 2 | Schemas | `schemas/product_schema.py` |
| 3 | Repository | `repositories/product_repository.py` |
| 4 | Service (optional) | `services/product_service.py` |
| 5 | Controller | `controllers/product_controller.py` |
| 6 | Permission | `db/seeds/data.py` — add permission entries to `SEED_PERMISSIONS` |
| 7 | Migration | Run `alembic revision --autogenerate` |
| 8 | Module registration | `app/modules/__init__.py` or `app/core/extensions.py` |
| 9 | Frontend service | `vue3-frontend/src/services/productService.js` |
| 10 | Frontend router | `vue3-frontend/src/router/index.js` |
| 11 | Frontend sidebar | `vue3-frontend/src/config/modules.js` |
| 12 | Frontend views | `vue3-frontend/src/views/products/*.vue` |
| 13 | Frontend store (if needed) | `vue3-frontend/src/stores/product.js` |
