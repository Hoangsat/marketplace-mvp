from django.db import migrations


NEW_GAMES = [
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


def forwards(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Platform = apps.get_model("catalog", "Platform")

    games_category = Category.objects.filter(slug="games").first()
    if games_category is None:
        games_category = Category.objects.filter(name="Games").first()
    if games_category is None:
        return

    for platform_data in NEW_GAMES:
        Platform.objects.update_or_create(
            slug=platform_data["slug"],
            defaults={
                "name": platform_data["name"],
                "display_name_vi": platform_data["display_name_vi"],
                "category": games_category,
                "is_active": True,
            },
        )


def backwards(apps, schema_editor):
    Platform = apps.get_model("catalog", "Platform")
    Platform.objects.filter(
        slug__in=[platform_data["slug"] for platform_data in NEW_GAMES]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0016_searchalias"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
