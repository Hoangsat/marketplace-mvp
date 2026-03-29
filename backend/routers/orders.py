# routers/orders.py
# Mock checkout, buyer order history, seller order items.

from datetime import datetime
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth import get_current_user
from database import get_db
from models.models import Order, OrderItem, Product, User
from schemas.schemas import CheckoutRequest, OrderItemOut, OrderOut

router = APIRouter(prefix="/orders", tags=["Orders"])
admin_router = APIRouter(prefix="/admin/orders", tags=["Admin"])


@router.post("/checkout", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def mock_checkout(
    checkout: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Checkout (manual bank flow):
    1. Validate all items have sufficient stock
    2. Create Order with status payment_pending and a unique payment_reference
    3. Create OrderItems — stock is not reduced until confirm_order_payment

    Replace with a real payment gateway later; see README.md for PayOS / VNPay / MoMo notes.
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
    payment_ref = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    order = Order(
        buyer_id=current_user.id,
        total=round(total, 2),
        status="payment_pending",
        payment_method="manual_bank",
        payment_provider=None,
        payment_reference=payment_ref,
    )
    db.add(order)
    db.flush()  # Get order.id without committing yet

    # ── Step 4: Create OrderItems ──────────────────────────────────────────
    for product, qty in products_to_buy:
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=qty,
            price_at_purchase=product.price,
        )
        db.add(order_item)
        # Note: Stock is NOT deducted here. Stock is only deducted when payment is confirmed.

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
    return (
        db.query(OrderItem)
        .join(Product)
        .join(Order)
        .filter(Product.seller_id == current_user.id)
        .filter(Order.status != "payment_pending")
        .all()
    )


# ─── Shared Business Logic ───────────────────────────────────────────────────

def confirm_order_payment(order_id: int, db: Session, admin_note: str = None) -> Order:
    """
    SINGLE place where order goes from payment_pending to paid.
    Deducts stock securely and marks payment timestamps.
    """
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status == "paid":
        return order  # Idempotent
    if order.status != "payment_pending":
        raise HTTPException(status_code=400, detail=f"Cannot confirm payment for order in status {order.status}")

    # Validate stock is STILL available
    for item in order.items:
        if not item.product:
            raise HTTPException(
                status_code=400, 
                detail="A product in this order no longer exists."
            )
        if item.product.stock < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock for '{item.product.title}' to fulfill this order now."
            )

    # Deduct stock
    for item in order.items:
        item.product.stock -= item.quantity

    # Update order
    order.status = "paid"
    order.payment_confirmed_at = func.now()

    db.commit()
    db.refresh(order)
    return order


# ─── New Payment Action Endpoints ──────────────────────────────────────────────

@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a single order by ID."""
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.buyer_id != current_user.id and current_user.id not in [i.product.seller_id for i in order.items if i.product]: 
        # In production, check is_admin, or verify user is buyer/seller of this order
        raise HTTPException(status_code=403, detail="Not your order")
    return order


@router.post("/{order_id}/mark-payment-submitted", response_model=OrderOut)
def mark_payment_submitted(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Buyer signals they have sent the bank transfer."""
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.buyer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your order")
    
    if order.status != "payment_pending":
        raise HTTPException(status_code=400, detail="Order is not pending payment")

    order.buyer_marked_paid_at = func.now()
    db.commit()
    db.refresh(order)
    return order


@admin_router.post("/{order_id}/confirm-payment", response_model=OrderOut)
def admin_confirm_payment(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Admin confirms the manual bank transfer arrived.
    For this MVP, we allow any authenticated user to act as admin.
    """
    # In production: if not current_user.is_admin: raise 403
    return confirm_order_payment(order_id, db)


@admin_router.post("/{order_id}/cancel", response_model=OrderOut)
def admin_cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel an unpaid order."""
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status not in ["payment_pending", "dispute"]:
        raise HTTPException(status_code=400, detail="Cannot cancel order in current state")

    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    return order
