# routers/products.py
# Product CRUD + image upload + public listing with search & filters.

import os
import shutil
import uuid
from typing import List, Optional

from fastapi import (
    APIRouter, Depends, File, Form, HTTPException,
    Query, UploadFile, status
)
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models.models import Category, Product, User
from schemas.schemas import CategoryOut, ProductCreate, ProductOut, ProductUpdate

router = APIRouter(tags=["Products"])

# Where uploaded images are stored on disk
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "static", "uploads")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
MAX_IMAGES_PER_PRODUCT = 5


def _save_images(files: List[UploadFile]) -> List[str]:
    """Validate and save uploaded image files. Returns list of URL paths."""
    if len(files) > MAX_IMAGES_PER_PRODUCT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_IMAGES_PER_PRODUCT} images allowed",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    saved_paths = []

    for file in files:
        # Check extension
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{file.filename}' is not allowed. Use jpg, jpeg, or png.",
            )

        # Read and check size
        content = file.file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{file.filename}' exceeds 5MB limit",
            )

        # Save with a unique filename to avoid collisions
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        dest_path = os.path.join(UPLOAD_DIR, unique_name)
        with open(dest_path, "wb") as f:
            f.write(content)

        saved_paths.append(f"/static/uploads/{unique_name}")

    return saved_paths


# ─── Public Endpoints (no auth required) ─────────────────────────────────────

@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    """List all product categories."""
    return db.query(Category).all()


@router.get("/products", response_model=List[ProductOut])
def list_products(
    search: Optional[str] = Query(None, description="Search in title"),
    category_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    db: Session = Depends(get_db),
):
    """List products with optional search and filters."""
    q = db.query(Product)

    if search:
        q = q.filter(Product.title.ilike(f"%{search}%"))
    if category_id:
        q = q.filter(Product.category_id == category_id)
    if min_price is not None:
        q = q.filter(Product.price >= min_price)
    if max_price is not None:
        q = q.filter(Product.price <= max_price)

    return q.all()


@router.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product by ID."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# ─── Seller Endpoints (auth + is_seller required) ────────────────────────────

@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    category_id: int = Form(...),
    images: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new product (seller only). Accepts multipart form with up to 5 images."""
    # Validate via Pydantic (manually since we use Form fields)
    data = ProductCreate(
        title=title, description=description,
        price=price, stock=stock, category_id=category_id
    )

    # Confirm category exists
    category = db.get(Category, data.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    image_paths = _save_images(images) if images else []

    product = Product(
        title=data.title,
        description=data.description,
        price=data.price,
        stock=data.stock,
        category_id=data.category_id,
        seller_id=current_user.id,
        images=image_paths,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/products/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update product fields (JSON body, no image update here — use separate upload)."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your product")

    # Only update provided fields
    for field, value in update.model_dump(exclude_none=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.post("/products/{product_id}/images", response_model=ProductOut)
def add_product_images(
    product_id: int,
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Replace all images for a product (seller only)."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your product")

    new_paths = _save_images(images)
    product.images = new_paths
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a product (seller only, own products only)."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your product")

    db.delete(product)
    db.commit()


@router.get("/seller/products", response_model=List[ProductOut])
def list_my_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all products belonging to the currently authenticated seller."""
    return db.query(Product).filter(Product.seller_id == current_user.id).all()
