from decimal import Decimal

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import PayoutRequest, User


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_inactive_user_cannot_log_in(self):
        User.objects.create_user(
            email="disabled@example.com",
            password="password123",
            is_active=False,
        )

        response = self.client.post(
            "/auth/login",
            {"username": "disabled@example.com", "password": "password123"},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["detail"], "Incorrect email or password")
        self.assertNotIn("access_token", response.json())


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_weak_password_is_rejected_by_backend_validation(self):
        response = self.client.post(
            "/auth/register",
            {"email": "weak@example.com", "password": "123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("too short", response.json()["detail"].lower())
        self.assertFalse(User.objects.filter(email="weak@example.com").exists())


class PayoutRequestViewTests(TestCase):
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
        self.seller.balance_available = Decimal("100.00")
        self.seller.save(update_fields=["balance_available"])

    def test_seller_can_create_payout_request(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.post(
            "/seller/payout-requests",
            {"amount": "40.00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PayoutRequest.objects.count(), 1)
        payout_request = PayoutRequest.objects.get()
        self.assertEqual(payout_request.seller_id, self.seller.id)
        self.assertEqual(payout_request.amount, Decimal("40.00"))
        self.assertEqual(payout_request.status, PayoutRequest.Status.PENDING)
        self.seller.refresh_from_db()
        self.assertEqual(self.seller.balance_available, Decimal("60.00"))

    def test_payout_request_amount_must_be_greater_than_zero(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.post(
            "/seller/payout-requests",
            {"amount": "0.00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "Amount must be greater than 0")
        self.assertEqual(PayoutRequest.objects.count(), 0)
        self.seller.refresh_from_db()
        self.assertEqual(self.seller.balance_available, Decimal("100.00"))

    def test_payout_request_amount_cannot_exceed_available_balance(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.post(
            "/seller/payout-requests",
            {"amount": "150.00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "Insufficient available balance")
        self.assertEqual(PayoutRequest.objects.count(), 0)
        self.seller.refresh_from_db()
        self.assertEqual(self.seller.balance_available, Decimal("100.00"))

    def test_non_seller_cannot_create_payout_request(self):
        self.client.force_authenticate(user=self.buyer)

        response = self.client.post(
            "/seller/payout-requests",
            {"amount": "10.00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "Seller account required")
        self.assertEqual(PayoutRequest.objects.count(), 0)

    def test_unauthenticated_user_cannot_create_payout_request(self):
        response = self.client.post(
            "/seller/payout-requests",
            {"amount": "10.00"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(PayoutRequest.objects.count(), 0)
