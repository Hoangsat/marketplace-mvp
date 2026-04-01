from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0013_category_slug_required"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Game",
            new_name="Platform",
        ),
        migrations.AlterModelTable(
            name="platform",
            table="games",
        ),
        migrations.AddField(
            model_name="platform",
            name="category",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="platforms",
                to="catalog.category",
            ),
        ),
        migrations.RenameField(
            model_name="product",
            old_name="game",
            new_name="platform",
        ),
        migrations.AddField(
            model_name="offertype",
            name="platform",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="offer_types",
                to="catalog.platform",
            ),
        ),
        migrations.AlterField(
            model_name="offertype",
            name="slug",
            field=models.SlugField(),
        ),
        migrations.AddConstraint(
            model_name="offertype",
            constraint=models.UniqueConstraint(
                fields=("platform", "slug"),
                name="unique_offer_type_slug_per_platform",
            ),
        ),
    ]
