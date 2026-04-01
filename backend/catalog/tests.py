from decimal import Decimal

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User, UserProfile
from catalog.models import Category, OfferType, Platform, Product
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

    def test_seller_product_list_excludes_soft_deleted_products_after_refresh(self):
        self.client.delete(f"/products/{self.sold_product.id}")

        response = self.client.get("/seller/products")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product_ids = [product["id"] for product in response.json()]
        self.assertNotIn(self.sold_product.id, product_ids)
        self.assertIn(self.unsold_product.id, product_ids)


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


class ProductSerializerNicknameTests(TestCase):
    def setUp(self):
        self.category, _ = Category.objects.get_or_create(name="Games")

    def test_product_serializer_uses_profile_nickname_when_present(self):
        seller = User.objects.create_user(
            email="seller@example.com",
            password="password123",
        )
        UserProfile.objects.create(user=seller, nickname="PixelTrader")
        product = Product.objects.create(
            title="Nickname Product",
            description="Uses seller nickname",
            price=Decimal("20.00"),
            stock=1,
            seller=seller,
            category=self.category,
        )

        serialized = ProductSerializer(product).data

        self.assertEqual(serialized["seller_nickname"], "PixelTrader")

    def test_product_serializer_falls_back_to_seller_when_profile_missing(self):
        seller = User.objects.create_user(
            email="seller@example.com",
            password="password123",
        )
        product = Product.objects.create(
            title="No Profile Product",
            description="No profile exists",
            price=Decimal("20.00"),
            stock=1,
            seller=seller,
            category=self.category,
        )

        serialized = ProductSerializer(product).data

        self.assertEqual(serialized["seller_nickname"], "Seller")

    def test_product_serializer_falls_back_to_seller_when_nickname_is_blank(self):
        seller = User.objects.create_user(
            email="seller@example.com",
            password="password123",
        )
        UserProfile.objects.create(user=seller, nickname="")
        product = Product.objects.create(
            title="Blank Nickname Product",
            description="Blank nickname",
            price=Decimal("20.00"),
            stock=1,
            seller=seller,
            category=self.category,
        )

        serialized = ProductSerializer(product).data

        self.assertEqual(serialized["seller_nickname"], "Seller")


class PublicCatalogVisibilityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.seller = User.objects.create_user(
            email="seller@example.com",
            password="password123",
        )
        self.category, _ = Category.objects.get_or_create(name="Games")
        self.active_platform = Platform.objects.create(
            name="Steam",
            slug="steam-public-visibility",
            category=self.category,
        )
        self.inactive_platform = Platform.objects.create(
            name="Lineage 2",
            slug="lineage-2-hidden",
            category=self.category,
            is_active=False,
        )
        self.inactive_offer_type = OfferType.objects.create(
            platform=self.active_platform,
            name="Accounts",
            slug="accounts-hidden",
            is_active=False,
        )
        self.visible_product = Product.objects.create(
            title="Visible Product",
            description="In stock and active",
            price=Decimal("15.00"),
            stock=2,
            seller=self.seller,
            category=self.category,
        )
        Product.objects.create(
            title="Inactive Platform Product",
            description="Platform is inactive",
            price=Decimal("16.00"),
            stock=2,
            seller=self.seller,
            category=self.category,
            platform=self.inactive_platform,
        )
        Product.objects.create(
            title="Inactive Offer Type Product",
            description="Offer type is inactive",
            price=Decimal("17.00"),
            stock=2,
            seller=self.seller,
            category=self.category,
            platform=self.active_platform,
            offer_type=self.inactive_offer_type,
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
        self.assertEqual(response.data[0]["seller_nickname"], "Seller")

    def test_category_products_endpoint_hides_products_under_inactive_nodes(self):
        response = self.client.get(f"/api/catalog/categories/{self.category.slug}/products")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([product["id"] for product in response.data], [self.visible_product.id])

    def test_public_product_detail_hides_inactive_product(self):
        inactive_product = Product.objects.filter(title="Inactive Product").get()

        response = self.client.get(f"/products/{inactive_product.id}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Product not found")

    def test_public_product_detail_hides_product_under_inactive_platform(self):
        product = Product.objects.get(title="Inactive Platform Product")

        response = self.client.get(f"/products/{product.id}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Product not found")

    def test_public_product_detail_hides_product_under_inactive_offer_type(self):
        product = Product.objects.get(title="Inactive Offer Type Product")

        response = self.client.get(f"/products/{product.id}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Product not found")

    def test_seller_can_still_view_own_inactive_product_detail(self):
        inactive_product = Product.objects.filter(title="Inactive Product").get()
        self.client.force_authenticate(user=self.seller)

        response = self.client.get(f"/products/{inactive_product.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], inactive_product.id)


class PlatformCatalogApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.seller = User.objects.create_user(
            email="seller@example.com",
            password="password123",
        )
        self.games_category, _ = Category.objects.get_or_create(
            name="Games",
            defaults={
                "slug": "games",
                "is_featured_home": True,
                "featured_rank": 1,
            },
        )
        self.software_category = Category.objects.create(
            name="Software",
            slug="software",
            is_featured_home=True,
            featured_rank=2,
        )
        self.steam = Platform.objects.create(
            name="Steam",
            slug="steam",
            display_name_vi="Steam",
            category=self.games_category,
        )
        self.chatgpt = Platform.objects.create(
            name="ChatGPT",
            slug="chatgpt",
            display_name_vi="ChatGPT",
            category=self.software_category,
        )
        self.steam_accounts = OfferType.objects.create(
            platform=self.steam,
            name="Accounts",
            slug="accounts",
            display_name_vi="Tai khoan",
        )
        self.chatgpt_accounts = OfferType.objects.create(
            platform=self.chatgpt,
            name="Accounts",
            slug="accounts",
            display_name_vi="Tai khoan",
        )
        self.steam_product = Product.objects.create(
            title="Steam account",
            description="Ready to use",
            price=Decimal("25.00"),
            stock=2,
            seller=self.seller,
            category=self.games_category,
            platform=self.steam,
            offer_type=self.steam_accounts,
        )
        Product.objects.create(
            title="ChatGPT account",
            description="Business account",
            price=Decimal("30.00"),
            stock=2,
            seller=self.seller,
            category=self.software_category,
            platform=self.chatgpt,
            offer_type=self.chatgpt_accounts,
        )

    def test_platform_alias_endpoints_return_platforms(self):
        response = self.client.get("/platforms")
        legacy_response = self.client.get("/games")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(legacy_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["slug"] for item in response.json()],
            [item["slug"] for item in legacy_response.json()],
        )

    def test_offer_types_can_be_filtered_by_platform_alias(self):
        response = self.client.get("/offer-types", {"platform": "steam"})
        legacy_response = self.client.get("/offer-types", {"game": "steam"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["platform_id"], self.steam.id)
        self.assertEqual(response.json(), legacy_response.json())

    def test_products_can_be_filtered_by_platform_and_legacy_game_alias(self):
        response = self.client.get("/products", {"platform": "steam"})
        legacy_response = self.client.get("/products", {"game": "steam"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], self.steam_product.id)
        self.assertEqual(response.json(), legacy_response.json())

    def test_create_product_accepts_legacy_game_id_alias(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.post(
            "/products",
            {
                "title": "Steam wallet top-up",
                "description": "Instant delivery",
                "price": "9.99",
                "stock": 4,
                "game_id": self.steam.id,
                "offer_type_id": self.steam_accounts.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Product.objects.get(id=response.json()["id"])
        self.assertEqual(created.platform_id, self.steam.id)
        self.assertEqual(created.category_id, self.games_category.id)
        self.assertEqual(created.offer_type_id, self.steam_accounts.id)

    def test_category_catalog_endpoints_return_top_level_navigation(self):
        response = self.client.get("/api/catalog/categories/top")
        platform_response = self.client.get("/api/catalog/categories/games/platforms")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(platform_response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()[0]["slug"], "games")
        self.assertEqual(platform_response.json()[0]["slug"], "steam")

    def test_platform_detail_exposes_offer_type_usage(self):
        response = self.client.get("/platforms/steam")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["has_offer_types"])
        self.assertEqual(response.json()["offer_types"][0]["slug"], "accounts")

    def test_create_product_without_offer_type_is_rejected_when_platform_uses_offer_types(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.post(
            "/products",
            {
                "title": "Steam direct listing",
                "description": "Should fail",
                "price": "11.00",
                "stock": 1,
                "platform_id": self.steam.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json()["detail"],
            "Offer type is required for this platform",
        )

    def test_create_product_without_offer_type_is_allowed_when_platform_has_no_offer_types(self):
        self.client.force_authenticate(user=self.seller)
        telegram = Platform.objects.create(
            name="Telegram",
            slug="telegram",
            display_name_vi="Telegram",
            category=self.software_category,
        )

        response = self.client.post(
            "/products",
            {
                "title": "Telegram account",
                "description": "Direct platform listing",
                "price": "19.00",
                "stock": 2,
                "platform_id": telegram.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Product.objects.get(id=response.json()["id"])
        self.assertEqual(created.platform_id, telegram.id)
        self.assertIsNone(created.offer_type_id)

    def test_create_product_with_category_only_is_allowed_for_terminal_category(self):
        self.client.force_authenticate(user=self.seller)
        terminal_category = Category.objects.create(
            name="Terminal Services",
            slug="terminal-services",
        )

        response = self.client.post(
            "/products",
            {
                "title": "Premium app subscription",
                "description": "Category-only listing",
                "price": "8.00",
                "stock": 3,
                "category_id": terminal_category.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Product.objects.get(id=response.json()["id"])
        self.assertEqual(created.category_id, terminal_category.id)
        self.assertIsNone(created.platform_id)
        self.assertIsNone(created.offer_type_id)

    def test_create_product_with_category_only_fails_when_category_has_platforms(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.post(
            "/products",
            {
                "title": "Games listing without platform",
                "description": "Should fail",
                "price": "7.00",
                "stock": 2,
                "category_id": self.games_category.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "Platform is required")

    def test_create_product_with_platform_still_works(self):
        self.client.force_authenticate(user=self.seller)
        telegram = Platform.objects.create(
            name="Telegram Direct",
            slug="telegram-direct",
            display_name_vi="Telegram",
            category=self.software_category,
        )

        response = self.client.post(
            "/products",
            {
                "title": "Telegram direct listing",
                "description": "Platform-based listing",
                "price": "17.00",
                "stock": 2,
                "platform_id": telegram.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Product.objects.get(id=response.json()["id"])
        self.assertEqual(created.platform_id, telegram.id)
        self.assertEqual(created.category_id, self.software_category.id)
        self.assertIsNone(created.offer_type_id)

    def test_create_product_with_offer_type_but_no_platform_fails(self):
        self.client.force_authenticate(user=self.seller)
        terminal_category = Category.objects.create(
            name="Terminal Services 2",
            slug="terminal-services-2",
        )

        response = self.client.post(
            "/products",
            {
                "title": "Broken category listing",
                "description": "Offer type without platform",
                "price": "9.00",
                "stock": 1,
                "category_id": terminal_category.id,
                "offer_type_id": self.steam_accounts.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "Platform is required")

    def test_update_product_can_clear_offer_type_when_platform_has_no_offer_types(self):
        self.client.force_authenticate(user=self.seller)
        telegram = Platform.objects.create(
            name="Telegram",
            slug="telegram-2",
            display_name_vi="Telegram",
            category=self.software_category,
        )

        response = self.client.put(
            f"/products/{self.steam_product.id}",
            {
                "platform_id": telegram.id,
                "offer_type_id": None,
                "title": self.steam_product.title,
                "description": self.steam_product.description,
                "price": str(self.steam_product.price),
                "stock": self.steam_product.stock,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.steam_product.refresh_from_db()
        self.assertEqual(self.steam_product.platform_id, telegram.id)
        self.assertIsNone(self.steam_product.offer_type_id)

    def test_update_category_only_product_in_terminal_category_succeeds_without_platform(self):
        self.client.force_authenticate(user=self.seller)
        terminal_category = Category.objects.create(
            name="Terminal Updates",
            slug="terminal-updates",
        )
        category_only_product = Product.objects.create(
            title="Category-only product",
            description="No platform needed",
            price=Decimal("12.00"),
            stock=2,
            seller=self.seller,
            category=terminal_category,
        )

        response = self.client.put(
            f"/products/{category_only_product.id}",
            {
                "title": "Updated category-only product",
                "description": category_only_product.description,
                "price": str(category_only_product.price),
                "stock": category_only_product.stock,
                "category_id": terminal_category.id,
                "platform_id": None,
                "offer_type_id": None,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category_only_product.refresh_from_db()
        self.assertEqual(category_only_product.title, "Updated category-only product")
        self.assertEqual(category_only_product.category_id, terminal_category.id)
        self.assertIsNone(category_only_product.platform_id)
        self.assertIsNone(category_only_product.offer_type_id)

    def test_update_product_to_category_with_active_platforms_and_no_platform_fails(self):
        self.client.force_authenticate(user=self.seller)
        terminal_category = Category.objects.create(
            name="Terminal Reassignment",
            slug="terminal-reassignment",
        )
        category_only_product = Product.objects.create(
            title="Terminal listing",
            description="Starts category only",
            price=Decimal("14.00"),
            stock=2,
            seller=self.seller,
            category=terminal_category,
        )

        response = self.client.put(
            f"/products/{category_only_product.id}",
            {
                "title": category_only_product.title,
                "description": category_only_product.description,
                "price": str(category_only_product.price),
                "stock": category_only_product.stock,
                "category_id": self.games_category.id,
                "platform_id": None,
                "offer_type_id": None,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "Platform is required")

    def test_update_platform_based_product_still_works(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.put(
            f"/products/{self.steam_product.id}",
            {
                "title": "Updated Steam account",
                "description": self.steam_product.description,
                "price": str(self.steam_product.price),
                "stock": self.steam_product.stock,
                "platform_id": self.steam.id,
                "offer_type_id": self.steam_accounts.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.steam_product.refresh_from_db()
        self.assertEqual(self.steam_product.title, "Updated Steam account")
        self.assertEqual(self.steam_product.platform_id, self.steam.id)
        self.assertEqual(self.steam_product.offer_type_id, self.steam_accounts.id)

    def test_update_with_offer_type_without_matching_platform_fails(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.put(
            f"/products/{self.steam_product.id}",
            {
                "title": self.steam_product.title,
                "description": self.steam_product.description,
                "price": str(self.steam_product.price),
                "stock": self.steam_product.stock,
                "platform_id": self.steam.id,
                "offer_type_id": self.chatgpt_accounts.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Offer type not found")
