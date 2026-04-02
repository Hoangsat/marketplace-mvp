from decimal import Decimal

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase
from django.test import TransactionTestCase
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import PayoutRequest, User, UserProfile
from catalog.models import Category, OfferType, Platform, Product


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_normalizes_email_case_and_whitespace(self):
        User.objects.create_user(
            email="test@example.com",
            password="password123",
        )

        response = self.client.post(
            "/auth/login",
            {"username": "  TeSt@example.com  ", "password": "password123"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", response.json())

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
        self.strong_password = "StrongPass!234"

    def test_register_requires_nickname(self):
        response = self.client.post(
            "/auth/register",
            {"email": "missing@example.com", "password": self.strong_password},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "Nickname is required")
        self.assertFalse(User.objects.filter(email="missing@example.com").exists())

    def test_register_rejects_invalid_nickname_characters(self):
        response = self.client.post(
            "/auth/register",
            {
                "email": "invalid@example.com",
                "password": self.strong_password,
                "nickname": "bad name!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["detail"],
            "Nickname may only contain letters, numbers, underscores, hyphens, and dots",
        )
        self.assertFalse(User.objects.filter(email="invalid@example.com").exists())

    def test_register_rejects_duplicate_nickname(self):
        existing_user = User.objects.create_user(
            email="existing@example.com",
            password=self.strong_password,
        )
        UserProfile.objects.create(user=existing_user, nickname="taken_name")

        response = self.client.post(
            "/auth/register",
            {
                "email": "duplicate@example.com",
                "password": self.strong_password,
                "nickname": "taken_name",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "Nickname is already taken")
        self.assertFalse(User.objects.filter(email="duplicate@example.com").exists())

    def test_register_rejects_duplicate_email_when_case_differs(self):
        User.objects.create_user(
            email="test@example.com",
            password=self.strong_password,
        )

        response = self.client.post(
            "/auth/register",
            {
                "email": "TEST@example.com",
                "password": self.strong_password,
                "nickname": "AnotherSeller",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "Email already registered")

    def test_register_normalizes_email_whitespace_and_case(self):
        response = self.client.post(
            "/auth/register",
            {
                "email": "  TEST@example.com  ",
                "password": self.strong_password,
                "nickname": "TrimmedEmailSeller",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="test@example.com")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(response.json()["email"], "test@example.com")

    def test_register_trims_nickname_before_saving_profile(self):
        response = self.client.post(
            "/auth/register",
            {
                "email": "trimmed@example.com",
                "password": self.strong_password,
                "nickname": "  PixelTrader  ",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="trimmed@example.com")
        self.assertEqual(user.profile.nickname, "PixelTrader")

    def test_register_creates_user_profile_with_nickname(self):
        response = self.client.post(
            "/auth/register",
            {
                "email": "profile@example.com",
                "password": self.strong_password,
                "nickname": "Seller.One",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="profile@example.com")
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        self.assertEqual(user.profile.nickname, "Seller.One")

    def test_weak_password_is_rejected_by_backend_validation(self):
        response = self.client.post(
            "/auth/register",
            {
                "email": "weak@example.com",
                "password": "123",
                "nickname": "WeakSeller",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("too short", response.json()["detail"].lower())
        self.assertFalse(User.objects.filter(email="weak@example.com").exists())


class UserEmailCleanupMigrationTests(TransactionTestCase):
    migrate_from = ("accounts", "0005_userprofile")
    migrate_to = ("accounts", "0007_user_email_ci_unique_constraint")

    def setUp(self):
        super().setUp()
        self.executor = MigrationExecutor(connection)
        self.executor.migrate([self.migrate_from])
        old_apps = self.executor.loader.project_state([self.migrate_from]).apps
        self.setUpBeforeMigration(old_apps)
        self.executor = MigrationExecutor(connection)
        self.executor.migrate([self.migrate_to])
        self.apps = self.executor.loader.project_state([self.migrate_to]).apps

    def setUpBeforeMigration(self, apps):
        User = apps.get_model("accounts", "User")
        self.kept_user = User.objects.create(
            email="  Test@Example.com  ",
            password="password123",
        )
        self.duplicate_user = User.objects.create(
            email="test@example.com",
            password="password123",
        )
        self.third_duplicate_user = User.objects.create(
            email="TEST@example.com",
            password="password123",
        )
        self.unique_user = User.objects.create(
            email="Other@example.com ",
            password="password123",
        )

    def test_migration_keeps_lowest_id_and_normalizes_email(self):
        User = self.apps.get_model("accounts", "User")

        users = list(User.objects.order_by("id").values("id", "email"))

        self.assertEqual(len(users), 2)
        self.assertEqual(users[0]["id"], self.kept_user.id)
        self.assertEqual(users[0]["email"], "test@example.com")
        self.assertEqual(users[1]["id"], self.unique_user.id)
        self.assertEqual(users[1]["email"], "other@example.com")

    def test_migration_leaves_no_duplicate_normalized_emails(self):
        User = self.apps.get_model("accounts", "User")

        emails = list(User.objects.order_by("id").values_list("email", flat=True))

        self.assertEqual(emails, ["test@example.com", "other@example.com"])
        self.assertEqual(len(emails), len(set(emails)))


class PublicSellerProfileViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category, _ = Category.objects.get_or_create(name="Games")

    def test_public_seller_profile_returns_404_when_nickname_not_found(self):
        response = self.client.get("/api/sellers/unknown-seller/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Seller not found")

    def test_public_seller_profile_returns_only_public_products(self):
        seller = User.objects.create_user(
            email="seller@example.com",
            password="password123",
        )
        UserProfile.objects.create(user=seller, nickname="market_seller")
        active_platform = Platform.objects.create(
            name="Steam",
            slug="steam-profile-visible",
            category=self.category,
        )
        inactive_platform = Platform.objects.create(
            name="Lineage 2",
            slug="lineage-2-profile-hidden",
            category=self.category,
            is_active=False,
        )
        inactive_offer_type = OfferType.objects.create(
            platform=active_platform,
            name="Accounts",
            slug="accounts-profile-hidden",
            is_active=False,
        )
        Product.objects.create(
            title="Visible Product",
            description="Visible",
            price=Decimal("10.00"),
            stock=3,
            seller=seller,
            category=self.category,
            is_active=True,
        )
        Product.objects.create(
            title="Inactive Platform Product",
            description="Hidden by inactive platform",
            price=Decimal("10.50"),
            stock=3,
            seller=seller,
            category=self.category,
            platform=inactive_platform,
            is_active=True,
        )
        Product.objects.create(
            title="Inactive Offer Type Product",
            description="Hidden by inactive offer type",
            price=Decimal("10.75"),
            stock=3,
            seller=seller,
            category=self.category,
            platform=active_platform,
            offer_type=inactive_offer_type,
            is_active=True,
        )
        Product.objects.create(
            title="Sold Out Product",
            description="Sold out",
            price=Decimal("11.00"),
            stock=0,
            seller=seller,
            category=self.category,
            is_active=True,
        )
        Product.objects.create(
            title="Inactive Product",
            description="Inactive",
            price=Decimal("12.00"),
            stock=3,
            seller=seller,
            category=self.category,
            is_active=False,
        )

        response = self.client.get("/api/sellers/market_seller/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["nickname"], "market_seller")
        self.assertEqual(len(response.json()["products"]), 1)
        self.assertEqual(response.json()["products"][0]["title"], "Visible Product")


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
