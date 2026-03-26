# main.py
# FastAPI application entry point.
# Run with: uvicorn main:app --reload

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from models.models import Category
from routers import auth, orders, products, users

# ─── Create the App ───────────────────────────────────────────────────────────

app = FastAPI(
    title="MarketPy API",
    description="Simple two-sided marketplace MVP — sellers list products, buyers place orders.",
    version="1.0.0",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
# Allow the Next.js frontend (localhost:3000) to call the API.
# In production, replace "*" origins with your actual domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static Files ─────────────────────────────────────────────────────────────
# Uploaded product images are served from /static/uploads/
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(os.path.join(STATIC_DIR, "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)


# ─── Startup: Create Tables + Seed Categories ─────────────────────────────────

SEED_CATEGORIES = ["Electronics", "Clothing", "Home", "Books", "Beauty", "Sports"]


@app.on_event("startup")
def startup():
    """Create all DB tables and seed default categories on first run."""
    # Create tables if they don't exist yet
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        for name in SEED_CATEGORIES:
            exists = db.query(Category).filter(Category.name == name).first()
            if not exists:
                db.add(Category(name=name))
        db.commit()
    finally:
        db.close()


# ─── Health Check ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "MarketPy API is running 🎉"}
