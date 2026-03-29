# MarketPy MVP Task Checklist

## Planning
- [x] Create task.md
- [x] Create implementation_plan.md
- [x] Get user approval

## Backend
- [x] Project scaffold (main.py, database.py, auth.py, .env.example)
- [x] Models: User, Category, Product, Order, OrderItem
- [x] Schemas (Pydantic v2) for all models
- [x] Auth router: register, login (JWT)
- [x] Products router: CRUD, image upload
- [x] Orders router: mock checkout, buyer orders, seller order items
- [x] DB seeding: 6 categories on startup
- [x] Static file serving for /static/uploads

## Frontend
- [/] Next.js 15 project scaffold with Tailwind CSS
- [ ] Auth pages: login, register
- [ ] Product catalog page (search, filter by category/price)
- [ ] Product detail page
- [ ] Cart (localStorage)
- [ ] Mock checkout
- [ ] Seller dashboard: product CRUD + image upload
- [ ] Buyer orders page
- [ ] Seller orders page

## Verification
- [ ] End-to-end: seller registers → creates product with images
- [ ] End-to-end: buyer registers → adds to cart → mock checkout
- [ ] Confirm order appears for buyer and seller views
- [ ] README.md with setup instructions
- [ ] .env.example
- [ ] Notes on Vietnam payment gateway integration

## Payment Flow Refactor (Manual Bank Transfer)
- [x] Backend: Update `Order` model with new fields and statuses.
- [x] Backend: Update `schemas.py` for OrderOut.
- [x] Backend: Refactor `POST /orders/checkout` (no stock deduction, add `payment_reference`).
- [x] Backend: Create shared business logic `confirm_order_payment`.
- [x] Backend: Add `mark-payment-submitted`, `confirm-payment`, and `cancel` endpoints.
- [x] Frontend: Redirect to `/orders/[id]/payment` upon checkout success.
- [x] Frontend: Create `/orders/[id]/payment` page with "I have paid" workflow.
- [x] Frontend: Update buyer orders list to reflect the new payment statuses.
