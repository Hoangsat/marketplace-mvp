from django.conf import settings
from django.db import models


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "categories"

    def __str__(self) -> str:
        return self.name


class Game(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    display_name_vi = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "games"

    def __str__(self) -> str:
        return self.name


class OfferType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    display_name_vi = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "offer_types"

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    stock = models.IntegerField(default=0)
    images = models.JSONField(default=list, blank=True)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
    )
    game = models.ForeignKey(
        "catalog.Game",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
    )
    offer_type = models.ForeignKey(
        "catalog.OfferType",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="products",
    )

    class Meta:
        db_table = "products"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gt=0),
                name="product_price_gt_0",
            ),
            models.CheckConstraint(
                condition=models.Q(stock__gte=0),
                name="product_stock_gte_0",
            ),
        ]

    def __str__(self) -> str:
        return self.title
