from decimal import Decimal

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from catalog.models import Category, Product
from catalog.serializers import ProductSerializer
from orders.services import create_checkout_order


class ProductDeletionProtectionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.seller = User.objects.create_user(
            email="seller@example.com",
            password="password123",
        )
        self.buyer = User.objects.create_user(
            email="buyer@example.com",
            password="password123",
            is_seller=False,
        )
        self.category, _ = Category.objects.get_or_create(name="Games")
        self.sold_product = Product.objects.create(
            title="Sold Product",
            description="Already sold",
            price=Decimal("10.00"),
            stock=3,
            images=["uploads/sold.png"],
            seller=self.seller,
            category=self.category,
        )
        self.unsold_product = Product.objects.create(
            title="Unsold Product",
            description="Still safe to delete",
            price=Decimal("12.00"),
            stock=3,
            images=["uploads/unsold.png"],
            seller=self.seller,
            category=self.category,
        )
        create_checkout_order(
            buyer=self.buyer,
            items=[{"product_id": self.sold_product.id, "quantity": 1}],
        )
        self.client.force_authenticate(user=self.seller)

    def test_sold_product_is_soft_deleted_via_api_when_protected(self):
        response = self.client.delete(f"/products/{self.sold_product.id}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Product.objects.filter(id=self.sold_product.id).exists())
        self.sold_product.refresh_from_db()
        self.assertFalse(self.sold_product.is_active)

    def test_unsold_product_can_be_deleted_via_api(self):
        response = self.client.delete(f"/products/{self.unsold_product.id}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.unsold_product.id).exists())


class ProductSerializerMediaTests(TestCase):
    @override_settings(MEDIA_PUBLIC_BASE_URL="https://media.example.com")
    def test_product_serializer_normalizes_legacy_and_storage_image_paths(self):
        seller = User.objects.create_user(
            email="seller@example.com",
            password="password123",
        )
        category, _ = Category.objects.get_or_create(name="Games")
        product = Product.objects.create(
            title="Media Product",
            description="Image handling",
            price=Decimal("20.00"),
            stock=4,
            images=[
                "uploads/storage-path.png",
                "/media/uploads/legacy-path.png",
                "https://cdn.example.com/already-absolute.png",
            ],
            seller=seller,
            category=category,
        )

        serialized = ProductSerializer(product).data

        self.assertEqual(
            serialized["images"],
            [
                "https://media.example.com/media/uploads/storage-path.png",
                "https://media.example.com/media/uploads/legacy-path.png",
                "https://cdn.example.com/already-absolute.png",
            ],
        )


class PublicCatalogVisibilityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.seller = User.objects.create_user(
            email="seller@example.com",
            password="password123",
        )
        self.category, _ = Category.objects.get_or_create(name="Games")
        self.visible_product = Product.objects.create(
            title="Visible Product",
            description="In stock and active",
            price=Decimal("15.00"),
            stock=2,
            seller=self.seller,
            category=self.category,
        )
        Product.objects.create(
            title="Sold Out Product",
            description="No stock left",
            price=Decimal("18.00"),
            stock=0,
            seller=self.seller,
            category=self.category,
        )
        Product.objects.create(
            title="Inactive Product",
            description="Disabled product",
            price=Decimal("20.00"),
            stock=5,
            is_active=False,
            seller=self.seller,
            category=self.category,
        )

    def test_public_catalog_only_returns_buyable_products(self):
        response = self.client.get("/products")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.visible_product.id)

    def test_public_product_detail_hides_inactive_product(self):
        inactive_product = Product.objects.filter(title="Inactive Product").get()

        response = self.client.get(f"/products/{inactive_product.id}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Product not found")

    def test_seller_can_still_view_own_inactive_product_detail(self):
        inactive_product = Product.objects.filter(title="Inactive Product").get()
        self.client.force_authenticate(user=self.seller)

        response = self.client.get(f"/products/{inactive_product.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], inactive_product.id)
