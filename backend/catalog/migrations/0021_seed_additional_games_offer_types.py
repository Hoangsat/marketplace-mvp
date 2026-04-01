from django.db import migrations


GAME_SEEDS = [
    {
        "name": "Liên Quân Mobile",
        "slug": "lien-quan-mobile",
        "display_name_vi": "Liên Quân Mobile",
    },
    {
        "name": "Liên Minh Huyền Thoại",
        "slug": "lien-minh-huyen-thoai",
        "display_name_vi": "Liên Minh Huyền Thoại",
    },
    {
        "name": "PUBG Mobile VN",
        "slug": "pubg-mobile-vn",
        "display_name_vi": "PUBG Mobile VN",
    },
    {
        "name": "VALORANT",
        "slug": "valorant",
        "display_name_vi": "VALORANT",
    },
    {
        "name": "FC Online",
        "slug": "fc-online",
        "display_name_vi": "FC Online",
    },
    {
        "name": "Roblox",
        "slug": "roblox",
        "display_name_vi": "Roblox",
    },
    {
        "name": "Liên Minh Huyền Thoại: Tốc Chiến",
        "slug": "lien-minh-huyen-thoai-toc-chien",
        "display_name_vi": "Liên Minh Huyền Thoại: Tốc Chiến",
    },
    {
        "name": "Free Fire",
        "slug": "free-fire",
        "display_name_vi": "Free Fire",
    },
    {
        "name": "Genshin Impact",
        "slug": "genshin-impact",
        "display_name_vi": "Genshin Impact",
    },
    {
        "name": "Minecraft",
        "slug": "minecraft",
        "display_name_vi": "Minecraft",
    },
]

OFFER_TYPE_SEEDS = [
    {
        "name": "Accounts",
        "slug": "accounts",
        "display_name_vi": "Accounts",
    },
    {
        "name": "Top Up",
        "slug": "top-up",
        "display_name_vi": "Top Up",
    },
    {
        "name": "Boosting",
        "slug": "boosting",
        "display_name_vi": "Boosting",
    },
    {
        "name": "Coaching",
        "slug": "coaching",
        "display_name_vi": "Coaching",
    },
    {
        "name": "Items",
        "slug": "items",
        "display_name_vi": "Items",
    },
    {
        "name": "Currency",
        "slug": "currency",
        "display_name_vi": "Currency",
    },
]


def forwards(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Platform = apps.get_model("catalog", "Platform")
    OfferType = apps.get_model("catalog", "OfferType")

    games_category = Category.objects.filter(slug="games").first()
    if games_category is None:
        return

    for game_seed in GAME_SEEDS:
        platform, _ = Platform.objects.get_or_create(
            slug=game_seed["slug"],
            defaults={
                "name": game_seed["name"],
                "display_name_vi": game_seed["display_name_vi"],
                "category": games_category,
                "is_active": True,
            },
        )

        platform_updates = []
        if platform.name != game_seed["name"]:
            platform.name = game_seed["name"]
            platform_updates.append("name")
        if platform.display_name_vi != game_seed["display_name_vi"]:
            platform.display_name_vi = game_seed["display_name_vi"]
            platform_updates.append("display_name_vi")
        if platform.category_id != games_category.id:
            platform.category = games_category
            platform_updates.append("category")
        if not platform.is_active:
            platform.is_active = True
            platform_updates.append("is_active")
        if platform_updates:
            platform.save(update_fields=platform_updates)

        for offer_type_seed in OFFER_TYPE_SEEDS:
            offer_type, _ = OfferType.objects.get_or_create(
                platform=platform,
                slug=offer_type_seed["slug"],
                defaults={
                    "name": offer_type_seed["name"],
                    "display_name_vi": offer_type_seed["display_name_vi"],
                    "is_active": True,
                },
            )

            offer_type_updates = []
            if offer_type.name != offer_type_seed["name"]:
                offer_type.name = offer_type_seed["name"]
                offer_type_updates.append("name")
            if offer_type.display_name_vi != offer_type_seed["display_name_vi"]:
                offer_type.display_name_vi = offer_type_seed["display_name_vi"]
                offer_type_updates.append("display_name_vi")
            if not offer_type.is_active:
                offer_type.is_active = True
                offer_type_updates.append("is_active")
            if offer_type_updates:
                offer_type.save(update_fields=offer_type_updates)


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0020_move_legacy_game_platforms_out_of_games"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
