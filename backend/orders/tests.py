from decimal import Decimal

from django.contrib.admin.sites import AdminSite
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from catalog.models import Category, OfferType, Platform, Product
from orders.admin import OrderAdmin
from orders.models import Order, OrderItem, SellerTransaction
from orders.serializers import OrderSerializer
from orders.services import (
    OrderFlowError,
    confirm_order_payment,
    create_checkout_order,
    mark_order_delivered,
)


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

    def test_checkout_rejects_inactive_product(self):
        self.product_one.is_active = False
        self.product_one.save(update_fields=["is_active"])
        self.client.force_authenticate(user=self.buyer)

        response = self.client.post(
            "/orders/checkout",
            {"items": [{"product_id": self.product_one.id, "quantity": 1}]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.json()["detail"],
            f"Product {self.product_one.id} not found",
        )
        self.assertFalse(Order.objects.filter(buyer=self.buyer).exists())

    def test_checkout_rejects_product_under_inactive_platform(self):
        inactive_platform = Platform.objects.create(
            name="Lineage 2",
            slug="lineage-2-checkout-hidden",
            category=self.category,
            is_active=False,
        )
        hidden_product = Product.objects.create(
            title="Inactive Platform Product",
            description="Hidden in checkout",
            price=Decimal("19.00"),
            stock=2,
            seller=self.seller_one,
            category=self.category,
            platform=inactive_platform,
        )
        self.client.force_authenticate(user=self.buyer)

        response = self.client.post(
            "/orders/checkout",
            {"items": [{"product_id": hidden_product.id, "quantity": 1}]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.json()["detail"],
            f"Product {hidden_product.id} not found",
        )
        self.assertFalse(Order.objects.filter(buyer=self.buyer).exists())

    def test_checkout_rejects_product_under_inactive_offer_type(self):
        active_platform = Platform.objects.create(
            name="Steam",
            slug="steam-checkout-visible",
            category=self.category,
        )
        inactive_offer_type = OfferType.objects.create(
            platform=active_platform,
            name="Accounts",
            slug="accounts-checkout-hidden",
            is_active=False,
        )
        hidden_product = Product.objects.create(
            title="Inactive Offer Type Product",
            description="Hidden in checkout",
            price=Decimal("20.00"),
            stock=2,
            seller=self.seller_one,
            category=self.category,
            platform=active_platform,
            offer_type=inactive_offer_type,
        )
        self.client.force_authenticate(user=self.buyer)

        response = self.client.post(
            "/orders/checkout",
            {"items": [{"product_id": hidden_product.id, "quantity": 1}]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.json()["detail"],
            f"Product {hidden_product.id} not found",
        )
        self.assertFalse(Order.objects.filter(buyer=self.buyer).exists())


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


class OrderPaymentStockUpdateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
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
            title="Stock Sensitive Product",
            description="Checks stock changes on payment confirmation",
            price=Decimal("30.00"),
            stock=5,
            seller=self.seller,
            category=self.category,
        )

    def _create_order(self, quantity):
        return create_checkout_order(
            buyer=self.buyer,
            items=[{"product_id": self.product.id, "quantity": quantity}],
        )

    def test_confirm_order_payment_reduces_product_stock(self):
        order = self._create_order(quantity=2)

        confirm_order_payment(order_id=order.id)

        self.product.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertTrue(self.product.is_active)
        self.assertEqual(order.status, Order.Status.PAID)

    def test_confirm_order_payment_marks_product_inactive_when_stock_reaches_zero(self):
        self.product.stock = 1
        self.product.save(update_fields=["stock"])
        order = self._create_order(quantity=1)

        confirm_order_payment(order_id=order.id)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 0)
        self.assertFalse(self.product.is_active)

        response = self.client.get(f"/products/{self.product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_confirm_order_payment_fails_safely_when_stock_is_no_longer_available(self):
        order = self._create_order(quantity=2)
        self.product.stock = 1
        self.product.save(update_fields=["stock"])

        with self.assertRaisesMessage(
            OrderFlowError,
            "Insufficient stock for 'Stock Sensitive Product' to fulfill this order now.",
        ):
            confirm_order_payment(order_id=order.id)

        self.product.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(self.product.stock, 1)
        self.assertEqual(order.status, Order.Status.PENDING)

    def test_out_of_stock_product_cannot_be_purchased(self):
        self.product.stock = 0
        self.product.save(update_fields=["stock"])

        with self.assertRaisesMessage(
            OrderFlowError,
            "'Stock Sensitive Product' is out of stock",
        ):
            self._create_order(quantity=1)

    def test_second_payment_confirmation_fails_after_stock_is_consumed(self):
        self.product.stock = 1
        self.product.save(update_fields=["stock"])
        first_order = self._create_order(quantity=1)
        second_order = self._create_order(quantity=1)

        confirm_order_payment(order_id=first_order.id)

        with self.assertRaisesMessage(
            OrderFlowError,
            "Insufficient stock for 'Stock Sensitive Product' to fulfill this order now.",
        ):
            confirm_order_payment(order_id=second_order.id)

        self.product.refresh_from_db()
        first_order.refresh_from_db()
        second_order.refresh_from_db()
        self.assertEqual(self.product.stock, 0)
        self.assertFalse(self.product.is_active)
        self.assertEqual(first_order.status, Order.Status.PAID)
        self.assertEqual(second_order.status, Order.Status.PENDING)


class DeliveredOrderSellerTransactionTests(TestCase):
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
        self.staff_user = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            is_staff=True,
        )
        self.category, _ = Category.objects.get_or_create(name="Games")
        self.product = Product.objects.create(
            title="Delivered Product",
            description="Product for delivery tests",
            price=Decimal("30.00"),
            stock=2,
            seller=self.seller,
            category=self.category,
        )
        self.order = Order.objects.create(
            buyer=self.buyer,
            total=Decimal("30.00"),
            status=Order.Status.PAID,
            payment_method="manual_bank",
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price_at_purchase=Decimal("30.00"),
            product_title_snapshot=self.product.title,
            product_image_snapshot="",
        )
        self.seller_transaction = SellerTransaction.objects.create(
            seller=self.seller,
            order=self.order,
            amount=Decimal("30.00"),
            status=SellerTransaction.Status.HOLD,
        )
        self.seller.balance_pending = Decimal("30.00")
        self.seller.save(update_fields=["balance_pending"])

    def test_mark_order_delivered_makes_hold_transactions_available(self):
        mark_order_delivered(order_id=self.order.id, current_user=self.seller)

        self.seller_transaction.refresh_from_db()
        self.assertEqual(
            self.seller_transaction.status,
            SellerTransaction.Status.AVAILABLE,
        )

    def test_admin_mark_as_shipped_makes_hold_transactions_available(self):
        order_admin = OrderAdmin(Order, AdminSite())
        order_admin.message_user = lambda *args, **kwargs: None
        request = RequestFactory().post("/admin/orders/order/")
        request.user = self.staff_user

        order_admin.mark_as_shipped(request, Order.objects.filter(id=self.order.id))

        self.seller_transaction.refresh_from_db()
        self.seller.refresh_from_db()
        self.assertEqual(
            self.seller_transaction.status,
            SellerTransaction.Status.AVAILABLE,
        )
        self.assertEqual(self.seller.balance_pending, Decimal("0.00"))
        self.assertEqual(self.seller.balance_available, Decimal("30.00"))


class BuyerCancelPendingOrderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.buyer = User.objects.create_user(
            email="buyer@example.com",
            password="password123",
            is_seller=False,
        )
        self.other_buyer = User.objects.create_user(
            email="other-buyer@example.com",
            password="password123",
            is_seller=False,
        )
        self.seller = User.objects.create_user(
            email="seller@example.com",
            password="password123",
        )
        self.category, _ = Category.objects.get_or_create(name="Games")
        self.product = Product.objects.create(
            title="Pending Order Product",
            description="Product for order cancellation tests",
            price=Decimal("22.00"),
            stock=5,
            seller=self.seller,
            category=self.category,
        )
        self.pending_order = Order.objects.create(
            buyer=self.buyer,
            total=Decimal("22.00"),
            status=Order.Status.PENDING,
            payment_method="manual_bank",
        )
        OrderItem.objects.create(
            order=self.pending_order,
            product=self.product,
            quantity=1,
            price_at_purchase=Decimal("22.00"),
            product_title_snapshot=self.product.title,
            product_image_snapshot="",
        )
        self.paid_order = Order.objects.create(
            buyer=self.buyer,
            total=Decimal("22.00"),
            status=Order.Status.PAID,
            payment_method="manual_bank",
        )
        OrderItem.objects.create(
            order=self.paid_order,
            product=self.product,
            quantity=1,
            price_at_purchase=Decimal("22.00"),
            product_title_snapshot=self.product.title,
            product_image_snapshot="",
        )

    def test_buyer_can_cancel_own_pending_order(self):
        self.client.force_authenticate(user=self.buyer)

        response = self.client.post(f"/orders/{self.pending_order.id}/cancel")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pending_order.refresh_from_db()
        self.assertEqual(self.pending_order.status, Order.Status.CANCELLED)

    def test_buyer_cannot_cancel_non_pending_order(self):
        self.client.force_authenticate(user=self.buyer)

        response = self.client.post(f"/orders/{self.paid_order.id}/cancel")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["detail"],
            "Only pending orders can be cancelled",
        )
        self.paid_order.refresh_from_db()
        self.assertEqual(self.paid_order.status, Order.Status.PAID)

    def test_buyer_cannot_cancel_someone_elses_order(self):
        self.client.force_authenticate(user=self.other_buyer)

        response = self.client.post(f"/orders/{self.pending_order.id}/cancel")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Not your order")
        self.pending_order.refresh_from_db()
        self.assertEqual(self.pending_order.status, Order.Status.PENDING)
