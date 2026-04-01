from django.db import migrations


CANONICAL_GAME_SLUGS = {
    "black-myth-wukong",
    "elden-ring",
    "grand-theft-auto-v",
    "minecraft",
    "free-fire",
    "pubg-mobile",
    "genshin-impact",
}


def forwards(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Platform = apps.get_model("catalog", "Platform")
    OfferType = apps.get_model("catalog", "OfferType")
    Product = apps.get_model("catalog", "Product")

    games_category = Category.objects.filter(slug="games").first()
    if games_category is None:
        return

    legacy_games_category, _ = Category.objects.get_or_create(
        slug="legacy-games",
        defaults={
            "name": "Legacy Games",
            "parent": games_category,
            "is_featured_home": False,
            "featured_rank": 999,
        },
    )

    legacy_platforms = Platform.objects.filter(category=games_category).exclude(
        slug__in=CANONICAL_GAME_SLUGS
    )

    legacy_platform_ids = list(legacy_platforms.values_list("id", flat=True))
    if not legacy_platform_ids:
        return

    legacy_platforms.update(category=legacy_games_category, is_active=False)
    OfferType.objects.filter(platform_id__in=legacy_platform_ids).update(is_active=False)
    Product.objects.filter(platform_id__in=legacy_platform_ids).update(
        category=legacy_games_category
    )


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0019_curated_catalog_normalization"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
