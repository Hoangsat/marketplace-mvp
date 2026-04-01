from django.db import migrations


CANONICAL_CATEGORIES = [
    {"name": "Games", "slug": "games"},
    {"name": "AI Tools", "slug": "ai-tools"},
    {"name": "Software", "slug": "software"},
    {"name": "Subscriptions", "slug": "subscriptions"},
    {"name": "Gift Cards", "slug": "gift-cards"},
    {"name": "Learning", "slug": "learning"},
    {"name": "VPN & Security", "slug": "vpn-security"},
]

TOP_LEVEL_REPARENT_MAP = {
    "cards": "gift-cards",
    "software-pc": "software",
    "itunes-app-store": "subscriptions",
    "gaming-accounts": "games",
    "social-networks": "subscriptions",
    "mobile-software": "software",
    "electronics": "software",
    "clothing": "subscriptions",
    "home": "software",
    "books": "learning",
    "beauty": "subscriptions",
    "sports": "games",
}

GAME_OFFER_TYPES = (
    {"name": "Accounts", "slug": "accounts", "display_name_vi": "Tai khoan"},
    {"name": "Boosting", "slug": "boosting", "display_name_vi": "Cay thue"},
    {"name": "Coaching", "slug": "coaching", "display_name_vi": "Huan luyen"},
    {"name": "Currency", "slug": "currency", "display_name_vi": "Vang / tien game"},
    {"name": "Items", "slug": "items", "display_name_vi": "Vat pham"},
    {"name": "Skins", "slug": "skins", "display_name_vi": "Trang phuc"},
)

ACCOUNT_SUBSCRIPTION_OFFER_TYPES = (
    {"name": "Accounts", "slug": "accounts", "display_name_vi": "Tai khoan"},
    {"name": "Subscription", "slug": "subscription", "display_name_vi": "Goi dang ky"},
)

ACCOUNT_SINGLE_SUBSCRIPTION_OFFER_TYPES = (
    {"name": "Account", "slug": "account", "display_name_vi": "Tai khoan"},
    {"name": "Subscription", "slug": "subscription", "display_name_vi": "Goi dang ky"},
)

LICENSE_SUBSCRIPTION_OFFER_TYPES = (
    {"name": "License", "slug": "license", "display_name_vi": "Ban quyen"},
    {"name": "Subscription", "slug": "subscription", "display_name_vi": "Goi dang ky"},
)

GIFT_CARD_OFFER_TYPES = (
    {"name": "Gift Card", "slug": "gift-card", "display_name_vi": "The qua tang"},
)

