from django.db import migrations


GAME_SEEDS = [
    {
        "name": "Lineage 2",
        "slug": "lineage-2",
        "display_name_vi": "Lineage 2",
        "is_active": True,
    },
    {
        "name": "Dota 2",
        "slug": "dota-2",
        "display_name_vi": "Dota 2",
        "is_active": True,
    },
    {
        "name": "League of Legends",
        "slug": "league-of-legends",
        "display_name_vi": "Liên Minh Huyền Thoại",
        "is_active": True,
    },
    {
        "name": "Lien Quan Mobile",
        "slug": "lien-quan-mobile",
        "display_name_vi": "Liên Quân Mobile",
        "is_active": True,
    },
]

OFFER_TYPE_SEEDS = [
    {
        "name": "Accounts",
        "slug": "accounts",
        "display_name_vi": "Tài khoản",
        "is_active": True,
    },
    {
        "name": "Boosting",
        "slug": "boosting",
        "display_name_vi": "Cày thuê",
        "is_active": True,
    },
    {
        "name": "Coaching",
        "slug": "coaching",
        "display_name_vi": "Huấn luyện",
        "is_active": True,
    },
    {
        "name": "Currency",
        "slug": "currency",
        "display_name_vi": "Vàng / tiền game",
        "is_active": True,
    },
    {
        "name": "Items",
        "slug": "items",
        "display_name_vi": "Vật phẩm",
        "is_active": True,
    },
    {
        "name": "Skins",
        "slug": "skins",
        "display_name_vi": "Trang phục",
        "is_active": True,
    },
]


def seed_games_and_offer_types(apps, schema_editor):
    Game = apps.get_model("catalog", "Game")
    OfferType = apps.get_model("catalog", "OfferType")

    for game in GAME_SEEDS:
        Game.objects.update_or_create(
            slug=game["slug"],
            defaults=game,
        )

    for offer_type in OFFER_TYPE_SEEDS:
        OfferType.objects.update_or_create(
            slug=offer_type["slug"],
            defaults=offer_type,
        )


def unseed_games_and_offer_types(apps, schema_editor):
    Game = apps.get_model("catalog", "Game")
    OfferType = apps.get_model("catalog", "OfferType")

    Game.objects.filter(slug__in=[game["slug"] for game in GAME_SEEDS]).delete()
    OfferType.objects.filter(
        slug__in=[offer_type["slug"] for offer_type in OFFER_TYPE_SEEDS]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0005_product_game_product_offer_type"),
    ]

    operations = [
        migrations.RunPython(seed_games_and_offer_types, unseed_games_and_offer_types),
    ]
