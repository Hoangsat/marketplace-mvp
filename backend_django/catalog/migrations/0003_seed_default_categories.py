from django.db import migrations


DEFAULT_CATEGORY_NAMES = [
    "Electronics",
    "Clothing",
    "Home",
    "Books",
    "Beauty",
    "Sports",
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    for name in DEFAULT_CATEGORY_NAMES:
        Category.objects.get_or_create(name=name)


def unseed_categories(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Category.objects.filter(name__in=DEFAULT_CATEGORY_NAMES).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0002_alter_category_id_alter_product_id_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
