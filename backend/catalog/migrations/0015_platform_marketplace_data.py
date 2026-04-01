from django.db import migrations, models
import django.db.models.deletion


def forwards(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Platform = apps.get_model("catalog", "Platform")
    OfferType = apps.get_model("catalog", "OfferType")
    Product = apps.get_model("catalog", "Product")

    games_category = Category.objects.filter(slug="games").first()
    if games_category is None:
        games_category = Category.objects.filter(name="Games").first()

    if games_category is None:
        games_category = Category.objects.create(
            name="Games",
            slug="games",
            is_featured_home=True,
            featured_rank=0,
        )
    else:
        slug_owner = Category.objects.filter(slug="games").exclude(pk=games_category.pk).first()
        updates = []
        if not games_category.slug and slug_owner is None:
            games_category.slug = "games"
            updates.append("slug")
        if not games_category.is_featured_home:
            games_category.is_featured_home = True
            updates.append("is_featured_home")
        if games_category.featured_rank != 0:
            games_category.featured_rank = 0
            updates.append("featured_rank")
        if updates:
            games_category.save(update_fields=updates)

    Platform.objects.filter(category__isnull=True).update(category=games_category)
    for product in Product.objects.filter(
        platform__isnull=False,
        platform__category__isnull=False,
    ).iterator():
        Product.objects.filter(id=product.id).update(category_id=product.platform.category_id)

    legacy_offer_types = list(
        OfferType.objects.filter(platform__isnull=True).order_by("id")
    )
    platform_ids = list(Platform.objects.values_list("id", flat=True))
    offer_type_map = {}

    for legacy_offer_type in legacy_offer_types:
        for platform_id in platform_ids:
            scoped_offer_type, _ = OfferType.objects.update_or_create(
                platform_id=platform_id,
                slug=legacy_offer_type.slug,
                defaults={
                    "name": legacy_offer_type.name,
                    "display_name_vi": legacy_offer_type.display_name_vi,
                    "is_active": legacy_offer_type.is_active,
                },
            )
            offer_type_map[(platform_id, legacy_offer_type.id)] = scoped_offer_type.id

    for product in Product.objects.filter(
        platform__isnull=False,
        offer_type__isnull=False,
    ).iterator():
        scoped_offer_type_id = offer_type_map.get((product.platform_id, product.offer_type_id))
        if scoped_offer_type_id:
            Product.objects.filter(id=product.id).update(offer_type_id=scoped_offer_type_id)

    Product.objects.filter(platform__isnull=True).update(offer_type=None)
    OfferType.objects.filter(platform__isnull=True).delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("catalog", "0014_platform_marketplace_schema"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="platform",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="platforms",
                to="catalog.category",
            ),
        ),
        migrations.AlterField(
            model_name="offertype",
            name="platform",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="offer_types",
                to="catalog.platform",
            ),
        ),
    ]