CURATED_PLATFORM_SEEDS = (
    {
        "category_slug": "games",
        "platforms": (
            {
                "name": "Black Myth: Wukong",
                "slug": "black-myth-wukong",
                "display_name_vi": "Black Myth: Wukong",
                "offer_types": GAME_OFFER_TYPES,
            },
            {
                "name": "Elden Ring",
                "slug": "elden-ring",
                "display_name_vi": "Elden Ring",
                "offer_types": GAME_OFFER_TYPES,
            },
            {
                "name": "Grand Theft Auto V",
                "slug": "grand-theft-auto-v",
                "display_name_vi": "Grand Theft Auto V",
                "offer_types": GAME_OFFER_TYPES,
            },
            {
                "name": "Minecraft",
                "slug": "minecraft",
                "display_name_vi": "Minecraft",
                "offer_types": GAME_OFFER_TYPES,
            },
            {
                "name": "Free Fire",
                "slug": "free-fire",
                "display_name_vi": "Free Fire",
                "offer_types": GAME_OFFER_TYPES,
            },
            {
                "name": "PUBG Mobile",
                "slug": "pubg-mobile",
                "display_name_vi": "PUBG Mobile",
                "offer_types": GAME_OFFER_TYPES,
            },
            {
                "name": "Genshin Impact",
                "slug": "genshin-impact",
                "display_name_vi": "Genshin Impact",
                "offer_types": GAME_OFFER_TYPES,
            },
        ),
    },
    {
        "category_slug": "ai-tools",
        "platforms": (
            {
                "name": "ChatGPT",
                "slug": "chatgpt",
                "display_name_vi": "ChatGPT",
                "offer_types": ACCOUNT_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "Claude",
                "slug": "claude",
                "display_name_vi": "Claude",
                "offer_types": ACCOUNT_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "Cursor",
                "slug": "cursor",
                "display_name_vi": "Cursor",
                "offer_types": ACCOUNT_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "Kling AI",
                "slug": "kling-ai",
                "display_name_vi": "Kling AI",
                "offer_types": ACCOUNT_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "Suno",
                "slug": "suno",
                "display_name_vi": "Suno",
                "offer_types": ACCOUNT_SUBSCRIPTION_OFFER_TYPES,
            },
        ),
    },
    {
        "category_slug": "software",
        "platforms": (
            {
                "name": "Microsoft Office",
                "slug": "microsoft-office",
                "display_name_vi": "Microsoft Office",
                "offer_types": LICENSE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "Microsoft Project",
                "slug": "microsoft-project",
                "display_name_vi": "Microsoft Project",
                "offer_types": LICENSE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "AutoCAD",
                "slug": "autocad",
                "display_name_vi": "AutoCAD",
                "offer_types": LICENSE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "Adobe Creative Cloud",
                "slug": "adobe-creative-cloud",
                "display_name_vi": "Adobe Creative Cloud",
                "offer_types": LICENSE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "JetBrains",
                "slug": "jetbrains",
                "display_name_vi": "JetBrains",
                "offer_types": LICENSE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "Shapr3D",
                "slug": "shapr3d",
                "display_name_vi": "Shapr3D",
                "offer_types": LICENSE_SUBSCRIPTION_OFFER_TYPES,
            },
        ),
    },
    {
        "category_slug": "subscriptions",
        "platforms": (
            {
                "name": "Netflix",
                "slug": "netflix",
                "display_name_vi": "Netflix",
                "offer_types": ACCOUNT_SINGLE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "Spotify",
                "slug": "spotify",
                "display_name_vi": "Spotify",
                "offer_types": ACCOUNT_SINGLE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "YouTube",
                "slug": "youtube",
                "display_name_vi": "YouTube",
                "offer_types": ACCOUNT_SINGLE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "Discord",
                "slug": "discord",
                "display_name_vi": "Discord",
                "offer_types": ACCOUNT_SINGLE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "Dropbox",
                "slug": "dropbox",
                "display_name_vi": "Dropbox",
                "offer_types": ACCOUNT_SINGLE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "Google One",
                "slug": "google-one",
                "display_name_vi": "Google One",
                "offer_types": ACCOUNT_SINGLE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "iCloud",
                "slug": "icloud",
                "display_name_vi": "iCloud",
                "offer_types": ACCOUNT_SINGLE_SUBSCRIPTION_OFFER_TYPES,
            },
        ),
    },
    {
        "category_slug": "gift-cards",
        "platforms": (
            {
                "name": "Steam",
                "slug": "steam",
                "display_name_vi": "Steam",
                "offer_types": GIFT_CARD_OFFER_TYPES,
            },
        ),
    },
    {
        "category_slug": "learning",
        "platforms": (
            {
                "name": "Coursera",
                "slug": "coursera",
                "display_name_vi": "Coursera",
                "offer_types": ACCOUNT_SINGLE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "Duolingo",
                "slug": "duolingo",
                "display_name_vi": "Duolingo",
                "offer_types": ACCOUNT_SINGLE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "Busuu",
                "slug": "busuu",
                "display_name_vi": "Busuu",
                "offer_types": ACCOUNT_SINGLE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "LinkedIn Learning",
                "slug": "linkedin-learning",
                "display_name_vi": "LinkedIn Learning",
                "offer_types": ACCOUNT_SINGLE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "DataCamp",
                "slug": "datacamp",
                "display_name_vi": "DataCamp",
                "offer_types": ACCOUNT_SINGLE_SUBSCRIPTION_OFFER_TYPES,
            },
        ),
    },
    {
        "category_slug": "vpn-security",
        "platforms": (
            {
                "name": "NordVPN",
                "slug": "nordvpn",
                "display_name_vi": "NordVPN",
                "offer_types": LICENSE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "ExpressVPN",
                "slug": "expressvpn",
                "display_name_vi": "ExpressVPN",
                "offer_types": LICENSE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "Avast",
                "slug": "avast",
                "display_name_vi": "Avast",
                "offer_types": LICENSE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "Kaspersky",
                "slug": "kaspersky",
                "display_name_vi": "Kaspersky",
                "offer_types": LICENSE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "1Password",
                "slug": "1password",
                "display_name_vi": "1Password",
                "offer_types": LICENSE_SUBSCRIPTION_OFFER_TYPES,
            },
            {
                "name": "LastPass",
                "slug": "lastpass",
                "display_name_vi": "LastPass",
                "offer_types": LICENSE_SUBSCRIPTION_OFFER_TYPES,
            },
        ),
    },
)

NON_FEATURED_RANK = len(CANONICAL_CATEGORIES) + 100


def _upsert_category(Category, *, name, slug, featured_rank):
    category = Category.objects.filter(slug=slug).first()
    if category is None:
        category = Category.objects.filter(name=name).first()

    if category is None:
        return Category.objects.create(
            name=name,
            slug=slug,
            parent=None,
            is_featured_home=True,
            featured_rank=featured_rank,
        )

    updates = []
    if category.name != name:
        category.name = name
        updates.append("name")
    if category.slug != slug:
        category.slug = slug
        updates.append("slug")
    if category.parent_id is not None:
        category.parent = None
        updates.append("parent")
    if not category.is_featured_home:
        category.is_featured_home = True
        updates.append("is_featured_home")
    if category.featured_rank != featured_rank:
        category.featured_rank = featured_rank
        updates.append("featured_rank")
    if updates:
        category.save(update_fields=updates)
    return category


