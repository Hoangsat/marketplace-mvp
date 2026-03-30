from decimal import Decimal

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from catalog.models import Category, Product
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer
from orders.services import create_checkout_order


class CheckoutFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.buyer = User.objects.create_user(
            email="buyer@example.com",
            password="password123",
            is_seller=False,
        )
        self.seller_one = User.objects.create_user(
            email="seller-one@example.com",
            password="password123",
        )
        self.seller_two = User.objects.create_user(
            email="seller-two@example.com",
            password="password123",
        )
        self.category, _ = Category.objects.get_or_create(name="Games")
        self.product_one = Product.objects.create(
            title="Seller One Product",
            description="First product",
            price=Decimal("15.00"),
            stock=5,
            images=["uploads/seller-one.png"],
            seller=self.seller_one,
            category=self.category,
        )
        self.product_two = Product.objects.create(
            title="Seller Two Product",
            description="Second product",
            price=Decimal("18.00"),
            stock=5,
            images=["uploads/seller-two.png"],
            seller=self.seller_two,
            category=self.category,
        )

    def test_checkout_rejects_mixed_seller_cart(self):
        self.client.force_authenticate(user=self.buyer)

        response = self.client.post(
            "/orders/checkout",
            {
                "items": [
                    {"product_id": self.product_one.id, "quantity": 1},
                    {"product_id": self.product_two.id, "quantity": 1},
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["detail"],
            "Cart can only contain products from one seller. Please place separate orders.",
        )

    def test_checkout_populates_snapshot_fields(self):
        self.client.force_authenticate(user=self.buyer)

        response = self.client.post(
            "/orders/checkout",
            {"items": [{"product_id": self.product_one.id, "quantity": 2}]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_item = OrderItem.objects.get(order_id=response.json()["id"])
        self.assertEqual(order_item.product_title_snapshot, "Seller One Product")
        self.assertEqual(order_item.product_image_snapshot, "uploads/seller-one.png")


class OrderHistorySnapshotTests(TestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(
            email="buyer@example.com",
            password="password123",
            is_seller=False,
        )
        self.seller = User.objects.create_user(
            email="seller@example.com",
            password="password123",
        )
        self.category, _ = Category.objects.get_or_create(name="Games")
        self.product = Product.objects.create(
            title="Original Title",
            description="Original description",
            price=Decimal("25.00"),
            stock=10,
            images=["uploads/original.png"],
            seller=self.seller,
            category=self.category,
        )

    def _create_order(self):
        return create_checkout_order(
            buyer=self.buyer,
            items=[{"product_id": self.product.id, "quantity": 1}],
        )

    def test_order_serializer_uses_snapshot_fields_after_product_changes(self):
        order = self._create_order()

        self.product.title = "Updated Title"
        self.product.price = Decimal("99.00")
        self.product.images = ["uploads/updated.png"]
        self.product.save(update_fields=["title", "price", "images"])

        serialized = OrderSerializer(
            Order.objects.prefetch_related("items__product__category").get(id=order.id)
        ).data

        self.assertEqual(serialized["items"][0]["product_title"], "Original Title")
        self.assertEqual(
            serialized["items"][0]["product_image"],
            "/media/uploads/original.png",
        )
        self.assertEqual(serialized["items"][0]["price_at_purchase"], 25.0)

    @override_settings(
        MANUAL_PAYMENT_BANK_NAME="Test Bank",
        MANUAL_PAYMENT_ACCOUNT_NAME="Marketplace Ltd",
        MANUAL_PAYMENT_ACCOUNT_NUMBER="123456789",
        MANUAL_PAYMENT_NOTE="Use the order reference as the memo.",
    )
    def test_order_serializer_returns_backend_payment_instructions(self):
        order = self._create_order()

        serialized = OrderSerializer(order).data

        self.assertEqual(
            serialized["payment_instructions"],
            {
                "bank_name": "Test Bank",
                "account_name": "Marketplace Ltd",
                "account_number": "123456789",
                "note": "Use the order reference as the memo.",
            },
        )
