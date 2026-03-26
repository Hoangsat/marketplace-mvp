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
