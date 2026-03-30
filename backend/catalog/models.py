from django.conf import settings
from django.db import models


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "categories"

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    price = models.FloatField()
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

    class Meta:
        db_table = "products"

    def __str__(self) -> str:
        return self.title
