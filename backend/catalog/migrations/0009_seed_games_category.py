from django.db import migrations


def seed_games_category(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Category.objects.update_or_create(name="Games")


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0008_product_product_price_gt_0_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_games_category, migrations.RunPython.noop),
    ]