def _upsert_platform(Platform, *, category, seed):
    platform = Platform.objects.filter(slug=seed["slug"]).first()
    if platform is None:
        platform = Platform.objects.filter(name=seed["name"]).first()

    if platform is None:
        return Platform.objects.create(
            name=seed["name"],
            slug=seed["slug"],
            display_name_vi=seed["display_name_vi"],
            category=category,
            is_active=True,
        )

    updates = []
    if platform.name != seed["name"]:
        platform.name = seed["name"]
        updates.append("name")
    if platform.slug != seed["slug"]:
        platform.slug = seed["slug"]
        updates.append("slug")
    if platform.display_name_vi != seed["display_name_vi"]:
        platform.display_name_vi = seed["display_name_vi"]
        updates.append("display_name_vi")
    if platform.category_id != category.id:
        platform.category = category
        updates.append("category")
    if not platform.is_active:
        platform.is_active = True
        updates.append("is_active")
    if updates:
        platform.save(update_fields=updates)
    return platform


def _upsert_offer_type(OfferType, *, platform, seed):
    offer_type, created = OfferType.objects.get_or_create(
        platform=platform,
        slug=seed["slug"],
        defaults={
            "name": seed["name"],
            "display_name_vi": seed["display_name_vi"],
            "is_active": True,
        },
    )
    if created:
        return offer_type

    updates = []
    if offer_type.name != seed["name"]:
        offer_type.name = seed["name"]
        updates.append("name")
    if offer_type.display_name_vi != seed["display_name_vi"]:
        offer_type.display_name_vi = seed["display_name_vi"]
        updates.append("display_name_vi")
    if not offer_type.is_active:
        offer_type.is_active = True
        updates.append("is_active")
    if updates:
        offer_type.save(update_fields=updates)
    return offer_type


def forwards(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Platform = apps.get_model("catalog", "Platform")
    OfferType = apps.get_model("catalog", "OfferType")
    Product = apps.get_model("catalog", "Product")

    canonical_categories = {}
    for index, category_seed in enumerate(CANONICAL_CATEGORIES, start=1):
        canonical_categories[category_seed["slug"]] = _upsert_category(
            Category,
            name=category_seed["name"],
            slug=category_seed["slug"],
            featured_rank=index,
        )

    canonical_platform_slugs = set()
    canonical_platform_category_ids = {}
    canonical_offer_type_slugs_by_platform = {}

    for category_seed in CURATED_PLATFORM_SEEDS:
        category = canonical_categories[category_seed["category_slug"]]
        for platform_seed in category_seed["platforms"]:
            platform = _upsert_platform(
                Platform,
                category=category,
                seed=platform_seed,
            )
            canonical_platform_slugs.add(platform.slug)
            canonical_platform_category_ids[platform.id] = category.id
            allowed_offer_type_slugs = []
            for offer_type_seed in platform_seed["offer_types"]:
                _upsert_offer_type(
                    OfferType,
                    platform=platform,
                    seed=offer_type_seed,
                )
                allowed_offer_type_slugs.append(offer_type_seed["slug"])
            canonical_offer_type_slugs_by_platform[platform.id] = set(allowed_offer_type_slugs)

    for platform_id, category_id in canonical_platform_category_ids.items():
        Product.objects.filter(platform_id=platform_id).exclude(category_id=category_id).update(
            category_id=category_id
        )

    for platform_id, allowed_offer_type_slugs in canonical_offer_type_slugs_by_platform.items():
        OfferType.objects.filter(platform_id=platform_id).exclude(
            slug__in=allowed_offer_type_slugs
        ).update(is_active=False)

    OfferType.objects.exclude(platform__slug__in=canonical_platform_slugs).update(
        is_active=False
    )
    Platform.objects.exclude(slug__in=canonical_platform_slugs).update(is_active=False)

    canonical_category_slugs = set(canonical_categories.keys())
    for category in Category.objects.exclude(slug__in=canonical_category_slugs).filter(
        parent__isnull=True
    ):
        target_slug = TOP_LEVEL_REPARENT_MAP.get(category.slug, "software")
        target_parent = canonical_categories[target_slug]
        updates = []
        if category.parent_id != target_parent.id:
            category.parent = target_parent
            updates.append("parent")
        if category.is_featured_home:
            category.is_featured_home = False
            updates.append("is_featured_home")
        if category.featured_rank != NON_FEATURED_RANK:
            category.featured_rank = NON_FEATURED_RANK
            updates.append("featured_rank")
        if updates:
            category.save(update_fields=updates)

    Category.objects.exclude(slug__in=canonical_category_slugs).filter(
        is_featured_home=True
    ).update(is_featured_home=False, featured_rank=NON_FEATURED_RANK)


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0018_seed_offer_types_for_additional_games"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
