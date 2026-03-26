# routers/orders.py
# Mock checkout, buyer order history, seller order items.

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models.models import Order, OrderItem, Product, User
from schemas.schemas import CheckoutRequest, OrderItemOut, OrderOut

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/checkout", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def mock_checkout(
    checkout: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Mock checkout flow:
    1. Validate all items have sufficient stock
    2. Create Order with status "paid_mock"
    3. Create OrderItems and deduct stock
    
    This is easy to replace with a real payment gateway later.
    See README.md for notes on PayOS / VNPay / MoMo integration.
    """
    if not checkout.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # ── Step 1: Validate stock for ALL items before touching the DB ────────
    products_to_buy = []
    for item in checkout.items:
        product = db.get(Product, item.product_id)
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found",
            )
        if product.stock == 0:
            raise HTTPException(
                status_code=400,
                detail=f"'{product.title}' is out of stock",
            )
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for '{product.title}'. Available: {product.stock}",
            )
        products_to_buy.append((product, item.quantity))

    # ── Step 2: Calculate total ────────────────────────────────────────────
    total = sum(product.price * qty for product, qty in products_to_buy)

    # ── Step 3: Create Order ───────────────────────────────────────────────
    order = Order(
        buyer_id=current_user.id,
        total=round(total, 2),
        status="paid_mock",
    )
    db.add(order)
    db.flush()  # Get order.id without committing yet

    # ── Step 4: Create OrderItems and deduct stock ─────────────────────────
    for product, qty in products_to_buy:
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=qty,
            price_at_purchase=product.price,
        )
        db.add(order_item)
        product.stock -= qty  # Deduct stock immediately

    db.commit()
    db.refresh(order)
    return order


@router.get("/buyer", response_model=List[OrderOut])
def get_buyer_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all orders placed by the current buyer (sorted newest first)."""
    return (
        db.query(Order)
        .filter(Order.buyer_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )


@router.get("/seller", response_model=List[OrderItemOut])
def get_seller_order_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return all order items where the product belongs to the current seller.
    Sellers only see line items for their own products — not the full order.
    """
    if not current_user.is_seller:
        raise HTTPException(status_code=403, detail="Only sellers can view this")

    return (
        db.query(OrderItem)
        .join(Product)
        .filter(Product.seller_id == current_user.id)
        .all()
    )
