from django.conf import settings
from django.db import models

from catalog.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PAYMENT_PENDING = "payment_pending", "payment_pending"
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
        default=Status.PAYMENT_PENDING,
    )
    payment_method = models.CharField(max_length=64, default="manual_bank")
    payment_provider = models.CharField(max_length=64, null=True, blank=True)
    payment_reference = models.CharField(max_length=255, unique=True, null=True, blank=True)
    payment_confirmed_at = models.DateTimeField(null=True, blank=True)
    buyer_marked_paid_at = models.DateTimeField(null=True, blank=True)
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
