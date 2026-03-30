from django.contrib import admin

from .models import Category, Game, OfferType, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("-id",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "category", "seller", "stock")
    search_fields = ("title",)
    list_filter = ("category",)
    ordering = ("-id",)
    list_select_related = ("category", "seller")

    @admin.display(ordering="title", description="Name")
    def name(self, obj):
        return obj.title


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "is_active", "created_at")
    search_fields = ("name", "slug", "display_name_vi")
    list_filter = ("is_active",)
    ordering = ("name",)


@admin.register(OfferType)
class OfferTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "is_active", "created_at")
    search_fields = ("name", "slug", "display_name_vi")
    list_filter = ("is_active",)
    ordering = ("name",)
