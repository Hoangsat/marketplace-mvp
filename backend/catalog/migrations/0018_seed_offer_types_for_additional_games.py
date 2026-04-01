from django.db import migrations


TARGET_PLATFORMS = [
    {
        "name": "Free Fire",
        "slug": "free-fire",
        "display_name_vi": "Free Fire",
    },
    {
        "name": "PUBG Mobile",
        "slug": "pubg-mobile",
        "display_name_vi": "PUBG Mobile",
    },
    {
        "name": "Genshin Impact",
        "slug": "genshin-impact",
        "display_name_vi": "Genshin Impact",
    },
]

OFFER_TYPE_SEEDS = [
    {
        "name": "Accounts",
        "slug": "accounts",
        "display_name_vi": "Tai khoan",
    },
    {
        "name": "Boosting",
        "slug": "boosting",
        "display_name_vi": "Cay thue",
    },
    {
        "name": "Coaching",
        "slug": "coaching",
        "display_name_vi": "Huan luyen",
    },
    {
        "name": "Currency",
        "slug": "currency",
        "display_name_vi": "Vang / tien game",
    },
    {
        "name": "Items",
        "slug": "items",
        "display_name_vi": "Vat pham",
    },
    {
        "name": "Skins",
        "slug": "skins",
        "display_name_vi": "Trang phuc",
    },
]


def forwards(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Platform = apps.get_model("catalog", "Platform")
    OfferType = apps.get_model("catalog", "OfferType")

    games_category = Category.objects.filter(slug="games").first()
    if games_category is None:
        games_category = Category.objects.filter(name="Games").first()
    if games_category is None:
        return

    for platform_data in TARGET_PLATFORMS:
        platform, _ = Platform.objects.update_or_create(
            slug=platform_data["slug"],
            defaults={
                "name": platform_data["name"],
                "display_name_vi": platform_data["display_name_vi"],
                "category": games_category,
                "is_active": True,
            },
        )
        for offer_type_data in OFFER_TYPE_SEEDS:
            OfferType.objects.update_or_create(
                platform=platform,
                slug=offer_type_data["slug"],
                defaults={
                    "name": offer_type_data["name"],
                    "display_name_vi": offer_type_data["display_name_vi"],
                    "is_active": True,
                },
            )


def backwards(apps, schema_editor):
    Platform = apps.get_model("catalog", "Platform")
    OfferType = apps.get_model("catalog", "OfferType")

    target_platform_ids = list(
        Platform.objects.filter(
            slug__in=[platform_data["slug"] for platform_data in TARGET_PLATFORMS]
        ).values_list("id", flat=True)
    )
    if not target_platform_ids:
        return

    OfferType.objects.filter(
        platform_id__in=target_platform_ids,
        slug__in=[offer_type_data["slug"] for offer_type_data in OFFER_TYPE_SEEDS],
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0017_seed_additional_games_platforms"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
