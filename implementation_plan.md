# MarketPy MVP — Implementation Plan

A minimal two-sided marketplace MVP built with FastAPI (backend) + Next.js 15 (frontend). The goal is clean, readable Python code that a solo developer can easily extend.

---

## Project Structure

```
marketplace-mvp/
├── backend/
│   ├── .env                      # loaded by python-dotenv
│   ├── main.py                   # FastAPI app entry point, startup seeding
│   ├── database.py               # SQLAlchemy engine + session
│   ├── auth.py                   # JWT helpers (create/verify token)
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py             # All ORM models (User, Category, Product, Order, OrderItem)
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py            # All Pydantic v2 schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py               # POST /register, POST /login
│   │   ├── products.py           # GET/POST/PUT/DELETE /products, image upload
│   │   ├── orders.py             # POST /checkout, GET /orders/buyer, GET /orders/seller
│   │   └── users.py              # GET /me, PATCH /me (toggle is_seller)
│   ├── static/
│   │   └── uploads/              # local image storage
│   └── requirements.txt
│
├── frontend/
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx              # product catalog (search + filters)
│   │   ├── products/[id]/page.tsx
│   │   ├── cart/page.tsx
│   │   ├── checkout/page.tsx
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   ├── orders/page.tsx       # buyer orders
│   │   └── dashboard/
│   │       ├── page.tsx          # seller product list
│   │       ├── new/page.tsx
│   │       ├── edit/[id]/page.tsx
│   │       └── orders/page.tsx   # seller order items
│   └── lib/
│       ├── api.ts                # typed fetch wrappers
│       └── auth.ts               # token storage helpers
│
├── .env.example
└── README.md
```

---

## Data Models

| Model | Fields |
|---|---|
| **User** | id, email, hashed_password, is_seller (bool, default false) |
| **Category** | id, name |
| **Product** | id, title, description, price, stock, images (JSON), seller_id → User, category_id → Category |
| **Order** | id, buyer_id → User, total, status ("pending"/"paid_mock"), created_at |
| **OrderItem** | id, order_id → Order, product_id → Product, quantity, price_at_purchase |

**Category pre-seed:** Electronics, Clothing, Home, Books, Beauty, Sports

---

## Proposed Changes

### Backend

#### [NEW] [requirements.txt](file:///G:/myDjangoProjects/marketplace-mvp/backend/requirements.txt)
```
fastapi, uvicorn[standard], sqlalchemy, pydantic[email], python-jose[cryptography], passlib[bcrypt], python-dotenv, python-multipart, aiofiles
```

#### [NEW] [.env.example](file:///G:/myDjangoProjects/marketplace-mvp/.env.example)
`DATABASE_URL`, `SECRET_KEY`, `ALGORITHM=HS256`, `ACCESS_TOKEN_EXPIRE_MINUTES=60`

#### [NEW] [backend/database.py](file:///G:/myDjangoProjects/marketplace-mvp/backend/database.py)
SQLAlchemy engine + `SessionLocal` + `Base` — reads `DATABASE_URL` from `.env`.

#### [NEW] [backend/auth.py](file:///G:/myDjangoProjects/marketplace-mvp/backend/auth.py)
`create_access_token()`, `get_current_user()` dependency using `python-jose` + `passlib`.

#### [NEW] [backend/models/models.py](file:///G:/myDjangoProjects/marketplace-mvp/backend/models/models.py)
All 5 ORM models. `Product.images` stored as `JSON` column.

#### [NEW] [backend/schemas/schemas.py](file:///G:/myDjangoProjects/marketplace-mvp/backend/schemas/schemas.py)
Pydantic v2 schemas: `UserCreate`, `UserOut`, `Token`, `ProductCreate`, `ProductOut`, `OrderCreate`, `OrderOut`, `OrderItemOut`, etc.

#### [NEW] [backend/routers/auth.py](file:///G:/myDjangoProjects/marketplace-mvp/backend/routers/auth.py)
- `POST /auth/register` — create user, hash password
- `POST /auth/login` — verify password, return JWT

#### [NEW] [backend/routers/users.py](file:///G:/myDjangoProjects/marketplace-mvp/backend/routers/users.py)
- `GET /users/me` — return current user
- `PATCH /users/me` — update `is_seller`

#### [NEW] [backend/routers/products.py](file:///G:/myDjangoProjects/marketplace-mvp/backend/routers/products.py)
- `GET /products` — list/search/filter (title, category_id, min_price, max_price)
- `GET /products/{id}` — detail
- `POST /products` — create (seller only), multipart form with up to 5 images
- `PUT /products/{id}` — update (own product only)
- `DELETE /products/{id}` — delete (own product only)
- `GET /categories` — list all categories

#### [NEW] [backend/routers/orders.py](file:///G:/myDjangoProjects/marketplace-mvp/backend/routers/orders.py)
- `POST /orders/checkout` — receives `[{product_id, quantity}]`, validates stock, creates `Order` + `OrderItems`, deducts stock, sets `status="paid_mock"`
- `GET /orders/buyer` — buyer's own orders
- `GET /orders/seller` — order items where product belongs to current seller

#### [NEW] [backend/main.py](file:///G:/myDjangoProjects/marketplace-mvp/backend/main.py)
- App entry, include all routers
- `startup` event: create all tables + seed 6 categories if missing
- Mount `/static` for image serving
- CORS configured for `localhost:3000`

---

### Frontend

#### [NEW] Next.js 15 App Router project in `frontend/`
- Tailwind CSS for styling (Etsy-like, clean, mobile-first)
- `lib/api.ts` — typed fetch helpers pointing to `http://localhost:8000`
- `lib/auth.ts` — `localStorage` token helpers + decoded user info

**Pages:**
| Route | Purpose |
|---|---|
| `/` | Product catalog: grid, search bar, category filter, price range |
| `/products/[id]` | Product detail with image gallery |
| `/cart` | Cart from localStorage, qty controls, remove, go to checkout |
| `/checkout` | Summary → POST `/orders/checkout` → success redirect |
| `/login` & `/register` | Auth forms |
| `/orders` | Buyer: list own orders + items |
| `/dashboard` | Seller: list own products |
| `/dashboard/new` | Seller: create product with image upload |
| `/dashboard/edit/[id]` | Seller: edit product |
| `/dashboard/orders` | Seller: order items for their products |

---

## Verification Plan

### Manual End-to-End Tests (Browser)

**Flow 1 — Seller registers and lists a product:**
1. Open `http://localhost:3000/register` → register with a new email
2. Go to `/dashboard` → click "Become a Seller" (PATCH `/users/me` sets `is_seller=true`)
3. Click "New Product" → fill form, upload 1–3 images, submit
4. Confirm product appears in `/` catalog

**Flow 2 — Buyer purchases:**
1. Register a second email at `/register` (or open incognito)
2. Browse `/` → search/filter products → open product detail
3. Click "Add to Cart" → go to `/cart` → adjust quantity
4. Click "Checkout" → confirm success message
5. Go to `/orders` → confirm order with `status: paid_mock`

**Flow 3 — Seller sees the order:**
1. Switch back to seller account → go to `/dashboard/orders`
2. Confirm the buyer's order item appears with correct product, qty, price

**Swagger Smoke Test:**
- Open `http://localhost:8000/docs`
- Confirm all endpoints visible and correctly documented

### Stock Validation Test (manual via Swagger):
1. Create product with `stock=1`
2. Try to checkout with `quantity=2` → expect `400 Insufficient stock`
3. Checkout with `quantity=1` → expect success
4. Try to checkout again → expect `400 Out of stock`
