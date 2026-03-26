# schemas/schemas.py
# Pydantic v2 schemas for request/response validation.
# Kept in one file for easy reading.

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, field_validator


# ─── Auth ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_seller: bool = False

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_seller: bool

    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    is_seller: bool

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── Category ────────────────────────────────────────────────────────────────

class CategoryOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


# ─── Product ─────────────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    title: str
    description: str
    price: float
    stock: int
    category_id: int

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @field_validator("stock")
    @classmethod
    def stock_not_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Stock cannot be negative")
        return v

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None

class ProductOut(BaseModel):
    id: int
    title: str
    description: str
    price: float
    stock: int
    images: List[str]
    seller_id: int
    category_id: int
    category: CategoryOut

    model_config = {"from_attributes": True}


# ─── Orders ──────────────────────────────────────────────────────────────────

class CheckoutItem(BaseModel):
    """One line item sent by the browser during checkout."""
    product_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Quantity must be at least 1")
        return v

class CheckoutRequest(BaseModel):
    items: List[CheckoutItem]

class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: float
    product: ProductOut

    model_config = {"from_attributes": True}

class OrderOut(BaseModel):
    id: int
    buyer_id: int
    total: float
    status: str
    created_at: datetime
    items: List[OrderItemOut]

    model_config = {"from_attributes": True}
