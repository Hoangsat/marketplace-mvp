from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0015_platform_marketplace_data"),
    ]

    operations = [
        migrations.CreateModel(
            name="SearchAlias",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("query", models.CharField(max_length=255)),
                ("normalized_query", models.CharField(db_index=True, max_length=255)),
                (
                    "entity_type",
                    models.CharField(
                        choices=[
                            ("category", "Category"),
                            ("game", "Game"),
                            ("offer_type", "Offer Type"),
                            ("search_term", "Search Term"),
                        ],
                        max_length=20,
                    ),
                ),
                ("entity_id", models.IntegerField(blank=True, null=True)),
                ("weight", models.IntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "search_aliases",
                "ordering": ("-weight", "query", "id"),
            },
        ),
        migrations.AddIndex(
            model_name="searchalias",
            index=models.Index(
                fields=["entity_type", "is_active", "-weight"],
                name="search_alia_entity__af47b4_idx",
            ),
        ),
    ]
