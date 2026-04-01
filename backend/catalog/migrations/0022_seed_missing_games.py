from django.db import migrations


def seed_games(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Platform = apps.get_model("catalog", "Platform")
    OfferType = apps.get_model("catalog", "OfferType")

    games_category = Category.objects.filter(slug="games").first()
    if not games_category:
        return

    platforms = [
        ("lien-quan-mobile", "Liên Quân Mobile"),
        ("lien-minh-huyen-thoai", "Liên Minh Huyền Thoại"),
        ("pubg-mobile-vn", "PUBG Mobile VN"),
        ("valorant", "VALORANT"),
        ("fc-online", "FC Online"),
        ("roblox", "Roblox"),
        ("lien-minh-huyen-thoai-toc-chien", "Liên Minh Huyền Thoại: Tốc Chiến"),
    ]

    offer_types = [
        ("accounts", "Accounts"),
        ("top-up", "Top Up"),
        ("boosting", "Boosting"),
        ("coaching", "Coaching"),
        ("items", "Items"),
        ("currency", "Currency"),
    ]

    for slug, name in platforms:
        platform, _ = Platform.objects.get_or_create(
            slug=slug,
            defaults={
                "name": name,
                "category": games_category,
                "is_active": True,
            },
        )

        for ot_slug, ot_name in offer_types:
            OfferType.objects.get_or_create(
                platform=platform,
                slug=ot_slug,
                defaults={
                    "name": ot_name,
                    "is_active": True,
                },
            )


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0021_seed_additional_games_offer_types"),
    ]

    operations = [
        migrations.RunPython(seed_games),
    ]
