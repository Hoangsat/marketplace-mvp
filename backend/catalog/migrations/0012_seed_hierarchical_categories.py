from django.db import migrations
from django.utils.text import slugify


TOP_CATEGORIES = [
    ("Games", "games"),
    ("Cards", "cards"),
    ("Software for PC", "software-pc"),
    ("iTunes & App Store", "itunes-app-store"),
    ("Gaming accounts", "gaming-accounts"),
    ("Social networks", "social-networks"),
    ("Mobile software", "mobile-software"),
]

CHILD_CATEGORIES = [
    ("Lineage 2", "lineage-2", "games"),
    ("Dota 2", "dota-2", "games"),
    ("CS2", "cs2", "games"),
    ("WoW", "wow", "games"),
    ("Steam", "steam", "cards"),
    ("PlayStation", "playstation", "cards"),
    ("Xbox", "xbox", "cards"),
    ("Windows", "windows", "software-pc"),
    ("Microsoft Office", "microsoft-office", "software-pc"),
    ("App Store", "app-store", "itunes-app-store"),
    ("iTunes", "itunes", "itunes-app-store"),
    ("Fortnite", "fortnite", "gaming-accounts"),
    ("Valorant", "valorant", "gaming-accounts"),
    ("Telegram", "telegram", "social-networks"),
    ("Instagram", "instagram", "social-networks"),
    ("Spotify", "spotify", "mobile-software"),
]

FEATURED_SLUGS = [
    "games",
    "cards",
    "software-pc",
    "itunes-app-store",
    "gaming-accounts",
    "social-networks",
    "mobile-software",
    "lineage-2",
    "dota-2",
    "cs2",
    "wow",
    "steam",
    "playstation",
    "xbox",
    "fortnite",
    "valorant",
]

NON_FEATURED_RANK = len(FEATURED_SLUGS) + 1


def _generate_unique_slug(Category, name, current_id=None):
    base_slug = slugify(name) or "category"
    candidate = base_slug
    suffix = 2

    existing = Category.objects.filter(slug=candidate)
    if current_id is not None:
        existing = existing.exclude(pk=current_id)

    while existing.exists():
        candidate = f"{base_slug}-{suffix}"
        suffix += 1
        existing = Category.objects.filter(slug=candidate)
        if current_id is not None:
            existing = existing.exclude(pk=current_id)

    return candidate


def _backfill_existing_slugs(Category):
    for category in Category.objects.order_by("id"):
        if category.slug:
            continue
        category.slug = _generate_unique_slug(Category, category.name, category.id)
        category.save(update_fields=["slug"])


def _upsert_category(Category, *, name, slug, parent=None, is_featured=False, featured_rank=0):
    category = Category.objects.filter(slug=slug).first()
    if category is None:
        category = Category.objects.filter(name=name).first()

    if category is None:
        category = Category.objects.create(
            name=name,
            slug=slug,
            parent=parent,
            is_featured_home=is_featured,
            featured_rank=featured_rank,
        )
        return category

    updates = []
    if category.name != name:
        category.name = name
        updates.append("name")
    if category.slug != slug:
        category.slug = slug
        updates.append("slug")
    if category.parent_id != getattr(parent, "id", None):
        category.parent = parent
        updates.append("parent")
    if category.is_featured_home != is_featured:
        category.is_featured_home = is_featured
        updates.append("is_featured_home")
    if category.featured_rank != featured_rank:
        category.featured_rank = featured_rank
        updates.append("featured_rank")

    if updates:
        category.save(update_fields=updates)

    return category


def seed_hierarchical_categories(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    _backfill_existing_slugs(Category)

    featured_ranks = {slug: index for index, slug in enumerate(FEATURED_SLUGS, start=0)}
    top_by_slug = {}

    for name, slug in TOP_CATEGORIES:
        top_by_slug[slug] = _upsert_category(
            Category,
            name=name,
            slug=slug,
            parent=None,
            is_featured=slug in featured_ranks,
            featured_rank=featured_ranks.get(slug, NON_FEATURED_RANK),
        )

    for name, slug, parent_slug in CHILD_CATEGORIES:
        _upsert_category(
            Category,
            name=name,
            slug=slug,
            parent=top_by_slug[parent_slug],
            is_featured=slug in featured_ranks,
            featured_rank=featured_ranks.get(slug, NON_FEATURED_RANK),
        )

    Category.objects.exclude(slug__in=FEATURED_SLUGS).filter(
        is_featured_home=True
    ).update(is_featured_home=False, featured_rank=NON_FEATURED_RANK)


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0011_category_hierarchy_fields"),
    ]

    operations = [
        migrations.RunPython(
            seed_hierarchical_categories,
            migrations.RunPython.noop,
        ),
    ]
