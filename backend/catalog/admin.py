from django.contrib import admin

from .models import Category, OfferType, Platform, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "parent", "is_featured_home", "featured_rank")
    search_fields = ("name", "slug")
    list_filter = ("is_featured_home",)
    ordering = ("featured_rank", "name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "category", "platform", "offer_type", "seller", "stock")
    search_fields = ("title",)
    list_filter = ("category", "platform", "offer_type")
    ordering = ("-id",)
    list_select_related = ("category", "platform", "offer_type", "seller")

    @admin.display(ordering="title", description="Name")
    def name(self, obj):
        return obj.title


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "category", "is_active", "created_at")
    search_fields = ("name", "slug", "display_name_vi", "category__name")
    list_filter = ("category", "is_active")
    ordering = ("name",)
    list_select_related = ("category",)


@admin.register(OfferType)
class OfferTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "platform", "is_active", "created_at")
    search_fields = ("name", "slug", "display_name_vi", "platform__name")
    list_filter = ("platform__category", "platform", "is_active")
    ordering = ("name",)
    list_select_related = ("platform", "platform__category")
