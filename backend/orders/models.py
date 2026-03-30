from django.conf import settings
from django.db import models

from catalog.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "pending"
        PAID = "paid", "paid"
        DELIVERED = "delivered", "delivered"
        COMPLETED = "completed", "completed"
        CANCELLED = "cancelled", "cancelled"
        DISPUTE = "dispute", "dispute"

    id = models.AutoField(primary_key=True)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    total = models.FloatField()
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
    )
    payment_method = models.CharField(max_length=64, default="manual_bank")
    payment_provider = models.CharField(max_length=64, null=True, blank=True)
    payment_reference = models.CharField(max_length=255, unique=True, null=True, blank=True)
    payment_confirmed_at = models.DateTimeField(null=True, blank=True)
    buyer_marked_paid_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "orders"

    def __str__(self) -> str:
        return f"Order #{self.pk}"


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.IntegerField()
    price_at_purchase = models.FloatField()

    class Meta:
        db_table = "order_items"

    def __str__(self) -> str:
        return f"OrderItem #{self.pk}"


class SellerTransaction(models.Model):
    class Status(models.TextChoices):
        HOLD = "hold", "Hold"
        AVAILABLE = "available", "Available"
        PAID_OUT = "paid_out", "Paid Out"

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="seller_transactions",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="seller_transactions",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "seller_transactions"
        constraints = [
            models.UniqueConstraint(
                fields=["seller", "order"],
                name="unique_seller_transaction_per_order",
            )
        ]

    def __str__(self) -> str:
        return f"SellerTransaction #{self.pk}"
