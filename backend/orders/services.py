import uuid

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import APIException

from catalog.models import Product

from .models import Order, OrderItem


class OrderFlowError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Order flow error"

    def __init__(self, detail, status_code=None):
        super().__init__(detail=detail)
        if status_code is not None:
            self.status_code = status_code


def create_checkout_order(*, buyer, items):
    if not items:
        raise OrderFlowError("Cart is empty", status.HTTP_400_BAD_REQUEST)

    products_to_buy = []
    for item in items:
        product = Product.objects.filter(id=item["product_id"]).first()
        if not product:
            raise OrderFlowError(
                f"Product {item['product_id']} not found",
                status.HTTP_404_NOT_FOUND,
            )
        if product.stock == 0:
            raise OrderFlowError(
                f"'{product.title}' is out of stock",
                status.HTTP_400_BAD_REQUEST,
            )
        if product.stock < item["quantity"]:
            raise OrderFlowError(
                f"Insufficient stock for '{product.title}'. Available: {product.stock}",
                status.HTTP_400_BAD_REQUEST,
            )
        products_to_buy.append((product, item["quantity"]))

    total = sum(product.price * qty for product, qty in products_to_buy)
    payment_ref = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    with transaction.atomic():
        order = Order.objects.create(
            buyer=buyer,
            total=round(total, 2),
            status=Order.Status.PAYMENT_PENDING,
            payment_method="manual_bank",
            payment_provider=None,
            payment_reference=payment_ref,
        )

        order_items = [
            OrderItem(
                order=order,
                product=product,
                quantity=qty,
                price_at_purchase=product.price,
            )
            for product, qty in products_to_buy
        ]
        OrderItem.objects.bulk_create(order_items)

    return _get_order_with_related(order.id)


def mark_payment_submitted(*, order_id, current_user):
    order = Order.objects.filter(id=order_id).first()
    if not order:
        raise OrderFlowError("Order not found", status.HTTP_404_NOT_FOUND)
    if order.buyer_id != current_user.id:
        raise OrderFlowError("Not your order", status.HTTP_403_FORBIDDEN)
    if order.status != Order.Status.PAYMENT_PENDING:
        raise OrderFlowError("Order is not pending payment", status.HTTP_400_BAD_REQUEST)

    order.buyer_marked_paid_at = timezone.now()
    order.save(update_fields=["buyer_marked_paid_at"])
    return _get_order_with_related(order.id)


def confirm_order_payment(*, order_id):
    order = _get_order_with_related(order_id)
    if not order:
        raise OrderFlowError("Order not found", status.HTTP_404_NOT_FOUND)

    if order.status == Order.Status.PAID:
        return order
    if order.status != Order.Status.PAYMENT_PENDING:
        raise OrderFlowError(
            f"Cannot confirm payment for order in status {order.status}",
            status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():
        order = _get_order_with_related(order_id)
        for item in order.items.all():
            if not item.product:
                raise OrderFlowError(
                    "A product in this order no longer exists.",
                    status.HTTP_400_BAD_REQUEST,
                )
            if item.product.stock < item.quantity:
                raise OrderFlowError(
                    f"Insufficient stock for '{item.product.title}' to fulfill this order now.",
                    status.HTTP_400_BAD_REQUEST,
                )

        for item in order.items.all():
            item.product.stock -= item.quantity
            item.product.save(update_fields=["stock"])

        order.status = Order.Status.PAID
        order.payment_confirmed_at = timezone.now()
        order.save(update_fields=["status", "payment_confirmed_at"])

    return _get_order_with_related(order_id)


def cancel_order(*, order_id):
    order = Order.objects.filter(id=order_id).first()
    if not order:
        raise OrderFlowError("Order not found", status.HTTP_404_NOT_FOUND)
    if order.status not in [Order.Status.PAYMENT_PENDING, Order.Status.DISPUTE]:
        raise OrderFlowError(
            "Cannot cancel order in current state",
            status.HTTP_400_BAD_REQUEST,
        )

    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status"])
    return _get_order_with_related(order.id)


def get_order_for_user(*, order_id, current_user):
    order = _get_order_with_related(order_id)
    if not order:
        raise OrderFlowError("Order not found", status.HTTP_404_NOT_FOUND)

    seller_ids = [item.product.seller_id for item in order.items.all() if item.product]
    if order.buyer_id != current_user.id and current_user.id not in seller_ids:
        raise OrderFlowError("Not your order", status.HTTP_403_FORBIDDEN)
    return order


def _get_order_with_related(order_id):
    return (
        Order.objects.filter(id=order_id)
        .prefetch_related("items__product__category")
        .select_related("buyer")
        .first()
    )
