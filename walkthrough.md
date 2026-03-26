# MarketPy Frontend — Build Complete ✅

## What Was Built

Next.js 15 (App Router, TypeScript, Tailwind CSS) frontend in `./frontend/`, connecting to the FastAPI backend at `http://localhost:8000`.

---

## Files Created

| File | Purpose |
|---|---|
| [lib/api.ts](file:///g:/myDjangoProjects/marketplace-mvp/frontend/lib/api.ts) | Fetch wrapper — prepends base URL, attaches Bearer JWT |
| [lib/auth.ts](file:///g:/myDjangoProjects/marketplace-mvp/frontend/lib/auth.ts) | JWT helpers — getToken / setToken / removeToken |
| [lib/cart.ts](file:///g:/myDjangoProjects/marketplace-mvp/frontend/lib/cart.ts) | localStorage cart — add / remove / update / clear |
| [lib/types.ts](file:///g:/myDjangoProjects/marketplace-mvp/frontend/lib/types.ts) | Shared TS types matching backend schemas |
| [components/Navbar.tsx](file:///g:/myDjangoProjects/marketplace-mvp/frontend/components/Navbar.tsx) | Sticky nav — auth state, cart count badge |
| [components/ProductCard.tsx](file:///g:/myDjangoProjects/marketplace-mvp/frontend/components/ProductCard.tsx) | Product grid card with next/image |
| [components/Toast.tsx](file:///g:/myDjangoProjects/marketplace-mvp/frontend/components/Toast.tsx) | Singleton toast — call [showToast()](file:///g:/myDjangoProjects/marketplace-mvp/frontend/components/Toast.tsx#19-23) anywhere |
| [app/layout.tsx](file:///g:/myDjangoProjects/marketplace-mvp/frontend/app/layout.tsx) | Root layout wrapping Navbar + Toast |
| [app/page.tsx](file:///g:/myDjangoProjects/marketplace-mvp/frontend/app/page.tsx) | Home catalog with debounced search + live filters |
| [app/login/page.tsx](file:///g:/myDjangoProjects/marketplace-mvp/frontend/app/login/page.tsx) | Login (form-encoded for OAuth2PasswordRequestForm) |
| [app/register/page.tsx](file:///g:/myDjangoProjects/marketplace-mvp/frontend/app/register/page.tsx) | Register with is_seller checkbox |
| `app/products/[id]/page.tsx` | Product detail with image gallery + add to cart |
| [app/cart/page.tsx](file:///g:/myDjangoProjects/marketplace-mvp/frontend/app/cart/page.tsx) | Cart view with qty edit + remove |
| [app/checkout/page.tsx](file:///g:/myDjangoProjects/marketplace-mvp/frontend/app/checkout/page.tsx) | Mock checkout — calls POST /orders/checkout |
| [app/orders/page.tsx](file:///g:/myDjangoProjects/marketplace-mvp/frontend/app/orders/page.tsx) | Buyer order history |
| [app/seller/dashboard/page.tsx](file:///g:/myDjangoProjects/marketplace-mvp/frontend/app/seller/dashboard/page.tsx) | Seller product list with delete |
| [app/seller/orders/page.tsx](file:///g:/myDjangoProjects/marketplace-mvp/frontend/app/seller/orders/page.tsx) | Seller order items (own products only) |
| [app/seller/products/new/page.tsx](file:///g:/myDjangoProjects/marketplace-mvp/frontend/app/seller/products/new/page.tsx) | Create product with image upload |
| `app/seller/products/[id]/edit/page.tsx` | Edit product + optional image replacement |

---

## Dev Server Verification

```
▲ Next.js 16.2.1 (Turbopack)
- Local: http://localhost:3000
✓ Zero compilation errors
✓ Zero console errors on home, login, register pages
```

## Screenshots

![Home Page](C:\Users\hoang\.gemini\antigravity\brain\04f134ca-69d9-460a-b713-a61a7479c406\frontend_home_page_1774552021706.png)

![Register Page](C:\Users\hoang\.gemini\antigravity\brain\04f134ca-69d9-460a-b713-a61a7479c406\frontend_register_page_1774552023080.png)

---

## How to Run

```bash
# Terminal 1 — Backend
cd backend && uvicorn main:app --reload

# Terminal 2 — Frontend
cd frontend && npm run dev
```

Backend: http://localhost:8000  
Frontend: http://localhost:3000  
API Docs: http://localhost:8000/docs
