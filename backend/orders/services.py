import uuid
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import APIException

from catalog.models import Product, filter_publicly_available_products

from .models import Order, OrderItem, SellerTransaction


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

    requested_quantities = {}
    for item in items:
        product_id = item["product_id"]
        requested_quantities[product_id] = (
            requested_quantities.get(product_id, 0) + item["quantity"]
        )

    products = {
        product.id: product
        for product in filter_publicly_available_products(
            Product.objects.filter(id__in=requested_quantities.keys())
        )
    }
    products_to_buy = []
    seller_ids = set()
    for product_id, quantity in requested_quantities.items():
        product = products.get(product_id)
        if not product:
            raise OrderFlowError(
                f"Product {product_id} not found",
                status.HTTP_404_NOT_FOUND,
            )
        if product.stock == 0:
            raise OrderFlowError(
                f"'{product.title}' is out of stock",
                status.HTTP_400_BAD_REQUEST,
            )
        if product.stock < quantity:
            raise OrderFlowError(
                f"Insufficient stock for '{product.title}'. Available: {product.stock}",
                status.HTTP_400_BAD_REQUEST,
            )
        products_to_buy.append((product, quantity))
        seller_ids.add(product.seller_id)

    if len(seller_ids) > 1:
        raise OrderFlowError(
            "Cart can only contain products from one seller. Please place separate orders.",
            status.HTTP_400_BAD_REQUEST,
        )

    total = sum(
        (product.price * qty for product, qty in products_to_buy),
        Decimal("0.00"),
    )
    payment_ref = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    with transaction.atomic():
        order = Order.objects.create(
            buyer=buyer,
            total=total.quantize(Decimal("0.01")),
            status=Order.Status.PENDING,
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
                product_title_snapshot=product.title,
                product_image_snapshot=(product.images or [None])[0] or "",
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
    if order.status != Order.Status.PENDING:
        raise OrderFlowError("Order is not pending payment", status.HTTP_400_BAD_REQUEST)

    order.buyer_marked_paid_at = timezone.now()
    order.save(update_fields=["buyer_marked_paid_at"])
    return _get_order_with_related(order.id)


def confirm_order_payment(*, order_id, current_user=None):
    order = _get_order_with_related(order_id)
    if not order:
        raise OrderFlowError("Order not found", status.HTTP_404_NOT_FOUND)
    if current_user is not None and order.buyer_id != current_user.id:
        raise OrderFlowError("Not your order", status.HTTP_403_FORBIDDEN)

    if order.status == Order.Status.PAID:
        return order
    if order.status != Order.Status.PENDING:
        raise OrderFlowError(
            f"Cannot confirm payment for order in status {order.status}",
            status.HTTP_400_BAD_REQUEST,
        )

    with transaction.atomic():
        order = _get_order_for_update(order_id)
        if order.status == Order.Status.PAID:
            return _get_order_with_related(order_id)
        if order.status != Order.Status.PENDING:
            raise OrderFlowError(
                f"Cannot confirm payment for order in status {order.status}",
                status.HTTP_400_BAD_REQUEST,
            )
        locked_products = {
            product.id: product
            for product in Product.objects.select_for_update().filter(
                id__in={item.product_id for item in order.items.all()}
            )
        }
        for item in order.items.all():
            product = locked_products.get(item.product_id)
            if not product:
                raise OrderFlowError(
                    "A product in this order no longer exists.",
                    status.HTTP_400_BAD_REQUEST,
                )
            if product.stock < item.quantity:
                raise OrderFlowError(
                    f"Insufficient stock for '{product.title}' to fulfill this order now.",
                    status.HTTP_400_BAD_REQUEST,
                )

        for item in order.items.all():
            product = locked_products[item.product_id]
            product.stock -= item.quantity
            if product.stock == 0:
                product.is_active = False
                product.save(update_fields=["stock", "is_active"])
            else:
                product.save(update_fields=["stock"])

        seller_amounts = _get_seller_amounts(order)
        for seller_id, seller_data in seller_amounts.items():
            seller = seller_data["seller"]
            amount = seller_data["amount"]
            seller_transaction, created = SellerTransaction.objects.get_or_create(
                seller=seller,
                order=order,
                defaults={
                    "amount": amount,
                    "status": SellerTransaction.Status.HOLD,
                },
            )
            if created:
                seller.__class__.objects.filter(id=seller_id).update(
                    balance_pending=F("balance_pending") + amount
                )
            elif seller_transaction.status != SellerTransaction.Status.HOLD:
                raise OrderFlowError(
                    "Seller transaction is not in a releasable hold state.",
                    status.HTTP_400_BAD_REQUEST,
                )

        order.status = Order.Status.PAID
        order.payment_confirmed_at = timezone.now()
        if order.buyer_marked_paid_at is None:
            order.buyer_marked_paid_at = timezone.now()
            order.save(
                update_fields=["status", "payment_confirmed_at", "buyer_marked_paid_at"]
            )
        else:
            order.save(update_fields=["status", "payment_confirmed_at"])

    return _get_order_with_related(order_id)


def cancel_order(*, order_id, current_user=None):
    order = Order.objects.filter(id=order_id).first()
    if not order:
        raise OrderFlowError("Order not found", status.HTTP_404_NOT_FOUND)
    if current_user is not None:
        if order.buyer_id != current_user.id:
            raise OrderFlowError("Not your order", status.HTTP_403_FORBIDDEN)
        if order.status != Order.Status.PENDING:
            raise OrderFlowError(
                "Only pending orders can be cancelled",
                status.HTTP_400_BAD_REQUEST,
            )
    elif order.status not in [Order.Status.PENDING, Order.Status.DISPUTE]:
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

    seller_ids = {item.product.seller_id for item in order.items.all() if item.product}
    if order.buyer_id == current_user.id:
        return order
    if seller_ids == {current_user.id}:
        return order
    if current_user.id not in seller_ids:
        raise OrderFlowError("Not your order", status.HTTP_403_FORBIDDEN)
    raise OrderFlowError("Not your order", status.HTTP_403_FORBIDDEN)


def release_order_funds(*, order_id):
    with transaction.atomic():
        order = _get_order_for_update(order_id)
        if not order:
            raise OrderFlowError("Order not found", status.HTTP_404_NOT_FOUND)
        if order.status != Order.Status.PAID:
            raise OrderFlowError(
                "Only paid orders can release seller funds",
                status.HTTP_400_BAD_REQUEST,
            )

        hold_transactions = list(
            order.seller_transactions.select_related("seller").filter(
                status=SellerTransaction.Status.HOLD
            )
        )
        if not hold_transactions:
            raise OrderFlowError(
                "This order has no held seller funds to release",
                status.HTTP_400_BAD_REQUEST,
            )

        for seller_transaction in hold_transactions:
            seller = seller_transaction.seller
            if seller.balance_pending < seller_transaction.amount:
                raise OrderFlowError(
                    f"Seller {seller.email} does not have enough pending balance to release",
                    status.HTTP_400_BAD_REQUEST,
                )
            seller.__class__.objects.filter(id=seller.id).update(
                balance_pending=F("balance_pending") - seller_transaction.amount,
                balance_available=F("balance_available") + seller_transaction.amount,
            )

            seller_transaction.status = SellerTransaction.Status.AVAILABLE
            seller_transaction.save(update_fields=["status", "updated_at"])

    return _get_order_with_related(order_id)


def mark_seller_transaction_paid_out(*, seller_transaction_id):
    with transaction.atomic():
        seller_transaction = (
            SellerTransaction.objects.select_for_update()
            .select_related("seller")
            .filter(id=seller_transaction_id)
            .first()
        )
        if not seller_transaction:
            raise OrderFlowError("Seller transaction not found", status.HTTP_404_NOT_FOUND)
        if seller_transaction.status != SellerTransaction.Status.AVAILABLE:
            raise OrderFlowError(
                "Only available seller transactions can be marked as paid out",
                status.HTTP_400_BAD_REQUEST,
            )

        updated_count = seller_transaction.seller.__class__.objects.filter(
            id=seller_transaction.seller_id,
            balance_available__gte=seller_transaction.amount,
        ).update(balance_available=F("balance_available") - seller_transaction.amount)
        if not updated_count:
            raise OrderFlowError(
                "Seller does not have enough available balance to pay out",
                status.HTTP_400_BAD_REQUEST,
            )

        seller_transaction.status = SellerTransaction.Status.PAID_OUT
        seller_transaction.paid_at = timezone.now()
        seller_transaction.save(update_fields=["status", "paid_at", "updated_at"])

    return seller_transaction


def mark_order_delivered(*, order_id, current_user):
    with transaction.atomic():
        order = _get_order_for_update(order_id)
        if not order:
            raise OrderFlowError("Order not found", status.HTTP_404_NOT_FOUND)

        seller_ids = {item.product.seller_id for item in order.items.all() if item.product}
        if seller_ids != {current_user.id}:
            raise OrderFlowError("Not your order", status.HTTP_403_FORBIDDEN)
        if order.status != Order.Status.PAID:
            raise OrderFlowError(
                "Only paid orders can be marked as delivered",
                status.HTTP_400_BAD_REQUEST,
            )

        release_order_funds(order_id=order.id)
        order.status = Order.Status.DELIVERED
        order.delivered_at = timezone.now()
        order.save(update_fields=["status", "delivered_at"])

    return _get_order_with_related(order_id)


def mark_order_completed(*, order_id, current_user):
    with transaction.atomic():
        order = _get_order_for_update(order_id)
        if not order:
            raise OrderFlowError("Order not found", status.HTTP_404_NOT_FOUND)
        if order.buyer_id != current_user.id:
            raise OrderFlowError("Not your order", status.HTTP_403_FORBIDDEN)
        if order.status != Order.Status.DELIVERED:
            raise OrderFlowError(
                "Only delivered orders can be marked as completed",
                status.HTTP_400_BAD_REQUEST,
            )

        order.status = Order.Status.COMPLETED
        order.save(update_fields=["status"])

    return _get_order_with_related(order_id)


def auto_complete_delivered_orders(queryset):
    """
    Lazy auto-complete: updates delivered orders older than 3 days to completed.
    Applied only to the current user's queryset.
    """
    cutoff = timezone.now() - timedelta(days=3)
    queryset.filter(
        status=Order.Status.DELIVERED,
        delivered_at__isnull=False,
        delivered_at__lte=cutoff,
    ).update(status=Order.Status.COMPLETED)
    return queryset


def _get_order_with_related(order_id):
    return (
        Order.objects.filter(id=order_id)
        .prefetch_related(
            "items__product__category",
            "items__product__platform",
            "items__product__platform__category",
            "items__product__offer_type",
            "seller_transactions__seller",
        )
        .select_related("buyer")
        .first()
    )


def _get_order_for_update(order_id):
    return (
        Order.objects.select_for_update()
        .filter(id=order_id)
        .prefetch_related(
            "items__product__seller",
            "items__product__platform",
            "items__product__platform__category",
            "items__product__offer_type",
        )
        .select_related("buyer")
        .first()
    )


def _get_seller_amounts(order):
    seller_amounts = {}
    for item in order.items.all():
        seller_id = item.product.seller_id
        line_total = Decimal(str(item.price_at_purchase)) * Decimal(item.quantity)
        if seller_id not in seller_amounts:
            seller_amounts[seller_id] = {
                "seller": item.product.seller,
                "amount": Decimal("0.00"),
            }
        seller_amounts[seller_id]["amount"] += line_total
    return seller_amounts


def make_hold_seller_transactions_available(order):
    seller_transactions = order.seller_transactions.filter(
        status=SellerTransaction.Status.HOLD
    )
    for seller_transaction in seller_transactions:
        seller_transaction.status = SellerTransaction.Status.AVAILABLE
        seller_transaction.save(update_fields=["status", "updated_at"])
