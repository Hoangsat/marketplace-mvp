from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0010_product_is_active"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="featured_rank",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="category",
            name="is_featured_home",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="category",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name="children",
                to="catalog.category",
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="slug",
            field=models.SlugField(blank=True, max_length=100, null=True),
        ),
    ]
