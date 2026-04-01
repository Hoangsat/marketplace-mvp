from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User, UserProfile
from catalog.models import (
    Category,
    OfferType,
    Platform,
    Product,
    SearchAlias,
    normalize_search_query,
)
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
        self.games_category = Category.objects.get(slug="games")
        self.ai_tools_category = Category.objects.get(slug="ai-tools")
        self.software_category = Category.objects.get(slug="software")
        self.free_fire = Platform.objects.get(slug="free-fire")
        self.chatgpt = Platform.objects.get(slug="chatgpt")
        self.free_fire_accounts = OfferType.objects.get(
            platform=self.free_fire,
            slug="accounts",
        )
        self.chatgpt_accounts = OfferType.objects.get(
            platform=self.chatgpt,
            slug="accounts",
        )
        self.free_fire_product = Product.objects.create(
            title="Free Fire account",
            description="Ready to use",
            price=Decimal("25.00"),
            stock=2,
            seller=self.seller,
            category=self.games_category,
            platform=self.free_fire,
            offer_type=self.free_fire_accounts,
        )
        Product.objects.create(
            title="ChatGPT account",
            description="Business account",
            price=Decimal("30.00"),
            stock=2,
            seller=self.seller,
            category=self.ai_tools_category,
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
        response = self.client.get("/offer-types", {"platform": "free-fire"})
        legacy_response = self.client.get("/offer-types", {"game": "free-fire"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 6)
        self.assertTrue(
            all(item["platform_id"] == self.free_fire.id for item in response.json())
        )
        self.assertEqual(response.json(), legacy_response.json())

    def test_products_can_be_filtered_by_platform_and_legacy_game_alias(self):
        response = self.client.get("/products", {"platform": "free-fire"})
        legacy_response = self.client.get("/products", {"game": "free-fire"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["id"], self.free_fire_product.id)
        self.assertEqual(response.json(), legacy_response.json())

    def test_create_product_accepts_legacy_game_id_alias(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.post(
            "/products",
            {
                "title": "Free Fire power-leveling",
                "description": "Instant delivery",
                "price": "9.99",
                "stock": 4,
                "game_id": self.free_fire.id,
                "offer_type_id": self.free_fire_accounts.id,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created = Product.objects.get(id=response.json()["id"])
        self.assertEqual(created.platform_id, self.free_fire.id)
        self.assertEqual(created.category_id, self.games_category.id)
        self.assertEqual(created.offer_type_id, self.free_fire_accounts.id)

    def test_category_catalog_endpoints_return_curated_top_level_navigation(self):
        response = self.client.get("/api/catalog/categories/top")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [item["slug"] for item in response.json()],
            [
                "games",
                "ai-tools",
                "software",
                "subscriptions",
                "gift-cards",
                "learning",
                "vpn-security",
            ],
        )

    def test_category_platform_endpoints_return_curated_platform_sets(self):
        games_response = self.client.get("/api/catalog/categories/games/platforms")
        ai_tools_response = self.client.get("/api/catalog/categories/ai-tools/platforms")
        software_response = self.client.get("/api/catalog/categories/software/platforms")
        subscriptions_response = self.client.get(
            "/api/catalog/categories/subscriptions/platforms"
        )
        gift_cards_response = self.client.get(
            "/api/catalog/categories/gift-cards/platforms"
        )

        self.assertEqual(games_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {item["slug"] for item in games_response.json()},
            {
                "black-myth-wukong",
                "elden-ring",
                "grand-theft-auto-v",
                "minecraft",
                "free-fire",
                "pubg-mobile",
                "genshin-impact",
            },
        )
        self.assertNotIn(
            "dota-2",
            {item["slug"] for item in games_response.json()},
        )
        self.assertNotIn(
            "league-of-legends",
            {item["slug"] for item in games_response.json()},
        )
        self.assertNotIn(
            "lineage-2",
            {item["slug"] for item in games_response.json()},
        )
        self.assertNotIn(
            "lien-quan-mobile",
            {item["slug"] for item in games_response.json()},
        )

        self.assertEqual(ai_tools_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {item["slug"] for item in ai_tools_response.json()},
            {"chatgpt", "claude", "cursor", "kling-ai", "suno"},
        )

        self.assertEqual(software_response.status_code, status.HTTP_200_OK)
        software_slugs = {item["slug"] for item in software_response.json()}
        self.assertIn("microsoft-office", software_slugs)
        self.assertNotIn("word", software_slugs)
        self.assertNotIn("excel", software_slugs)
        self.assertNotIn("ms-office-365", software_slugs)

        self.assertEqual(subscriptions_response.status_code, status.HTTP_200_OK)
        subscription_slugs = {item["slug"] for item in subscriptions_response.json()}
        self.assertIn("netflix", subscription_slugs)
        self.assertNotIn("netflix-premium", subscription_slugs)

        self.assertEqual(gift_cards_response.status_code, status.HTTP_200_OK)
        gift_card_slugs = {item["slug"] for item in gift_cards_response.json()}
        self.assertEqual(gift_card_slugs, {"steam"})
        self.assertNotIn("steam-wallet-code", gift_card_slugs)

    def test_legacy_demo_game_platforms_are_moved_out_of_games_category(self):
        legacy_slugs = {"dota-2", "league-of-legends", "lineage-2", "lien-quan-mobile"}

        self.assertFalse(
            Platform.objects.filter(
                category__slug="games",
                slug__in=legacy_slugs,
            ).exists()
        )
        self.assertEqual(
            set(
                Platform.objects.filter(slug__in=legacy_slugs).values_list(
                    "category__slug",
                    flat=True,
                )
            ),
            {"legacy-games"},
        )

    def test_platform_detail_exposes_offer_type_usage(self):
        response = self.client.get("/platforms/chatgpt")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()["has_offer_types"])
        self.assertEqual(
            [item["slug"] for item in response.json()["offer_types"]],
            ["accounts", "subscription"],
        )

    def test_seeded_games_expose_same_offer_type_hierarchy(self):
        expected_offer_type_slugs = [
            "accounts",
            "boosting",
            "coaching",
            "currency",
            "items",
            "skins",
        ]

        for platform_slug in ("free-fire", "pubg-mobile", "genshin-impact"):
            response = self.client.get(f"/platforms/{platform_slug}")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.json()["has_offer_types"])
            self.assertEqual(
                [item["slug"] for item in response.json()["offer_types"]],
                expected_offer_type_slugs,
            )

    def test_create_product_without_offer_type_is_rejected_when_platform_uses_offer_types(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.post(
            "/products",
            {
                "title": "Free Fire direct listing",
                "description": "Should fail",
                "price": "11.00",
                "stock": 1,
                "platform_id": self.free_fire.id,
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
                "offer_type_id": self.free_fire_accounts.id,
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
            f"/products/{self.free_fire_product.id}",
            {
                "platform_id": telegram.id,
                "offer_type_id": None,
                "title": self.free_fire_product.title,
                "description": self.free_fire_product.description,
                "price": str(self.free_fire_product.price),
                "stock": self.free_fire_product.stock,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.free_fire_product.refresh_from_db()
        self.assertEqual(self.free_fire_product.platform_id, telegram.id)
        self.assertIsNone(self.free_fire_product.offer_type_id)

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
            f"/products/{self.free_fire_product.id}",
            {
                "title": "Updated Free Fire account",
                "description": self.free_fire_product.description,
                "price": str(self.free_fire_product.price),
                "stock": self.free_fire_product.stock,
                "platform_id": self.free_fire.id,
                "offer_type_id": self.free_fire_accounts.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.free_fire_product.refresh_from_db()
        self.assertEqual(self.free_fire_product.title, "Updated Free Fire account")
        self.assertEqual(self.free_fire_product.platform_id, self.free_fire.id)
        self.assertEqual(self.free_fire_product.offer_type_id, self.free_fire_accounts.id)

    def test_update_with_offer_type_without_matching_platform_fails(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.put(
            f"/products/{self.free_fire_product.id}",
            {
                "title": self.free_fire_product.title,
                "description": self.free_fire_product.description,
                "price": str(self.free_fire_product.price),
                "stock": self.free_fire_product.stock,
                "platform_id": self.free_fire.id,
                "offer_type_id": self.chatgpt_accounts.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["detail"], "Offer type not found")


class SearchApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.seller = User.objects.create_user(
            email="search-seller@example.com",
            password="password123",
        )
        self.category = Category.objects.create(
            name="Zen Tools",
            slug="zen-tools",
        )
        self.platform = Platform.objects.create(
            name="Zen Chat",
            slug="zen-chat",
            display_name_vi="Zen Chat",
            category=self.category,
        )
        self.offer_type = OfferType.objects.create(
            platform=self.platform,
            name="Zen Plus",
            slug="zen-plus",
            display_name_vi="Zen Plus",
        )
        self.title_match_product = Product.objects.create(
            title="Zen bundle access",
            description="Direct title match",
            price=Decimal("15.00"),
            stock=3,
            seller=self.seller,
            category=self.category,
            platform=self.platform,
            offer_type=self.offer_type,
        )
        self.category_match_product = Product.objects.create(
            title="Utility membership",
            description="Matches through category only",
            price=Decimal("14.00"),
            stock=2,
            seller=self.seller,
            category=self.category,
        )
        self.out_of_stock_product = Product.objects.create(
            title="Zen sold out",
            description="Out of stock",
            price=Decimal("16.00"),
            stock=0,
            seller=self.seller,
            category=self.category,
        )
        self.inactive_product = Product.objects.create(
            title="Zen inactive",
            description="Inactive product",
            price=Decimal("17.00"),
            stock=2,
            is_active=False,
            seller=self.seller,
            category=self.category,
        )
        self.hidden_platform = Platform.objects.create(
            name="Zen Hidden",
            slug="zen-hidden",
            category=self.category,
            is_active=False,
        )
        self.hidden_platform_product = Product.objects.create(
            title="Zen hidden product",
            description="Hidden by inactive platform",
            price=Decimal("18.00"),
            stock=2,
            seller=self.seller,
            category=self.category,
            platform=self.hidden_platform,
        )
        self.direct_entity_alias = SearchAlias.objects.create(
            query="zen chat official",
            entity_type=SearchAlias.EntityType.GAME,
            entity_id=self.platform.id,
            weight=25,
        )
        self.search_term_alias = SearchAlias.objects.create(
            query="zen chat premium",
            entity_type=SearchAlias.EntityType.SEARCH_TERM,
            weight=40,
        )
        self.inactive_alias = SearchAlias.objects.create(
            query="zen hidden secret",
            entity_type=SearchAlias.EntityType.SEARCH_TERM,
            weight=99,
            is_active=False,
        )
        self.games_category = Category.objects.get(slug="games")
        self.free_fire_platform = Platform.objects.get(slug="free-fire")

    def test_normalize_search_query_trims_lowercases_and_collapses_spaces(self):
        self.assertEqual(normalize_search_query("  Zen   CHAT  Plus "), "zen chat plus")
        self.assertEqual(normalize_search_query(""), "")

    def test_search_suggest_returns_empty_groups_for_short_queries(self):
        response = self.client.get("/api/search/suggest", {"q": "z"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {"query": "z", "categories": [], "search_terms": []},
        )

    def test_search_suggest_returns_direct_matches_and_search_terms(self):
        response = self.client.get("/api/search/suggest", {"q": "zen"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.json()
        category_types = {item["type"] for item in payload["categories"]}
        self.assertIn("category", category_types)
        self.assertIn("game", category_types)
        self.assertIn("offer_type", category_types)
        self.assertTrue(
            any(item["query"] == "zen chat premium" for item in payload["search_terms"])
        )

    def test_search_suggest_returns_games_category_for_game_query(self):
        response = self.client.get("/api/search/suggest", {"q": "game"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            any(
                item["type"] == "category"
                and item["id"] == self.games_category.id
                and item["slug"] == "games"
                and item["url"] == "/categories/games"
                for item in response.json()["categories"]
            )
        )

    def test_search_suggest_returns_free_fire_platform_for_free_query(self):
        response = self.client.get("/api/search/suggest", {"q": "free"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            any(
                item["type"] == "game"
                and item["id"] == self.free_fire_platform.id
                and item["slug"] == "free-fire"
                and item["url"] == "/catalog/free-fire"
                for item in response.json()["categories"]
            )
        )

    def test_search_suggest_returns_free_fire_platform_for_full_query(self):
        response = self.client.get("/api/search/suggest", {"q": "free fire"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            any(
                item["type"] == "game"
                and item["id"] == self.free_fire_platform.id
                and item["slug"] == "free-fire"
                and item["url"] == "/catalog/free-fire"
                for item in response.json()["categories"]
            )
        )

    def test_search_suggest_keeps_direct_matches_when_alias_lookup_fails(self):
        with patch.object(SearchAlias.objects, "filter", side_effect=RuntimeError("alias boom")):
            response = self.client.get("/api/search/suggest", {"q": "free"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            any(
                item["type"] == "game"
                and item["id"] == self.free_fire_platform.id
                and item["slug"] == "free-fire"
                for item in response.json()["categories"]
            )
        )

    def test_search_suggest_deduplicates_alias_backed_entities(self):
        response = self.client.get("/api/search/suggest", {"q": "zen chat"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        platform_matches = [
            item
            for item in response.json()["categories"]
            if item["type"] == "game" and item["id"] == self.platform.id
        ]
        self.assertEqual(len(platform_matches), 1)

    def test_search_suggest_excludes_inactive_aliases_and_entities(self):
        response = self.client.get("/api/search/suggest", {"q": "hidden"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payload = response.json()
        self.assertEqual(payload["categories"], [])
        self.assertEqual(payload["search_terms"], [])

    def test_search_suggest_returns_safe_empty_response_on_unexpected_error(self):
        with patch("catalog.views._category_queryset", side_effect=RuntimeError("boom")):
            response = self.client.get("/api/search/suggest", {"q": "zen"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {"query": "zen", "categories": [], "search_terms": []},
        )

    def test_full_search_returns_only_public_active_buyable_products(self):
        response = self.client.get("/api/search", {"q": "zen"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result_ids = [item["id"] for item in response.json()["results"]]
        self.assertIn(self.title_match_product.id, result_ids)
        self.assertIn(self.category_match_product.id, result_ids)
        self.assertNotIn(self.out_of_stock_product.id, result_ids)
        self.assertNotIn(self.inactive_product.id, result_ids)
        self.assertNotIn(self.hidden_platform_product.id, result_ids)

    def test_full_search_ranks_title_matches_ahead_of_related_name_matches(self):
        response = self.client.get("/api/search", {"q": "zen"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["results"][0]["id"], self.title_match_product.id)

    def test_full_search_paginates_results(self):
        for index in range(25):
            Product.objects.create(
                title=f"Searchpage item {index}",
                description="Pagination product",
                price=Decimal("10.00"),
                stock=1,
                seller=self.seller,
                category=self.category,
            )

        first_page = self.client.get("/api/search", {"q": "searchpage", "page": 1})
        second_page = self.client.get("/api/search", {"q": "searchpage", "page": 2})

        self.assertEqual(first_page.status_code, status.HTTP_200_OK)
        self.assertEqual(second_page.status_code, status.HTTP_200_OK)
        self.assertEqual(first_page.json()["count"], 25)
        self.assertEqual(first_page.json()["page"], 1)
        self.assertEqual(first_page.json()["page_size"], 24)
        self.assertTrue(first_page.json()["has_more"])
        self.assertEqual(len(first_page.json()["results"]), 24)
        self.assertEqual(second_page.json()["page"], 2)
        self.assertFalse(second_page.json()["has_more"])
        self.assertEqual(len(second_page.json()["results"]), 1)
